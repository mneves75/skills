/**
 * @fileoverview Application discovery for monorepos
 * @module kb-tools/lib/app-discovery
 *
 * @description
 * Discovers application boundaries in a repository. Critical for monorepo
 * support where each app may have different tooling and maturity levels.
 *
 * An "app" is defined as a deployable unit with:
 * - Its own dependency manifest (package.json, go.mod, Cargo.toml, etc.)
 * - Its own build/entry point
 *
 * A "library" is a shared package that's not independently deployed.
 */

import fs from "node:fs";
import path from "node:path";
import type { Language } from "./language-detection.js";
import { detectLanguageQuick } from "./language-detection.js";

// ============================================================================
// Types
// ============================================================================

/**
 * Type of detected application
 */
export type AppType = "app" | "library" | "workspace-root";

/**
 * Dependency manifest types we recognize
 */
export type ManifestType =
	| "package.json"
	| "go.mod"
	| "Cargo.toml"
	| "pyproject.toml"
	| "pom.xml"
	| "build.gradle"
	| "Gemfile"
	| "composer.json";

/**
 * A discovered application within a repository
 */
export interface DetectedApp {
	/** Unique identifier (relative path from repo root) */
	id: string;
	/** Display name (directory name or from manifest) */
	name: string;
	/** Absolute path to app root */
	path: string;
	/** Relative path from repo root */
	relativePath: string;
	/** Type of app (app, library, or workspace-root) */
	type: AppType;
	/** Primary language detected */
	language: Language;
	/** Dependency manifest file used for detection */
	manifest: ManifestType;
	/** Path to the manifest file */
	manifestPath: string;
	/** Whether this is the repository root */
	isRoot: boolean;
	/** Parent app ID for nested apps (rare) */
	parentId?: string;
}

/**
 * Complete discovery result
 */
export interface DiscoveryResult {
	/** Repository root path */
	repoRoot: string;
	/** Whether this is a monorepo */
	isMonorepo: boolean;
	/** All discovered apps */
	apps: DetectedApp[];
	/** Workspace configuration if present */
	workspaceConfig?: WorkspaceConfig;
}

/**
 * Workspace configuration (npm/pnpm/yarn workspaces, Go workspaces, etc.)
 */
export interface WorkspaceConfig {
	/** Workspace manager type */
	type: "npm" | "pnpm" | "yarn" | "bun" | "go" | "cargo" | "turborepo" | "nx";
	/** Workspace patterns (globs) */
	patterns: string[];
	/** Path to config file */
	configPath: string;
}

// ============================================================================
// Configuration
// ============================================================================

/**
 * Manifest files to language mapping
 */
const MANIFEST_TO_LANGUAGE: Record<ManifestType, Language> = {
	"package.json": "typescript", // Default, will be refined
	"go.mod": "go",
	"Cargo.toml": "rust",
	"pyproject.toml": "python",
	"pom.xml": "java",
	"build.gradle": "java",
	Gemfile: "ruby",
	"composer.json": "php",
};

/**
 * Directories that indicate an "apps" location
 */
const APP_DIRECTORIES = new Set([
	"apps",
	"services",
	"packages",
	"modules",
	"projects",
	"cmd", // Go convention
	"internal", // Go convention
	"crates", // Rust convention
	"members", // Rust convention
]);

/**
 * Directories to skip during discovery
 */
const SKIP_DIRECTORIES = new Set([
	"node_modules",
	".git",
	".svn",
	"vendor",
	"target",
	"build",
	"dist",
	"out",
	".next",
	".nuxt",
	"__pycache__",
	".pytest_cache",
	".mypy_cache",
	"venv",
	".venv",
	"env",
	".tox",
	"coverage",
	".coverage",
	"htmlcov",
	".gradle",
	".idea",
	".vscode",
	"Pods",
	"DerivedData",
	"testdata",
	"fixtures",
	"examples",
]);

// ============================================================================
// Utility Functions
// ============================================================================

