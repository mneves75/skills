/**
 * @fileoverview Adapter base factory
 * @module kb-tools/lib/adapters/base
 *
 * @description
 * Factory for creating language adapters with automatic fallback to shared checks.
 * Reduces boilerplate by allowing adapters to only implement language-specific checks
 * while inheriting common patterns from the shared check library.
 */

import path from "node:path";
import type { CheckResult, CheckRunner, LanguageAdapter } from "../check-registry.js";
import { fileExists, readText } from "../check-registry.js";
import { listSharedChecks, sharedChecks } from "../checks/shared.js";
import type { Language } from "../language-detection.js";

// ============================================================================
// Types
// ============================================================================

/**
 * Configuration for creating a language adapter
 */
export interface AdapterConfig {
	/** Language identifier */
	language: Language;
	/** Human-readable display name */
	displayName: string;
	/** Language-specific check runners */
	runners: Record<string, CheckRunner>;
	/**
	 * Optional list of shared checks to exclude for this language
	 * (e.g., TypeScript-only checks excluded from Go adapter)
	 */
	excludeSharedChecks?: string[];
}

// ============================================================================
// Factory Function
// ============================================================================

/**
 * Creates a language adapter with automatic fallback to shared checks.
 *
 * Language-specific checks take precedence over shared checks with the same ID.
 * This allows adapters to override common patterns when needed while still
 * benefiting from shared implementations for truly universal checks.
 *
 * @example
 * ```typescript
 * const goAdapter = createLanguageAdapter({
 *   language: "go",
 *   displayName: "Go",
 *   runners: {
 *     "linter-exists": async (ctx) => { ... },
 *     "type-checker-strict": async (ctx) => { ... },
 *   },
 * });
 * ```
 */
export function createLanguageAdapter(config: AdapterConfig): LanguageAdapter {
	const { language, displayName, runners, excludeSharedChecks = [] } = config;

	// Build the set of excluded checks for fast lookup
	const excludedSet = new Set(excludeSharedChecks);

	return {
		language,
		displayName,

		getRunner(checkId: string): CheckRunner | undefined {
			// Language-specific runners take precedence
			if (runners[checkId]) {
				return runners[checkId];
			}

			// Fall back to shared checks unless excluded
			if (!excludedSet.has(checkId) && sharedChecks[checkId]) {
				return sharedChecks[checkId];
			}

			return undefined;
		},

		supportedChecks(): string[] {
			// Combine language-specific and shared checks
			const languageChecks = Object.keys(runners);
			const sharedCheckIds = listSharedChecks().filter(
				(id) => !excludedSet.has(id) && !runners[id]
			);

			return [...languageChecks, ...sharedCheckIds];
		},
	};
}

// ============================================================================
// Source scanning
// ============================================================================

/** Directories that hold vendored, generated or environment files, not the project's own code. */
const SCAN_SKIP_DIRS = new Set([
	"node_modules",
	"vendor",
	"venv",
	"dist",
	"build",
	"target",
	"__pycache__",
	"site-packages",
]);

/**
 * Count source lines under `root` matching `pattern` in files with the given extensions.
 * Hidden directories (`.git`, `.venv`) and SCAN_SKIP_DIRS are not scanned.
 */
export async function countSourceMatches(
	root: string,
	extensions: readonly string[],
	pattern: RegExp,
): Promise<number> {
	const glob = new Bun.Glob(`**/*.{${extensions.join(",")}}`);
	let count = 0;
	for await (const file of glob.scan({ cwd: root, onlyFiles: true, followSymlinks: false })) {
		if (file.split("/").some((part) => SCAN_SKIP_DIRS.has(part))) continue;
		const text = await Bun.file(path.join(root, file)).text();
		for (const line of text.split("\n")) if (pattern.test(line)) count++;
	}
	return count;
}

/**
 * Find a task runner an agent can list tasks from: Makefile targets, a justfile, a Taskfile,
 * or one of `extraFiles` (the language's own runners).
 */
export async function findTaskRunner(appPath: string, extraFiles: readonly string[] = []): Promise<CheckResult> {
	const targets = (await readText(path.join(appPath, "Makefile")))?.match(/^[a-zA-Z_-]+:/gm)?.length ?? 0;
	if (targets > 0) return { pass: true, configPath: "Makefile", details: `${targets} Makefile targets` };
	for (const file of ["justfile", "Justfile", "Taskfile.yml", "Taskfile.yaml", ...extraFiles]) {
		if (await fileExists(path.join(appPath, file))) return { pass: true, configPath: file };
	}
	return { pass: false, details: "No task runner configured" };
}
