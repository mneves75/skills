/**
 * @fileoverview package.json dependency parser
 * @module kb-tools/lib/readiness/deps/package-json
 *
 * @description
 * Parses npm/bun/pnpm/yarn package.json files to extract dependencies,
 * scripts, and metadata.
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

interface PackageJson {
	name?: string;
	version?: string;
	scripts?: Record<string, string>;
	dependencies?: Record<string, string>;
	devDependencies?: Record<string, string>;
	peerDependencies?: Record<string, string>;
	optionalDependencies?: Record<string, string>;
	workspaces?: string[] | { packages: string[] };
	packageManager?: string;
	engines?: Record<string, string>;
}

// ============================================================================
// Parser
// ============================================================================

/**
 * Parse a package.json file
 */
export async function parsePackageJson(
	filepath: string,
	options: ParseOptions = {}
): Promise<DependencyManifest | null> {
	const { includeDev = true } = options;

	try {
		const file = Bun.file(filepath);
		if (!(await file.exists())) {
			return null;
		}

		const pkg: PackageJson = await file.json();
		const manifestType = detectPackageManager(filepath, pkg);

		const dependencies: Dependency[] = [];
		const devDependencies: Dependency[] = [];

		// Parse production dependencies
		if (pkg.dependencies) {
			for (const [name, version] of Object.entries(pkg.dependencies)) {
				dependencies.push({
					name,
					version,
					type: "production",
				});
			}
		}

		// Parse peer dependencies as production
		if (pkg.peerDependencies) {
			for (const [name, version] of Object.entries(pkg.peerDependencies)) {
				dependencies.push({
					name,
					version,
					type: "peer",
				});
			}
		}

		// Parse optional dependencies
		if (pkg.optionalDependencies) {
			for (const [name, version] of Object.entries(pkg.optionalDependencies)) {
				dependencies.push({
					name,
					version,
					type: "optional",
					optional: true,
				});
			}
		}

		// Parse dev dependencies
		if (includeDev && pkg.devDependencies) {
			for (const [name, version] of Object.entries(pkg.devDependencies)) {
				devDependencies.push({
					name,
					version,
					type: "development",
				});
			}
		}

		return {
			path: filepath,
			type: manifestType,
			name: pkg.name,
			version: pkg.version,
			dependencies,
			devDependencies,
			scripts: pkg.scripts,
			metadata: {
				packageManager: pkg.packageManager,
				engines: pkg.engines,
				hasWorkspaces: Boolean(pkg.workspaces),
			},
		};
	} catch {
		return null;
	}
}

/**
 * Detect the package manager being used
 */
function detectPackageManager(
	filepath: string,
	pkg: PackageJson
): ManifestType {
	const dir = path.dirname(filepath);

	// Check packageManager field first (modern approach)
	if (pkg.packageManager) {
		if (pkg.packageManager.startsWith("bun")) return "bun";
		if (pkg.packageManager.startsWith("pnpm")) return "pnpm";
		if (pkg.packageManager.startsWith("yarn")) return "yarn";
		return "npm";
	}

	// Check for lockfiles
	try {
		const fs = require("node:fs");
		if (fs.existsSync(path.join(dir, "bun.lockb")) ||
			fs.existsSync(path.join(dir, "bun.lock"))) {
			return "bun";
		}
		if (fs.existsSync(path.join(dir, "pnpm-lock.yaml"))) {
			return "pnpm";
		}
		if (fs.existsSync(path.join(dir, "yarn.lock"))) {
			return "yarn";
		}
	} catch {
		// Ignore filesystem errors
	}

	return "npm";
}

/**
 * Check if a package has a specific script
 */
export function hasScript(
	manifest: DependencyManifest,
	scriptName: string
): boolean {
	return Boolean(manifest.scripts?.[scriptName]);
}

/**
 * Get all script names from a manifest
 */
export function getScriptNames(manifest: DependencyManifest): string[] {
	return Object.keys(manifest.scripts ?? {});
}
