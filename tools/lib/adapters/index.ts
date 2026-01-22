/**
 * @fileoverview Language adapter barrel exports
 * @module kb-tools/lib/adapters
 *
 * @description
 * Exports all language adapters and provides a factory function
 * to get the appropriate adapter for a detected language.
 */

import type { Language } from "../language-detection.js";
import type { LanguageAdapter } from "../check-registry.js";
import { typescriptAdapter, javascriptAdapter } from "./typescript.js";
import { goAdapter } from "./go.js";
import { pythonAdapter } from "./python.js";
import { rustAdapter } from "./rust.js";
import { javaAdapter } from "./java.js";

// ============================================================================
// Adapter Registry
// ============================================================================

/**
 * Map of all available adapters by language
 */
const ADAPTERS: Partial<Record<Language, LanguageAdapter>> = {
	typescript: typescriptAdapter,
	javascript: javascriptAdapter,
	go: goAdapter,
	python: pythonAdapter,
	rust: rustAdapter,
	java: javaAdapter,
};

/**
 * Get the adapter for a specific language
 */
export function getAdapter(language: Language): LanguageAdapter | undefined {
	return ADAPTERS[language];
}

/**
 * Get all available adapters
 */
export function getAllAdapters(): LanguageAdapter[] {
	return Object.values(ADAPTERS) as LanguageAdapter[];
}

/**
 * Check if a language has an adapter
 */
export function hasAdapter(language: Language): boolean {
	return language in ADAPTERS;
}

/**
 * Get list of supported languages
 */
export function getSupportedLanguages(): Language[] {
	return Object.keys(ADAPTERS) as Language[];
}

// ============================================================================
// Re-exports
// ============================================================================

export { typescriptAdapter, javascriptAdapter } from "./typescript.js";
export { goAdapter } from "./go.js";
export { pythonAdapter } from "./python.js";
export { rustAdapter } from "./rust.js";
export { javaAdapter } from "./java.js";

// Export all check IDs for reference
export const ALL_CHECK_IDS = [
	// Style & Validation (Pillar 1)
	"linter-exists",
	"type-checker-strict",
	"formatter-exists",
	"pre-commit-hooks",
	"no-lint-ignores",
	"no-unsafe-types",

	// Build System (Pillar 2)
	"dependency-manifest",
	"lockfile-exists",
	"package-json-exists",
	"build-defined",
	"ci-pipeline",
	"reproducible-builds",
	"no-deprecated-deps",

	// Testing (Pillar 3)
	"test-framework",
	"test-coverage",
	"tests-pass",
	"integration-tests",
	"e2e-tests",
	"test-isolation",

	// Documentation (Pillar 4)
	"readme-exists",
	"architecture-docs",
	"api-documentation",
	"changelog-exists",
	"inline-docs",
	"examples-exist",

	// Development Environment (Pillar 5)
	"env-setup-script",
	"devcontainer",
	"editor-config",
	"debug-configs",
	"local-env-docs",
	"watch-mode",

	// Debugging & Observability (Pillar 6)
	"structured-logging",
	"error-tracking",
	"tracing",
	"metrics",
	"health-endpoints",
	"log-levels",

	// Security (Pillar 7)
	"security-scanning",
	"secrets-management",
	"auth-implementation",
	"input-validation",
	"audit-logging",
	"vulnerability-policy",

	// Task Discovery (Pillar 8)
	"task-definitions",
	"npm-scripts",
	"makefile",
	"common-aliases",
	"task-documentation",
	"ci-tasks-aligned",

	// Product & Experimentation (Pillar 9)
	"feature-flags",
	"analytics",
	"ab-testing",
	"monitoring-dashboards",
	"error-budgets",
	"release-process",
] as const;

export type CheckId = (typeof ALL_CHECK_IDS)[number];
