/**
 * @fileoverview pyproject.toml dependency parser
 * @module kb-tools/lib/readiness/deps/pyproject
 *
 * @description
 * Parses Python pyproject.toml files (PEP 517/518/621) and Poetry format.
 * Also supports requirements.txt as fallback.
 */

import path from "node:path";
import type {
	Dependency,
	DependencyManifest,
	ManifestType,
	ParseOptions,
} from "./types.js";

// ============================================================================
// Types
// ============================================================================

interface PyProject {
	project?: {
		name?: string;
		version?: string;
		dependencies?: string[];
		"optional-dependencies"?: Record<string, string[]>;
	};
	tool?: {
		poetry?: {
			name?: string;
			version?: string;
			dependencies?: Record<string, string | PoetryDep>;
			"dev-dependencies"?: Record<string, string | PoetryDep>;
			group?: Record<string, { dependencies?: Record<string, string | PoetryDep> }>;
		};
		uv?: {
			"dev-dependencies"?: string[];
		};
	};
	"build-system"?: {
		requires?: string[];
		"build-backend"?: string;
	};
}

interface PoetryDep {
	version?: string;
	optional?: boolean;
	extras?: string[];
	python?: string;
	git?: string;
	path?: string;
}

// ============================================================================
// Parser
// ============================================================================

/**
 * Parse a pyproject.toml file
 */
export async function parsePyProject(
	filepath: string,
	options: ParseOptions = {}
): Promise<DependencyManifest | null> {
	const { includeDev = true } = options;

	try {
		const file = Bun.file(filepath);
		if (!(await file.exists())) {
			return null;
		}

		const content = await file.text();
		const pyproject = parseToml(content);
		if (!pyproject) return null;

		const dependencies: Dependency[] = [];
		const devDependencies: Dependency[] = [];
		let manifestType: ManifestType = "python-pyproject";
		let name: string | undefined;
		let version: string | undefined;

		// PEP 621 format (project table)
		if (pyproject.project) {
			name = pyproject.project.name;
			version = pyproject.project.version;

			// Parse dependencies
			if (pyproject.project.dependencies) {
				for (const dep of pyproject.project.dependencies) {
					const parsed = parsePep508(dep);
					if (parsed) {
						dependencies.push(parsed);
					}
				}
			}

			// Parse optional dependencies (often used for dev)
			if (includeDev && pyproject.project["optional-dependencies"]) {
				for (const [group, deps] of Object.entries(
					pyproject.project["optional-dependencies"]
				)) {
					const isDev = ["dev", "test", "testing", "development"].includes(
						group.toLowerCase()
					);
					for (const dep of deps) {
						const parsed = parsePep508(dep);
						if (parsed) {
							parsed.type = isDev ? "development" : "optional";
							if (isDev) {
								devDependencies.push(parsed);
							} else {
								dependencies.push(parsed);
							}
						}
					}
				}
			}
		}

		// Poetry format
		if (pyproject.tool?.poetry) {
			manifestType = "python-poetry";
			const poetry = pyproject.tool.poetry;
			name = poetry.name ?? name;
			version = poetry.version ?? version;

			// Parse Poetry dependencies
			if (poetry.dependencies) {
				for (const [depName, depSpec] of Object.entries(poetry.dependencies)) {
					if (depName === "python") continue; // Skip Python version constraint
					const dep = parsePoetryDep(depName, depSpec);
					if (dep) {
						dependencies.push(dep);
					}
				}
			}

			// Parse Poetry dev dependencies
			if (includeDev && poetry["dev-dependencies"]) {
				for (const [depName, depSpec] of Object.entries(
					poetry["dev-dependencies"]
				)) {
					const dep = parsePoetryDep(depName, depSpec);
					if (dep) {
						dep.type = "development";
						devDependencies.push(dep);
					}
				}
			}

			// Parse Poetry groups (e.g., [tool.poetry.group.dev.dependencies])
			if (includeDev && poetry.group) {
				for (const [groupName, group] of Object.entries(poetry.group)) {
					const isDev = ["dev", "test", "testing", "development"].includes(
						groupName.toLowerCase()
					);
					if (group.dependencies) {
						for (const [depName, depSpec] of Object.entries(group.dependencies)) {
							const dep = parsePoetryDep(depName, depSpec);
							if (dep) {
								dep.type = isDev ? "development" : "optional";
								if (isDev) {
									devDependencies.push(dep);
								} else {
									dependencies.push(dep);
								}
							}
						}
					}
				}
			}
		}

		// UV format dev dependencies
		if (includeDev && pyproject.tool?.uv?.["dev-dependencies"]) {
			for (const dep of pyproject.tool.uv["dev-dependencies"]) {
				const parsed = parsePep508(dep);
				if (parsed) {
					parsed.type = "development";
					devDependencies.push(parsed);
				}
			}
		}

		return {
			path: filepath,
			type: manifestType,
			name,
			version,
			dependencies,
			devDependencies,
			metadata: {
				buildBackend: pyproject["build-system"]?.["build-backend"],
			},
		};
	} catch {
		return null;
	}
}

