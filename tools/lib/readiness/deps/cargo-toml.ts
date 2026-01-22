/**
 * @fileoverview Cargo.toml dependency parser
 * @module kb-tools/lib/readiness/deps/cargo-toml
 *
 * @description
 * Parses Rust Cargo.toml files to extract dependencies.
 * Supports regular, dev, and build dependencies.
 */

import type {
	Dependency,
	DependencyManifest,
	ParseOptions,
} from "./types.js";

// ============================================================================
// Types
// ============================================================================

interface CargoToml {
	package?: {
		name?: string;
		version?: string;
	};
	dependencies?: Record<string, string | CargoDep>;
	"dev-dependencies"?: Record<string, string | CargoDep>;
	"build-dependencies"?: Record<string, string | CargoDep>;
	workspace?: {
		members?: string[];
		dependencies?: Record<string, string | CargoDep>;
	};
	features?: Record<string, string[]>;
}

interface CargoDep {
	version?: string;
	optional?: boolean;
	features?: string[];
	git?: string;
	branch?: string;
	path?: string;
	workspace?: boolean;
}

// ============================================================================
// Parser
// ============================================================================

/**
 * Parse a Cargo.toml file
 */
export async function parseCargoToml(
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
		const cargo = parseToml(content);
		if (!cargo) return null;

		const dependencies: Dependency[] = [];
		const devDependencies: Dependency[] = [];

		// Parse regular dependencies
		if (cargo.dependencies) {
			for (const [name, spec] of Object.entries(cargo.dependencies)) {
				const dep = parseCargoDep(name, spec);
				if (dep) {
					dependencies.push(dep);
				}
			}
		}

		// Parse dev dependencies
		if (includeDev && cargo["dev-dependencies"]) {
			for (const [name, spec] of Object.entries(cargo["dev-dependencies"])) {
				const dep = parseCargoDep(name, spec);
				if (dep) {
					dep.type = "development";
					devDependencies.push(dep);
				}
			}
		}

		// Parse build dependencies
		if (cargo["build-dependencies"]) {
			for (const [name, spec] of Object.entries(cargo["build-dependencies"])) {
				const dep = parseCargoDep(name, spec);
				if (dep) {
					dep.type = "build";
					dependencies.push(dep);
				}
			}
		}

		return {
			path: filepath,
			type: "rust",
			name: cargo.package?.name,
			version: cargo.package?.version,
			dependencies,
			devDependencies,
			metadata: {
				isWorkspace: Boolean(cargo.workspace),
				features: cargo.features ? Object.keys(cargo.features) : [],
			},
		};
	} catch {
		return null;
	}
}

/**
 * Parse a single Cargo dependency
 */
function parseCargoDep(name: string, spec: string | CargoDep): Dependency | null {
	if (typeof spec === "string") {
		return {
			name,
			version: spec,
			type: "production",
		};
	}

	// Handle workspace dependency
	if (spec.workspace) {
		return {
			name,
			version: "workspace",
			type: "production",
		};
	}

	// Handle git dependency
	if (spec.git) {
		return {
			name,
			version: spec.branch || spec.git,
			type: "production",
		};
	}

	// Handle path dependency
	if (spec.path && !spec.version) {
		return {
			name,
			version: `path:${spec.path}`,
			type: "production",
		};
	}

	return {
		name,
		version: spec.version || "*",
		type: "production",
		optional: spec.optional,
	};
}

// ============================================================================
// TOML Parser (Simplified for Cargo.toml)
// ============================================================================

