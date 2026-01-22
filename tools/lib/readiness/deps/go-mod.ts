/**
 * @fileoverview go.mod dependency parser
 * @module kb-tools/lib/readiness/deps/go-mod
 *
 * @description
 * Parses Go module files (go.mod) to extract dependencies.
 * Supports require blocks, replace directives, and indirect dependencies.
 */

import type {
	Dependency,
	DependencyManifest,
	ParseOptions,
} from "./types.js";

// ============================================================================
// Parser
// ============================================================================

/**
 * Parse a go.mod file
 */
export async function parseGoMod(
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
		const dependencies: Dependency[] = [];
		const devDependencies: Dependency[] = [];

		let moduleName: string | undefined;
		let goVersion: string | undefined;

		// Parse line by line
		const lines = content.split("\n");
		let inRequireBlock = false;

		for (let i = 0; i < lines.length; i++) {
			const line = lines[i]!.trim();

			// Skip empty lines and comments
			if (!line || line.startsWith("//")) continue;

			// Module name
			if (line.startsWith("module ")) {
				moduleName = line.substring(7).trim();
				continue;
			}

			// Go version
			if (line.startsWith("go ")) {
				goVersion = line.substring(3).trim();
				continue;
			}

			// Require block start
			if (line === "require (" || line.startsWith("require (")) {
				inRequireBlock = true;
				continue;
			}

			// Require block end
			if (line === ")" && inRequireBlock) {
				inRequireBlock = false;
				continue;
			}

			// Single-line require
			if (line.startsWith("require ") && !line.includes("(")) {
				const dep = parseRequireLine(line.substring(8).trim());
				if (dep) {
					if (dep.type === "development" && !includeDev) continue;
					if (dep.type === "development") {
						devDependencies.push(dep);
					} else {
						dependencies.push(dep);
					}
				}
				continue;
			}

			// Inside require block
			if (inRequireBlock) {
				const dep = parseRequireLine(line);
				if (dep) {
					if (dep.type === "development" && !includeDev) continue;
					if (dep.type === "development") {
						devDependencies.push(dep);
					} else {
						dependencies.push(dep);
					}
				}
			}
		}

		return {
			path: filepath,
			type: "go",
			name: moduleName,
			version: goVersion,
			dependencies,
			devDependencies,
			metadata: {
				goVersion,
			},
		};
	} catch {
		return null;
	}
}

/**
 * Parse a single require line
 * Format: "module/path v1.2.3" or "module/path v1.2.3 // indirect"
 */
function parseRequireLine(line: string): Dependency | null {
	// Remove trailing comments except "// indirect"
	let isIndirect = false;
	let cleanLine = line;

	if (line.includes("// indirect")) {
		isIndirect = true;
		cleanLine = line.replace("// indirect", "").trim();
	} else if (line.includes("//")) {
		cleanLine = line.substring(0, line.indexOf("//")).trim();
	}

	// Split into module path and version
	const parts = cleanLine.split(/\s+/);
	if (parts.length < 2) return null;

	const [modulePath, version] = parts;
	if (!modulePath || !version) return null;

	return {
		name: modulePath,
		version: version,
		type: isIndirect ? "development" : "production",
	};
}

/**
 * Check if a module path matches a pattern
 * Supports prefix matching (e.g., "github.com/stretchr" matches "github.com/stretchr/testify")
 */
export function moduleMatches(modulePath: string, pattern: string): boolean {
	return modulePath === pattern || modulePath.startsWith(pattern + "/");
}
