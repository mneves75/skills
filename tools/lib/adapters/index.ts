/**
 * @fileoverview Language adapter barrel exports
 * @module kb-tools/lib/adapters
 *
 * @description
 * Exports all language adapters and provides a factory function
 * to get the appropriate adapter for a detected language.
 */

import type { LanguageAdapter } from "../check-registry.js";
import type { Language } from "../language-detection.js";
import { goAdapter } from "./go.js";
import { javaAdapter } from "./java.js";
import { pythonAdapter } from "./python.js";
import { rustAdapter } from "./rust.js";
import { javascriptAdapter, typescriptAdapter } from "./typescript.js";

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
 * Get list of supported languages
 */
export function getSupportedLanguages(): Language[] {
	return Object.keys(ADAPTERS) as Language[];
}

// ============================================================================
// Re-exports
// ============================================================================

export { goAdapter } from "./go.js";
export { javaAdapter } from "./java.js";
export { pythonAdapter } from "./python.js";
export { rustAdapter } from "./rust.js";
export { javascriptAdapter, typescriptAdapter } from "./typescript.js";