function parseToml(content: string): CargoToml | null {
	try {
		const result: Record<string, unknown> = {};
		const lines = content.split("\n");
		let currentSection: string[] = [];
		let currentObject: Record<string, unknown> = result;
		let inMultilineValue = false;
		let multilineKey = "";
		let multilineValue = "";

		for (let i = 0; i < lines.length; i++) {
			let line = lines[i]!;

			// Handle multiline strings/arrays
			if (inMultilineValue) {
				multilineValue += "\n" + line;
				if (
					(multilineValue.startsWith("[") && line.trim().endsWith("]")) ||
					(multilineValue.startsWith("{") && line.trim().endsWith("}")) ||
					line.includes('"""') ||
					line.includes("'''")
				) {
					inMultilineValue = false;
					const parsed = parseTomlValue(multilineValue.trim());
					setNestedValue(currentObject, multilineKey, parsed);
					multilineValue = "";
					multilineKey = "";
				}
				continue;
			}

			line = line.trim();

			// Skip empty lines and comments
			if (!line || line.startsWith("#")) continue;

			// Array of tables: [[section]]
			if (line.startsWith("[[") && line.endsWith("]]")) {
				const section = line.slice(2, -2).trim();
				currentSection = section.split(".").map((s) => s.trim());
				// For arrays of tables, we need to append to an array
				currentObject = ensureArrayPath(result, currentSection);
				continue;
			}

			// Section header: [section]
			if (line.startsWith("[") && line.endsWith("]")) {
				const section = line.slice(1, -1).trim();
				currentSection = section.split(".").map((s) => s.trim());
				currentObject = ensurePath(result, currentSection);
				continue;
			}

			// Key-value pair
			const kvMatch = line.match(/^([^=]+)=(.*)$/);
			if (kvMatch) {
				const key = kvMatch[1]!.trim();
				const value = kvMatch[2]!.trim();

				// Check for multiline values
				if (
					(value.startsWith("[") && !value.includes("]")) ||
					(value.startsWith("{") && !value.includes("}")) ||
					value === '"""' ||
					value === "'''"
				) {
					inMultilineValue = true;
					multilineKey = key;
					multilineValue = value;
					continue;
				}

				const parsedValue = parseTomlValue(value);
				setNestedValue(currentObject, key, parsedValue);
			}
		}

		return result as CargoToml;
	} catch {
		return null;
	}
}

function parseTomlValue(value: string): unknown {
	// Triple-quoted string
	if (value.startsWith('"""') && value.endsWith('"""')) {
		return value.slice(3, -3);
	}
	if (value.startsWith("'''") && value.endsWith("'''")) {
		return value.slice(3, -3);
	}

	// Regular string
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

		// Split by comma, handling quoted strings and nested structures
		const items: string[] = [];
		let current = "";
		let depth = 0;
		let inQuotes = false;
		let quoteChar = "";

		for (const char of arrayContent) {
			if ((char === '"' || char === "'") && !inQuotes) {
				inQuotes = true;
				quoteChar = char;
				current += char;
			} else if (char === quoteChar && inQuotes) {
				inQuotes = false;
				current += char;
			} else if ((char === "[" || char === "{") && !inQuotes) {
				depth++;
				current += char;
			} else if ((char === "]" || char === "}") && !inQuotes) {
				depth--;
				current += char;
			} else if (char === "," && !inQuotes && depth === 0) {
				items.push(current.trim());
				current = "";
			} else {
				current += char;
			}
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

		// Parse inline table with proper quote handling
		let current = "";
		let inQuotes = false;
		let quoteChar = "";
		const pairs: string[] = [];

		for (const char of tableContent) {
			if ((char === '"' || char === "'") && !inQuotes) {
				inQuotes = true;
				quoteChar = char;
				current += char;
			} else if (char === quoteChar && inQuotes) {
				inQuotes = false;
				current += char;
			} else if (char === "," && !inQuotes) {
				pairs.push(current.trim());
				current = "";
			} else {
				current += char;
			}
		}
		if (current.trim()) {
			pairs.push(current.trim());
		}

		for (const pair of pairs) {
			const eqIdx = pair.indexOf("=");
			if (eqIdx !== -1) {
				const k = pair.substring(0, eqIdx).trim();
				const v = parseTomlValue(pair.substring(eqIdx + 1).trim());
				result[k] = v;
			}
		}
		return result;
	}

	// Number
	if (/^-?\d+(\.\d+)?$/.test(value)) {
		return Number(value);
	}

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

function ensureArrayPath(
	obj: Record<string, unknown>,
	path: string[]
): Record<string, unknown> {
	let current = obj;
	for (let i = 0; i < path.length - 1; i++) {
		const key = path[i]!;
		if (!(key in current)) {
			current[key] = {};
		}
		current = current[key] as Record<string, unknown>;
	}

	const lastKey = path[path.length - 1]!;
	if (!(lastKey in current)) {
		current[lastKey] = [];
	}
	const arr = current[lastKey] as unknown[];
	const newObj: Record<string, unknown> = {};
	arr.push(newObj);
	return newObj;
}

function setNestedValue(
	obj: Record<string, unknown>,
	key: string,
	value: unknown
): void {
	// Handle dotted keys
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