/**
 * Parse a requirements.txt file
 */
export async function parseRequirementsTxt(
	filepath: string,
	options: ParseOptions = {}
): Promise<DependencyManifest | null> {
	try {
		const file = Bun.file(filepath);
		if (!(await file.exists())) {
			return null;
		}

		const content = await file.text();
		const dependencies: Dependency[] = [];

		for (const line of content.split("\n")) {
			const trimmed = line.trim();

			// Skip empty lines and comments
			if (!trimmed || trimmed.startsWith("#")) continue;

			// Skip options like -r, -e, --index-url
			if (trimmed.startsWith("-")) continue;

			const dep = parsePep508(trimmed);
			if (dep) {
				dependencies.push(dep);
			}
		}

		return {
			path: filepath,
			type: "python-requirements",
			dependencies,
			devDependencies: [],
		};
	} catch {
		return null;
	}
}

// ============================================================================
// Helpers
// ============================================================================

/**
 * Parse a PEP 508 dependency specification
 * Examples: "requests>=2.28.0", "numpy[all]>=1.24", "mypy ; extra == 'dev'"
 */
function parsePep508(spec: string): Dependency | null {
	// Remove extras and environment markers for basic parsing
	let name = spec;
	let version = "*";

	// Remove environment markers
	const markerIndex = spec.indexOf(";");
	if (markerIndex !== -1) {
		name = spec.substring(0, markerIndex).trim();
	}

	// Remove extras
	const extrasMatch = name.match(/^([a-zA-Z0-9_-]+)\[/);
	if (extrasMatch) {
		name = extrasMatch[1]!;
		const bracketEnd = spec.indexOf("]");
		if (bracketEnd !== -1) {
			const afterBracket = spec.substring(bracketEnd + 1).trim();
			// Extract version from after extras
			const versionMatch = afterBracket.match(/^([><=!~]+[\d.]+)/);
			if (versionMatch?.[1]) {
				version = versionMatch[1];
			}
		}
	} else {
		// Parse version constraint
		const versionMatch = name.match(/^([a-zA-Z0-9_-]+)([><=!~].+)$/);
		if (versionMatch) {
			name = versionMatch[1]!;
			version = versionMatch[2]!;
		} else {
			// No version, just package name
			name = name.replace(/[><=!~].*$/, "").trim();
		}
	}

	if (!name) return null;

	return {
		name: name.toLowerCase().replace(/_/g, "-"),
		version,
		type: "production",
	};
}

/**
 * Parse a Poetry dependency specification
 */
function parsePoetryDep(
	name: string,
	spec: string | PoetryDep
): Dependency | null {
	if (typeof spec === "string") {
		return {
			name: name.toLowerCase().replace(/_/g, "-"),
			version: spec,
			type: "production",
		};
	}

	return {
		name: name.toLowerCase().replace(/_/g, "-"),
		version: spec.version ?? "*",
		type: "production",
		optional: spec.optional,
	};
}

/**
 * Simple TOML parser for pyproject.toml
 * Handles the common cases without external dependencies
 */
function parseToml(content: string): PyProject | null {
	try {
		const result: Record<string, unknown> = {};
		const lines = content.split("\n");
		let currentSection: string[] = [];
		let currentObject: Record<string, unknown> = result;
		let inMultilineArray = false;
		let multilineArrayContent = "";
		let multilineArrayKey = "";

		for (let i = 0; i < lines.length; i++) {
			let line = lines[i]!;

			// Handle multiline arrays
			if (inMultilineArray) {
				multilineArrayContent += line;
				if (line.includes("]")) {
					inMultilineArray = false;
					// Parse the complete array
					const arrayContent = multilineArrayContent
						.replace(/^\[/, "")
						.replace(/\]$/, "")
						.trim();
					const items = arrayContent
						.split(",")
						.map((s) => s.trim())
						.filter(Boolean)
						.map((s) => s.replace(/^["']|["']$/g, ""));

					setNestedValue(currentObject, multilineArrayKey, items);
					multilineArrayContent = "";
					multilineArrayKey = "";
				}
				continue;
			}

			line = line.trim();

			// Skip empty lines and comments
			if (!line || line.startsWith("#")) continue;

			// Section header
			if (line.startsWith("[")) {
				const sectionMatch = line.match(/^\[+([^\]]+)\]+$/);
				if (sectionMatch) {
					currentSection = sectionMatch[1]!.split(".").map((s) => s.trim());
					currentObject = ensurePath(result, currentSection);
				}
				continue;
			}

			// Key-value pair
			const kvMatch = line.match(/^([^=]+)=(.*)$/);
			if (kvMatch) {
				const key = kvMatch[1]!.trim();
				let value = kvMatch[2]!.trim();

				// Start of multiline array
				if (value.startsWith("[") && !value.includes("]")) {
					inMultilineArray = true;
					multilineArrayContent = value;
					multilineArrayKey = key;
					continue;
				}

				// Parse value
				const parsedValue = parseTomlValue(value);
				setNestedValue(currentObject, key, parsedValue);
			}
		}

		return result as PyProject;
	} catch {
		return null;
	}
}

function parseTomlValue(value: string): unknown {
	// String
	if (
		(value.startsWith('"') && value.endsWith('"')) ||
		(value.startsWith("'") && value.endsWith("'"))
	) {
		return value.slice(1, -1);
	}

	// Boolean
	if (value === "true") return true;
	if (value === "false") return false;

	// Array
	if (value.startsWith("[") && value.endsWith("]")) {
		const arrayContent = value.slice(1, -1).trim();
		if (!arrayContent) return [];

		// Split by comma, handling quoted strings
		const items: string[] = [];
		let current = "";
		let inQuotes = false;
		let quoteChar = "";

		for (const char of arrayContent) {
			if ((char === '"' || char === "'") && !inQuotes) {
				inQuotes = true;
				quoteChar = char;
			} else if (char === quoteChar && inQuotes) {
				inQuotes = false;
			} else if (char === "," && !inQuotes) {
				items.push(current.trim());
				current = "";
				continue;
			}
			current += char;
		}
		if (current.trim()) {
			items.push(current.trim());
		}

		return items.map(parseTomlValue);
	}

	// Inline table
	if (value.startsWith("{") && value.endsWith("}")) {
		const tableContent = value.slice(1, -1).trim();
		const result: Record<string, unknown> = {};
		// Simple inline table parsing
		const pairs = tableContent.split(",");
		for (const pair of pairs) {
			const kv = pair.split("=");
			if (kv.length === 2) {
				const k = kv[0]!.trim();
				const v = parseTomlValue(kv[1]!.trim());
				result[k] = v;
			}
		}
		return result;
	}

	// Number
	if (/^-?\d+(\.\d+)?$/.test(value)) {
		return Number(value);
	}

	// Return as string
	return value;
}

function ensurePath(
	obj: Record<string, unknown>,
	path: string[]
): Record<string, unknown> {
	let current = obj;
	for (const key of path) {
		if (!(key in current)) {
			current[key] = {};
		}
		current = current[key] as Record<string, unknown>;
	}
	return current;
}

function setNestedValue(
	obj: Record<string, unknown>,
	key: string,
	value: unknown
): void {
	const parts = key.split(".");
	let current = obj;

	for (let i = 0; i < parts.length - 1; i++) {
		const part = parts[i]!;
		if (!(part in current)) {
			current[part] = {};
		}
		current = current[part] as Record<string, unknown>;
	}

	current[parts[parts.length - 1]!] = value;
}
