/**
 * @fileoverview Git repository utilities
 * @module skills-tools/repo
 */

import { execSync } from "node:child_process";
import fs from "node:fs";
import path from "node:path";
import type { Result } from "./result.js";
import { err, ok } from "./result.js";

/** Cached repository root path */
let cachedRoot: string | null = null;

const ROOT_MARKERS = ["GUIDELINES_INDEX.json", "AGENTS.md"] as const;

function hasRootMarkers(dir: string): boolean {
	return ROOT_MARKERS.every((marker) => fs.existsSync(path.join(dir, marker)));
}

/**
 * Finds the repository root directory.
 *
 * @returns The absolute path to the repository root
 *
 * @remarks
 * Result is cached after first call for performance.
 * Prefers root markers, then falls back to git root or cwd.
 *
 * @example
 * ```typescript
 * const root = findRepoRoot();
 * console.log(root); // "/Users/dev/my-project"
 * ```
 */
export function findRepoRoot(): string {
	if (cachedRoot !== null) {
		return cachedRoot;
	}

	const startDir = process.cwd();
	let dir = path.resolve(startDir);

	while (true) {
		if (hasRootMarkers(dir)) {
			cachedRoot = dir;
			return cachedRoot;
		}
		const parent = path.dirname(dir);
		if (parent === dir) {
			break;
		}
		dir = parent;
	}

	try {
		cachedRoot = execSync("git rev-parse --show-toplevel", {
			encoding: "utf8",
			stdio: ["pipe", "pipe", "pipe"],
		}).trim();
	} catch {
		cachedRoot = path.resolve(startDir);
	}

	return cachedRoot;
}

/**
 * Clears the cached repository root.
 * @internal For testing only.
 */
export function clearRepoCache(): void {
	cachedRoot = null;
}

/**
 * Resolves a path relative to the repository root.
 *
 * @param segments - Path segments to join
 * @returns Absolute path from repository root
 *
 * @example
 * ```typescript
 * const indexPath = resolvePath("package.json");
 * // "/Users/dev/my-project/package.json"
 *
 * const toolPath = resolvePath("tools", "lib", "repo.ts");
 * // "/Users/dev/my-project/tools/lib/repo.ts"
 * ```
 */
export function resolvePath(...segments: string[]): string {
	return path.join(findRepoRoot(), ...segments);
}

/**
 * Checks if a path exists relative to repository root.
 *
 * @param relativePath - Path relative to repo root
 * @returns True if path exists
 */
export function pathExists(relativePath: string): boolean {
	return fs.existsSync(resolvePath(relativePath));
}

/**
 * Gets the current git branch name.
 *
 * @returns Result containing branch name or error
 */
export function getCurrentBranch(): Result<string, Error> {
	try {
		const branch = execSync("git rev-parse --abbrev-ref HEAD", {
			encoding: "utf8",
			stdio: ["pipe", "pipe", "pipe"],
			cwd: findRepoRoot(),
		}).trim();
		return ok(branch);
	} catch (e) {
		return err(e instanceof Error ? e : new Error("Failed to get branch"));
	}
}

/**
 * Gets git user information.
 *
 * @returns Object with name and email
 */
export function getGitUser(): { name: string; email: string } {
	let name = "unknown";
	let email = "unknown@local";

	try {
		name = execSync("git config user.name", {
			encoding: "utf8",
			stdio: ["pipe", "pipe", "pipe"],
		}).trim();
	} catch {
		// Keep default
	}

	try {
		email = execSync("git config user.email", {
			encoding: "utf8",
			stdio: ["pipe", "pipe", "pipe"],
		}).trim();
	} catch {
		// Keep default
	}

	return { name, email };
}

/**
 * Gets the current git commit hash (short form).
 *
 * @returns Result containing commit hash or error
 */
export function getCurrentCommit(): Result<string, Error> {
	try {
		const hash = execSync("git rev-parse --short HEAD", {
			encoding: "utf8",
			stdio: ["pipe", "pipe", "pipe"],
			cwd: findRepoRoot(),
		}).trim();
		return ok(hash);
	} catch (e) {
		return err(e instanceof Error ? e : new Error("Failed to get commit"));
	}
}

