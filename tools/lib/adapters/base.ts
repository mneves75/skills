/**
 * @fileoverview Adapter base factory
 * @module kb-tools/lib/adapters/base
 *
 * @description
 * Factory for creating language adapters with automatic fallback to shared checks.
 * Reduces boilerplate by allowing adapters to only implement language-specific checks
 * while inheriting common patterns from the shared check library.
 */

import type { CheckRunner, LanguageAdapter } from "../check-registry.js";
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
