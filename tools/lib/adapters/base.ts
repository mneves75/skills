/**
 * @fileoverview Adapter base factory
 * @module kb-tools/lib/adapters/base
 *
 * @description
 * Factory for creating language adapters with automatic fallback to shared checks.
 * Reduces boilerplate by allowing adapters to only implement language-specific checks
 * while inheriting common patterns from the shared check library.
 */

import type { Language } from "../language-detection.js";
import type { LanguageAdapter, CheckRunner } from "../check-registry.js";
import { sharedChecks, listSharedChecks } from "../checks/shared.js";

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
// Check Categories
// ============================================================================

/**
 * Check IDs that are always language-specific and should never use shared impl.
 * These checks require language-specific tooling detection (linters, formatters, etc.)
 */
export const LANGUAGE_SPECIFIC_CHECKS = new Set([
	// Style & Validation (tool-specific)
	"linter-exists",
	"type-checker-strict",
	"formatter-exists",
	"no-any-casts",
	"no-ts-ignore",
	"no-lint-ignores",
	"no-unsafe-types",
	"strict-mode",
	"zero-lint-errors",

	// Build System (toolchain-specific)
	"build-command",
	"build-defined",
	"lockfile-exists",
	"dependency-manifest",
	"package-json-exists",
	"deps-installed",
	"build-succeeds",
	"reproducible-builds",
	"no-deprecated-deps",

	// Testing (runner-specific)
	"tests-exist",
	"tests-pass",
	"test-coverage",
	"integration-tests",
	"e2e-tests",
	"test-isolation",
	"tests-fast",

	// Observability (console.log is language-specific)
	"console-logs-minimal",
	"log-levels",
	"health-endpoints",

	// Documentation (language-specific commands in CLAUDE.md)
	"inline-docs",

	// CI (language-specific test commands)
	"ci-runs-tests",
	"ci-tasks-aligned",

	// Task Discovery (npm scripts is JS-specific)
	"npm-scripts",
	"common-aliases",
	"task-documentation",
	"watch-mode",

	// Security (language-specific auth patterns)
	"auth-implementation",
	"audit-logging",

	// Product
	"ab-testing",
	"monitoring-dashboards",
	"error-budgets",
]);

/**
 * Check IDs that are shared across languages via the dependency parsing module.
 * These use LIBRARY_MAPPINGS to detect libraries for each language.
 */
export const SHARED_ONLY_CHECKS = new Set([
	// Documentation
	"readme-exists",
	"gitignore-exists",
	"claude-md-exists",
	"claude-md-concise",
	"claude-md-recent",
	"claude-md-has-commands",
	"contributing-guide",
	"changelog-exists",
	"architecture-docs",
	"api-documentation",
	"examples-exist",

	// Development Environment
	"editorconfig-exists",
	"devcontainer-exists",
	"env-example",
	"docker-compose",
	"env-setup-script",
	"debug-configs",
	"local-env-docs",

	// Security
	"git-initialized",
	"no-secrets-in-repo",
	"secret-scanning",
	"codeowners-exists",
	"branch-protection-documented",
	"dependency-scanning",
	"pre-commit-hooks",
	"secrets-management",
	"security-scanning",
	"vulnerability-policy",

	// Task Discovery
	"pr-template",
	"issue-templates",
	"branch-naming",
	"commit-convention",
	"task-definitions",
	"makefile",
	"release-process",

	// CI/CD
	"ci-configured",
	"ci-pipeline",

	// Observability (using dependency parsing)
	"structured-logging",
	"error-tracking",
	"tracing",
	"metrics",

	// Testing (using dependency parsing)
	"test-framework",
	"input-validation",

	// Product (using dependency parsing)
	"feature-flags",
	"analytics",
]);

/**
 * Returns true if a check should be language-specific
 */
export function isLanguageSpecificCheck(checkId: string): boolean {
	return LANGUAGE_SPECIFIC_CHECKS.has(checkId);
}

/**
 * Returns true if a check should use shared implementation
 */
export function isSharedCheck(checkId: string): boolean {
	return SHARED_ONLY_CHECKS.has(checkId);
}