/**
 * Checks if the repository has uncommitted changes.
 *
 * @returns True if there are uncommitted changes
 */
export function hasUncommittedChanges(): boolean {
	try {
		const status = execSync("git status --porcelain", {
			encoding: "utf8",
			stdio: ["pipe", "pipe", "pipe"],
			cwd: findRepoRoot(),
		}).trim();
		return status.length > 0;
	} catch {
		return false;
	}
}

/**
 * Reads a JSON file from the repository.
 *
 * @param relativePath - Path relative to repo root
 * @returns Result containing parsed JSON or error
 */
export function readJsonFile<T>(relativePath: string): Result<T, Error> {
	const fullPath = resolvePath(relativePath);

	if (!fs.existsSync(fullPath)) {
		return err(new Error(`File not found: ${relativePath}`));
	}

	try {
		const content = fs.readFileSync(fullPath, "utf8");
		const data = JSON.parse(content) as T;
		return ok(data);
	} catch (e) {
		return err(
			e instanceof Error ? e : new Error(`Failed to read ${relativePath}`),
		);
	}
}

/**
 * Writes a JSON file to the repository.
 *
 * @param relativePath - Path relative to repo root
 * @param data - Data to write
 * @returns Result indicating success or error
 */
export function writeJsonFile(
	relativePath: string,
	data: unknown,
): Result<void, Error> {
	const fullPath = resolvePath(relativePath);

	try {
		const dir = path.dirname(fullPath);
		if (!fs.existsSync(dir)) {
			fs.mkdirSync(dir, { recursive: true });
		}
		fs.writeFileSync(fullPath, `${JSON.stringify(data, null, 2)}\n`);
		return ok(undefined);
	} catch (e) {
		return err(
			e instanceof Error ? e : new Error(`Failed to write ${relativePath}`),
		);
	}
}

/**
 * Reads a text file from the repository.
 *
 * @param relativePath - Path relative to repo root
 * @returns Result containing file content or error
 */
export function readTextFile(relativePath: string): Result<string, Error> {
	const fullPath = resolvePath(relativePath);

	if (!fs.existsSync(fullPath)) {
		return err(new Error(`File not found: ${relativePath}`));
	}

	try {
		const content = fs.readFileSync(fullPath, "utf8");
		return ok(content);
	} catch (e) {
		return err(
			e instanceof Error ? e : new Error(`Failed to read ${relativePath}`),
		);
	}
}

/**
 * Converts a path to POSIX style (forward slashes).
 *
 * @param p - Path to convert
 * @returns POSIX-style path
 */
export function toPosixPath(p: string): string {
	return p.split(path.sep).join("/");
}

/**
 * Lists all markdown files in the repository.
 *
 * @param rootDir - Root directory to search (defaults to repo root)
 * @returns Array of relative paths to markdown files
 */
export function listMarkdownFiles(rootDir?: string): string[] {
	const root = rootDir ?? findRepoRoot();
	const results: string[] = [];

	function walk(absDir: string): void {
		const entries = fs.readdirSync(absDir, { withFileTypes: true });
		for (const entry of entries) {
			if (entry.name === ".git") continue;
			if (entry.name === "node_modules") continue;
			if (entry.name.startsWith(".kb-")) continue;

			const absPath = path.join(absDir, entry.name);
			if (entry.isDirectory()) {
				walk(absPath);
				continue;
			}
			if (!entry.isFile()) continue;
			if (!entry.name.endsWith(".md")) continue;

			const rel = toPosixPath(path.relative(root, absPath));
			results.push(rel);
		}
	}

	walk(root);
	results.sort();
	return results;
}

/**
 * Reads text content from a file.
 *
 * @param repoRoot - Repository root path
 * @param relPath - Relative path to file
 * @returns File content as string
 * @deprecated Use readTextFile(relativePath) which returns a Result.
 */
export function readText(repoRoot: string, relPath: string): string {
	const abs = path.join(repoRoot, relPath);
	return fs.readFileSync(abs, "utf8");
}