async function fileExists(filepath: string): Promise<boolean> {
	try {
		return await Bun.file(filepath).exists();
	} catch {
		return false;
	}
}

async function readJsonSafe<T>(filepath: string): Promise<T | null> {
	try {
		const file = Bun.file(filepath);
		if (!(await file.exists())) return null;
		return await file.json();
	} catch {
		return null;
	}
}

async function readTextSafe(filepath: string): Promise<string | null> {
	try {
		const file = Bun.file(filepath);
		if (!(await file.exists())) return null;
		return await file.text();
	} catch {
		return null;
	}
}

// ============================================================================
// Workspace Detection
// ============================================================================

/**
 * Detect workspace configuration in a repository
 */
async function detectWorkspaceConfig(
	repoRoot: string,
): Promise<WorkspaceConfig | undefined> {
	// Check for pnpm-workspace.yaml
	const pnpmWorkspacePath = path.join(repoRoot, "pnpm-workspace.yaml");
	if (await fileExists(pnpmWorkspacePath)) {
		const content = await readTextSafe(pnpmWorkspacePath);
		if (content) {
			// Parse YAML (simple extraction of packages patterns)
			const patterns: string[] = [];
			const lines = content.split("\n");
			let inPackages = false;
			for (const line of lines) {
				if (line.trim().startsWith("packages:")) {
					inPackages = true;
					continue;
				}
				if (inPackages && line.trim().startsWith("-")) {
					const pattern = line.replace(/^\s*-\s*['"]?/, "").replace(/['"]?\s*$/, "");
					if (pattern) patterns.push(pattern);
				} else if (inPackages && !line.match(/^\s/)) {
					inPackages = false;
				}
			}
			return {
				type: "pnpm",
				patterns,
				configPath: pnpmWorkspacePath,
			};
		}
	}

	// Check for Turborepo
	const turboPath = path.join(repoRoot, "turbo.json");
	if (await fileExists(turboPath)) {
		// Turbo uses npm/pnpm/yarn workspaces, so look for those patterns
		const pkgPath = path.join(repoRoot, "package.json");
		const pkg = await readJsonSafe<{ workspaces?: string[] | { packages: string[] } }>(pkgPath);
		const patterns = Array.isArray(pkg?.workspaces)
			? pkg.workspaces
			: pkg?.workspaces?.packages || [];
		return {
			type: "turborepo",
			patterns,
			configPath: turboPath,
		};
	}

	// Check for Nx
	const nxPath = path.join(repoRoot, "nx.json");
	if (await fileExists(nxPath)) {
		return {
			type: "nx",
			patterns: ["apps/*", "libs/*", "packages/*"],
			configPath: nxPath,
		};
	}

	// Check for npm/yarn/bun workspaces in package.json
	const pkgPath = path.join(repoRoot, "package.json");
	const pkg = await readJsonSafe<{ workspaces?: string[] | { packages: string[] } }>(pkgPath);
	if (pkg?.workspaces) {
		const patterns = Array.isArray(pkg.workspaces)
			? pkg.workspaces
			: pkg.workspaces.packages || [];

		// Determine which package manager
		let type: WorkspaceConfig["type"] = "npm";
		if (await fileExists(path.join(repoRoot, "bun.lockb")) || await fileExists(path.join(repoRoot, "bun.lock"))) {
			type = "bun";
		} else if (await fileExists(path.join(repoRoot, "yarn.lock"))) {
			type = "yarn";
		} else if (await fileExists(path.join(repoRoot, "pnpm-lock.yaml"))) {
			type = "pnpm";
		}

		return { type, patterns, configPath: pkgPath };
	}

	// Check for Go workspace (go.work)
	const goWorkPath = path.join(repoRoot, "go.work");
	if (await fileExists(goWorkPath)) {
		const content = await readTextSafe(goWorkPath);
		if (content) {
			const patterns: string[] = [];
			const lines = content.split("\n");
			for (const line of lines) {
				const match = line.match(/^\s*use\s+(\S+)/);
				if (match?.[1]) {
					patterns.push(match[1]);
				}
			}
			return { type: "go", patterns, configPath: goWorkPath };
		}
	}

	// Check for Cargo workspace (Cargo.toml with [workspace])
	const cargoPath = path.join(repoRoot, "Cargo.toml");
	if (await fileExists(cargoPath)) {
		const content = await readTextSafe(cargoPath);
		if (content?.includes("[workspace]")) {
			const patterns: string[] = [];
			const lines = content.split("\n");
			let inMembers = false;
			for (const line of lines) {
				if (line.includes("members")) {
					inMembers = true;
					// Handle inline array: members = ["crate1", "crate2"]
					const inlineMatch = line.match(/members\s*=\s*\[(.*)\]/);
					if (inlineMatch?.[1]) {
						const members = inlineMatch[1].match(/"([^"]+)"/g);
						if (members) {
							patterns.push(...members.map((m) => m.replace(/"/g, "")));
						}
						inMembers = false;
					}
					continue;
				}
				if (inMembers) {
					if (line.includes("]")) {
						inMembers = false;
					} else {
						const match = line.match(/"([^"]+)"/);
						if (match?.[1]) patterns.push(match[1]);
					}
				}
			}
			return { type: "cargo", patterns, configPath: cargoPath };
		}
	}

	return undefined;
}

// ============================================================================
// App Type Classification
// ============================================================================

/**
 * Determine if a package.json represents an app or library
 */
async function classifyNodeApp(
	manifestPath: string,
	relativePath: string,
): Promise<AppType> {
	const pkg = await readJsonSafe<{
		name?: string;
		private?: boolean;
		scripts?: Record<string, string>;
		main?: string;
		bin?: Record<string, string> | string;
		workspaces?: unknown;
	}>(manifestPath);

	if (!pkg) return "library";

	// Workspace root
	if (pkg.workspaces) return "workspace-root";

	// Has bin or start script = likely app
	if (pkg.bin) return "app";
	if (pkg.scripts?.["start"]) return "app";
	if (pkg.scripts?.["dev"]) return "app";
	if (pkg.scripts?.["serve"]) return "app";

	// In "apps" or "services" directory = app
	if (relativePath.match(/^(apps?|services?)\//i)) return "app";

	// In "packages" or "libs" directory = library
	if (relativePath.match(/^(packages?|libs?)\//i)) return "library";

	// Private package without main = likely app
	if (pkg.private && !pkg.main) return "app";

	// Has main = library
	if (pkg.main) return "library";

	// Default to app for standalone package.json
	return relativePath === "." ? "app" : "library";
}

/**
 * Determine if a Go module represents an app or library
 */
async function classifyGoApp(
	appPath: string,
	relativePath: string,
): Promise<AppType> {
	// Check for main.go = app
	const mainPath = path.join(appPath, "main.go");
	if (await fileExists(mainPath)) return "app";

	// Check for cmd directory = app
	const cmdPath = path.join(appPath, "cmd");
	try {
		const stat = fs.statSync(cmdPath);
		if (stat.isDirectory()) return "app";
	} catch {
		// Not found
	}

	// In cmd/ directory = app
	if (relativePath.startsWith("cmd/")) return "app";

	// In internal/ or pkg/ = library
	if (relativePath.startsWith("internal/") || relativePath.startsWith("pkg/")) {
		return "library";
	}

	// Root go.mod with main.go = app
	if (relativePath === ".") {
		return "app";
	}

	return "library";
}

/**
 * Determine if a Cargo crate represents an app or library
 */
async function classifyRustApp(
	manifestPath: string,
	relativePath: string,
): Promise<AppType> {
	const content = await readTextSafe(manifestPath);
	if (!content) return "library";

	// Check for workspace
	if (content.includes("[workspace]") && !content.includes("[[bin]]")) {
		return "workspace-root";
	}

	// Has [[bin]] section = app
	if (content.includes("[[bin]]")) return "app";

	// Has [lib] section = library
	if (content.includes("[lib]")) return "library";

	// Check for main.rs vs lib.rs
	const appDir = path.dirname(manifestPath);
	if (await fileExists(path.join(appDir, "src", "main.rs"))) return "app";
	if (await fileExists(path.join(appDir, "src", "lib.rs"))) return "library";

	// In bins/ directory = app
	if (relativePath.match(/^bins?\//)) return "app";

	return "app"; // Default for standalone crate
}

/**
 * Determine if a Python project represents an app or library
 */
async function classifyPythonApp(
	manifestPath: string,
	relativePath: string,
): Promise<AppType> {
	const content = await readTextSafe(manifestPath);
	if (!content) return "library";

	// Has entry points = app
	if (content.includes("[project.scripts]") || content.includes("[tool.poetry.scripts]")) {
		return "app";
	}

	// Check for __main__.py
	const appDir = path.dirname(manifestPath);
	const projectName = path.basename(appDir);
	if (await fileExists(path.join(appDir, projectName, "__main__.py"))) return "app";
	if (await fileExists(path.join(appDir, "src", projectName, "__main__.py"))) return "app";

	// In apps/ directory = app
	if (relativePath.match(/^apps?\//i)) return "app";

	return "library";
}

// ============================================================================
// Main Discovery Logic
// ============================================================================

/**
 * Find all manifest files in a directory tree
 */
async function findManifests(
	repoRoot: string,
	maxDepth = 4,
): Promise<Array<{ path: string; type: ManifestType; relativePath: string }>> {
	const manifests: Array<{ path: string; type: ManifestType; relativePath: string }> = [];
	const manifestFiles: ManifestType[] = [
		"package.json",
		"go.mod",
		"Cargo.toml",
		"pyproject.toml",
		"pom.xml",
		"build.gradle",
		"Gemfile",
		"composer.json",
	];

	function scan(dir: string, depth: number, relPath: string): void {
		if (depth > maxDepth) return;

		let entries: fs.Dirent[];
		try {
			entries = fs.readdirSync(dir, { withFileTypes: true });
		} catch {
			return;
		}

		for (const entry of entries) {
			if (entry.isFile() && manifestFiles.includes(entry.name as ManifestType)) {
				manifests.push({
					path: path.join(dir, entry.name),
					type: entry.name as ManifestType,
					relativePath: relPath || ".",
				});
			} else if (entry.isDirectory() && !SKIP_DIRECTORIES.has(entry.name)) {
				scan(
					path.join(dir, entry.name),
					depth + 1,
					relPath ? path.join(relPath, entry.name) : entry.name,
				);
			}
		}
	}

	scan(repoRoot, 0, "");
	return manifests;
}

/**
 * Extract app name from manifest
 */
async function extractAppName(
	manifestPath: string,
	manifestType: ManifestType,
): Promise<string> {
	switch (manifestType) {
		case "package.json": {
			const pkg = await readJsonSafe<{ name?: string }>(manifestPath);
			return pkg?.name || path.basename(path.dirname(manifestPath));
		}
		case "go.mod": {
			const content = await readTextSafe(manifestPath);
			const match = content?.match(/^module\s+(\S+)/m);
			if (match?.[1]) {
				// Return last part of module path
				const parts = match[1].split("/");
				return parts[parts.length - 1] || path.basename(path.dirname(manifestPath));
			}
			return path.basename(path.dirname(manifestPath));
		}
		case "Cargo.toml": {
			const content = await readTextSafe(manifestPath);
			const match = content?.match(/^\s*name\s*=\s*"([^"]+)"/m);
			return match?.[1] || path.basename(path.dirname(manifestPath));
		}
		case "pyproject.toml": {
			const content = await readTextSafe(manifestPath);
			const match = content?.match(/^\s*name\s*=\s*"([^"]+)"/m);
			return match?.[1] || path.basename(path.dirname(manifestPath));
		}
		case "pom.xml": {
			const content = await readTextSafe(manifestPath);
			const match = content?.match(/<artifactId>([^<]+)<\/artifactId>/);
			return match?.[1] || path.basename(path.dirname(manifestPath));
		}
		default:
			return path.basename(path.dirname(manifestPath));
	}
}

/**
 * Classify an app based on its manifest
 */
async function classifyApp(
	manifestPath: string,
	manifestType: ManifestType,
	relativePath: string,
): Promise<AppType> {
	const appPath = path.dirname(manifestPath);

	switch (manifestType) {
		case "package.json":
			return classifyNodeApp(manifestPath, relativePath);
		case "go.mod":
			return classifyGoApp(appPath, relativePath);
		case "Cargo.toml":
			return classifyRustApp(manifestPath, relativePath);
		case "pyproject.toml":
			return classifyPythonApp(manifestPath, relativePath);
		case "pom.xml":
		case "build.gradle":
			// Java apps typically have a main class
			return relativePath === "." ? "app" : "library";
		default:
			return "app";
	}
}

/**
 * Refine language detection for package.json (JS vs TS)
 */
async function refineNodeLanguage(appPath: string): Promise<Language> {
	// Check for tsconfig.json
	if (await fileExists(path.join(appPath, "tsconfig.json"))) {
		return "typescript";
	}

	// Check for .ts files in src
	const srcPath = path.join(appPath, "src");
	try {
		const files = fs.readdirSync(srcPath);
		if (files.some((f) => f.endsWith(".ts") || f.endsWith(".tsx"))) {
			return "typescript";
		}
	} catch {
		// No src directory
	}

	return "javascript";
}

/**
 * Discover all applications in a repository
 *
 * @param repoPath - Repository root path (defaults to cwd)
 * @returns Complete discovery result with all apps
 */
export async function discoverApps(repoPath?: string): Promise<DiscoveryResult> {
	const repoRoot = repoPath || process.cwd();

	// Find all manifests
	const manifests = await findManifests(repoRoot);

	// Detect workspace configuration
	const workspaceConfig = await detectWorkspaceConfig(repoRoot);

	// Build app list
	const apps: DetectedApp[] = [];

	for (const manifest of manifests) {
		const appPath = path.dirname(manifest.path);
		const appType = await classifyApp(manifest.path, manifest.type, manifest.relativePath);

		// Determine language
		let language = MANIFEST_TO_LANGUAGE[manifest.type];
		if (manifest.type === "package.json") {
			language = await refineNodeLanguage(appPath);
		}

		const name = await extractAppName(manifest.path, manifest.type);

		apps.push({
			id: manifest.relativePath,
			name,
			path: appPath,
			relativePath: manifest.relativePath,
			type: appType,
			language,
			manifest: manifest.type,
			manifestPath: manifest.path,
			isRoot: manifest.relativePath === ".",
		});
	}

	// Sort: root first, then by path
	apps.sort((a, b) => {
		if (a.isRoot && !b.isRoot) return -1;
		if (!a.isRoot && b.isRoot) return 1;
		return a.relativePath.localeCompare(b.relativePath);
	});

	// Determine if monorepo
	const isMonorepo =
		apps.length > 1 ||
		workspaceConfig !== undefined ||
		apps.some((a) => a.type === "workspace-root");

	return {
		repoRoot,
		isMonorepo,
		apps,
		workspaceConfig,
	};
}

/**
 * Get only deployable apps (excluding libraries and workspace roots)
 */
export function getDeployableApps(result: DiscoveryResult): DetectedApp[] {
	return result.apps.filter((app) => app.type === "app");
}

/**
 * Get the primary app (root app or first deployable app)
 */
export function getPrimaryApp(result: DiscoveryResult): DetectedApp | undefined {
	// First check for root app
	const rootApp = result.apps.find((a) => a.isRoot && a.type === "app");
	if (rootApp) return rootApp;

	// Then first deployable app
	const deployable = getDeployableApps(result);
	return deployable[0];
}
