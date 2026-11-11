/**
 * @fileoverview Pluggable check registry for Agent Readiness
 * @module kb-tools/lib/check-registry
 *
 * @description
 * Defines the check abstraction layer that separates "what to check" (criteria)
 * from "how to check" (language-specific implementations).
 *
 * Key concepts:
 * - Check: A criterion to evaluate (e.g., "linter configured")
 * - Adapter: Language-specific implementation of how to check
 * - Capability: The result of checking (pass/fail + metadata)
 *
 * This allows the same 9 pillars to work across Go, Python, Rust, etc.
 */

import type { DetectedApp } from "./app-discovery.js";
import type { Language } from "./language-detection.js";

// ============================================================================
// Core Types
// ============================================================================

/**
 * The 9 technical pillars from Factory.ai framework
 */
export type Pillar =
	| "style"
	| "build"
	| "testing"
	| "documentation"
	| "devenv"
	| "observability"
	| "security"
	| "taskdiscovery"
	| "product";

/**
 * Maturity levels (1-5)
 */
export type Level = 1 | 2 | 3 | 4 | 5;

/**
 * Human-readable pillar names
 */
export const PILLAR_NAMES: Record<Pillar, string> = {
	style: "Style & Validation",
	build: "Build System",
	testing: "Testing",
	documentation: "Documentation",
	devenv: "Development Environment",
	observability: "Debugging & Observability",
	security: "Security",
	taskdiscovery: "Task Discovery",
	product: "Product & Experimentation",
};

/**
 * Human-readable level names
 */
export const LEVEL_NAMES: Record<Level, string> = {
	1: "Functional",
	2: "Documented",
	3: "Standardized",
	4: "Optimized",
	5: "Autonomous",
};

/**
 * Result of running a check
 */
export interface CheckResult {
	/** Whether the check passed */
	pass: boolean;
	/** Human-readable details about the result */
	details?: string;
	/** Whether the check was skipped (e.g., --skip-tests) */
	skipped?: boolean;
	/** Tool that provides this capability (e.g., "ESLint", "golangci-lint") */
	tool?: string | undefined;
	/** Path to the configuration file */
	configPath?: string;
	/** Confidence in the result (0-100) */
	confidence?: number;
}

/**
 * A registered check definition
 */
export interface CheckDefinition {
	/** Unique check identifier */
	id: string;
	/** Which pillar this check belongs to */
	pillar: Pillar;
	/** Minimum level this check applies to */
	level: Level;
	/** Human-readable check name */
	name: string;
	/** Longer description of what this checks */
	description?: string;
	/** Languages this check applies to (empty = all) */
	languages?: Language[];
	/** Whether this check can be skipped */
	skippable?: boolean;
	/** Tags for filtering */
	tags?: string[];
}

/**
 * Context passed to check runners
 */
export interface CheckContext {
	/** The app being checked */
	app: DetectedApp;
	/** Repository root path */
	repoRoot: string;
	/** Runtime options */
	options: CheckOptions;
}

/**
 * Runtime options for checks
 */
export interface CheckOptions {
	/** Skip test execution */
	skipTests?: boolean;
	/** Skip build verification */
	skipBuild?: boolean;
	/** Timeout for long-running checks (ms) */
	timeout?: number;
	/** Verbose output */
	verbose?: boolean;
}

/**
 * A check runner function
 */
export type CheckRunner = (ctx: CheckContext) => Promise<CheckResult>;

/**
 * Result with check metadata attached
 */
export interface CheckResultWithMeta extends CheckResult {
	/** The check that was run */
	check: CheckDefinition;
	/** Time taken to run (ms) */
	durationMs?: number;
}

// ============================================================================
// Language Adapter Types
// ============================================================================

/**
 * A language adapter provides check implementations for a specific language
 */
export interface LanguageAdapter {
	/** Language this adapter handles */
	language: Language;
	/** Display name */
	displayName: string;
	/** Get a check runner for a given check ID */
	getRunner(checkId: string): CheckRunner | undefined;
}

// ============================================================================
// Check Registry Implementation
// ============================================================================

/**
 * Central registry for all checks
 */
export class CheckRegistry {
	private checks: Map<string, CheckDefinition> = new Map();
	private adapters: Map<Language, LanguageAdapter> = new Map();

	/**
	 * Register a check definition (overwrites if already exists)
	 */
	registerCheck(check: CheckDefinition): void {
		// Allow overwriting for testing and adapter registration
		this.checks.set(check.id, check);
	}

	/**
	 * Register multiple checks at once
	 */
	registerChecks(checks: CheckDefinition[]): void {
		for (const check of checks) {
			this.registerCheck(check);
		}
	}

	/**
	 * Register a language adapter
	 */
	registerAdapter(adapter: LanguageAdapter): void {
		this.adapters.set(adapter.language, adapter);
	}

	/**
	 * Get all registered checks
	 */
	getAllChecks(): CheckDefinition[] {
		return Array.from(this.checks.values());
	}

	/**
	 * Get checks applicable to a language
	 */
	getChecksForLanguage(language: Language): CheckDefinition[] {
		return this.getAllChecks().filter(
			(c) => !c.languages || c.languages.length === 0 || c.languages.includes(language),
		);
	}

	/**
	 * The language adapter's runner for a check; undefined when the check is not implemented for it
	 */
	getRunner(checkId: string, language: Language): CheckRunner | undefined {
		return this.adapters.get(language)?.getRunner(checkId);
	}

	/**
	 * Run a single check
	 */
	async runCheck(checkId: string, ctx: CheckContext): Promise<CheckResultWithMeta> {
		const check = this.checks.get(checkId);
		if (!check) {
			throw new Error(`Check '${checkId}' not found`);
		}

		// Check if applicable to this language
		if (check.languages && check.languages.length > 0) {
			if (!check.languages.includes(ctx.app.language)) {
				return {
					pass: true,
					skipped: true,
					details: `Not applicable to ${ctx.app.language}`,
					check,
				};
			}
		}

		const start = Date.now();
		const runner = this.getRunner(checkId, ctx.app.language);

		// A check that cannot run for this language counts neither for nor against the score.
		if (!runner) {
			return {
				pass: true,
				skipped: true,
				details: `Not implemented for ${ctx.app.language}`,
				check,
			};
		}

		try {
			const result = await runner(ctx);
			const durationMs = Date.now() - start;
			return { ...result, check, durationMs };
		} catch (error) {
			const durationMs = Date.now() - start;
			return {
				pass: false,
				details: error instanceof Error ? error.message : "Unknown error",
				check,
				durationMs,
			};
		}
	}

	/**
	 * Run all applicable checks for an app
	 */
	async runAllChecks(ctx: CheckContext): Promise<CheckResultWithMeta[]> {
		const applicableChecks = this.getChecksForLanguage(ctx.app.language);
		const results: CheckResultWithMeta[] = [];

		for (const check of applicableChecks) {
			const result = await this.runCheck(check.id, ctx);
			results.push(result);
		}

		return results;
	}
}

// ============================================================================
// Singleton Instance
// ============================================================================

/**
 * Global check registry instance
 */
export const checkRegistry = new CheckRegistry();

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Create a check definition helper
 */
export function defineCheck(
	id: string,
	pillar: Pillar,
	level: Level,
	name: string,
	options?: Partial<Omit<CheckDefinition, "id" | "pillar" | "level" | "name">>,
): CheckDefinition {
	return {
		id,
		pillar,
		level,
		name,
		...options,
	};
}

/**
 * Run with timeout (utility for runners)
 */
export async function runWithTimeout<T>(
	promise: Promise<T>,
	timeoutMs: number,
	cancel: () => Promise<void>,
): Promise<T> {
	let timer: ReturnType<typeof setTimeout> | undefined;
	let timedOut = false;
	try {
		return await Promise.race([
			promise,
			new Promise<never>((_, reject) => {
				timer = setTimeout(() => {
					timedOut = true;
					reject(new Error("Timeout"));
				}, timeoutMs);
			}),
		]);
	} finally {
		clearTimeout(timer);
		if (timedOut) await cancel();
	}
}
