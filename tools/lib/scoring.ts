/**
 * @fileoverview Scoring engine for Agent Readiness Assessment
 * @module kb-tools/lib/scoring
 *
 * @description
 * Implements Factory.ai-aligned scoring with three modes:
 * - Weighted: Pillar importance weights (Factory.ai default)
 * - Strict: Minimum level across all pillars (original behavior)
 * - Average: Simple percentage average
 *
 * Key insight: Factory.ai uses numerator/denominator per-app scoring,
 * then aggregates across the organization. This enables "5 of 7 apps
 * pass security" style reporting.
 */

import type {
	Pillar,
	Level,
	CheckResultWithMeta,
	CheckDefinition,
} from "./check-registry.js";
import type { DetectedApp } from "./app-discovery.js";

// ============================================================================
// Types
// ============================================================================

/**
 * Scoring mode selection
 */
export type ScoringMode = "weighted" | "strict" | "average";

/**
 * Scoring configuration
 */
export interface ScoringConfig {
	/** Which scoring algorithm to use */
	mode: ScoringMode;
	/** Custom pillar weights (only used in weighted mode) */
	pillarWeights?: Partial<Record<Pillar, number>>;
	/** Threshold for "passing" a check (0-100, default 80) */
	passThreshold?: number;
}

/**
 * Per-pillar score breakdown
 */
export interface PillarScore {
	pillar: Pillar;
	/** Display name */
	name: string;
	/** Score as percentage (0-100) */
	score: number;
	/** Derived level (1-5) */
	level: Level;
	/** Checks that passed */
	passed: number;
	/** Total applicable checks */
	total: number;
	/** Check results for this pillar */
	checks: CheckResultWithMeta[];
}

/**
 * Per-application score
 */
export interface AppScore {
	/** The application scored */
	app: DetectedApp;
	/** Per-pillar breakdown */
	pillars: PillarScore[];
	/** Overall maturity level */
	level: Level;
	/** Overall score (0-100) */
	score: number;
	/** All check results */
	checks: CheckResultWithMeta[];
	/** Time taken to run all checks (ms) */
	durationMs: number;
}

/**
 * Aggregated pillar score across multiple apps
 */
export interface AggregatedPillarScore {
	pillar: Pillar;
	name: string;
	/** Number of apps passing threshold for this pillar */
	numerator: number;
	/** Total apps evaluated */
	denominator: number;
	/** Percentage (numerator/denominator * 100) */
	percentage: number;
	/** Derived level from percentage */
	level: Level;
	/** Average score across all apps */
	averageScore: number;
}

/**
 * Organization-level (repo-level) score
 */
export interface OrgScore {
	/** Per-app scores */
	apps: AppScore[];
	/** Aggregated pillar scores */
	pillars: AggregatedPillarScore[];
	/** Overall maturity level */
	level: Level;
	/** Overall score (0-100) */
	score: number;
	/** Scoring mode used */
	mode: ScoringMode;
	/** Total checks run across all apps */
	totalChecks: number;
	/** Total checks passed across all apps */
	totalPassed: number;
}

// ============================================================================
// Constants
// ============================================================================

/**
 * Default pillar weights based on Factory.ai apparent behavior
 *
 * Calibrated against Factory.ai benchmark scores:
 * - FastAPI (Python): Factory.ai L3 (53%) vs Our L3 (53%) ✓
 * - CockroachDB (Go): Factory.ai L4 (74%) vs Our L3 (56%)
 *
 * Key insight: Factory.ai weights "visible maturity indicators" higher:
 * - Documentation, build, and style are most visible for OSS projects
 * - Product/observability are less relevant for libraries/frameworks
 * - Large OSS projects often have internal solutions for logging/auth
 */
export const DEFAULT_PILLAR_WEIGHTS: Record<Pillar, number> = {
	style: 1.0, // Essential for code quality
	build: 1.3, // Critical for contributions and CI
	testing: 1.4, // Important for safety (but not overweighted)
	documentation: 1.5, // Most visible maturity indicator for OSS
	devenv: 0.5, // Nice to have, but established projects work differently
	observability: 0.5, // Large projects have internal solutions
	security: 0.8, // Important but often internal for enterprises
	taskdiscovery: 0.5, // Nice to have
	product: 0.3, // Not relevant for OSS libraries/frameworks
};

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
 * Level thresholds (percentage -> level)
 *
 * These are calibrated to match Factory.ai's apparent scoring:
 * - L5 (Autonomous): 80%+ - Full agent delegation possible
 * - L4 (Optimized): 65%+ - Agents can work with minimal supervision
 * - L3 (Standardized): 50%+ - Agents need some guidance
 * - L2 (Documented): 35%+ - Agents struggle but can contribute
 * - L1 (Functional): <35% - Not ready for agents
 */
export const LEVEL_THRESHOLDS: [number, Level][] = [
	[80, 5],
	[65, 4],
	[50, 3],
	[35, 2],
	[0, 1],
];

/**
 * Level names for display
 */
export const LEVEL_NAMES: Record<Level, string> = {
	1: "Functional",
	2: "Documented",
	3: "Standardized",
	4: "Optimized",
	5: "Autonomous",
};

// ============================================================================
// Core Scoring Functions
// ============================================================================

/**
 * Calculate level from percentage score
 */
export function scoreToLevel(score: number): Level {
	for (const [threshold, level] of LEVEL_THRESHOLDS) {
		if (score >= threshold) {
			return level;
		}
	}
	return 1;
}

/**
 * Calculate pillar scores from check results
 */
export function calculatePillarScores(
	checks: CheckResultWithMeta[],
): PillarScore[] {
	// Group checks by pillar
	const byPillar = new Map<Pillar, CheckResultWithMeta[]>();

	for (const check of checks) {
		const pillar = check.check.pillar;
		if (!byPillar.has(pillar)) {
			byPillar.set(pillar, []);
		}
		byPillar.get(pillar)!.push(check);
	}

	// Calculate score for each pillar
	const scores: PillarScore[] = [];

	for (const [pillar, pillarChecks] of byPillar) {
		// Filter out skipped checks for scoring
		const applicable = pillarChecks.filter((c) => !c.skipped);
		const passed = applicable.filter((c) => c.pass).length;
		const total = applicable.length;

		// Score is percentage of passed checks
		const score = total > 0 ? (passed / total) * 100 : 0;

		scores.push({
			pillar,
			name: PILLAR_NAMES[pillar],
			score,
			level: scoreToLevel(score),
			passed,
			total,
			checks: pillarChecks,
		});
	}

	// Sort by pillar order (style -> product)
	const pillarOrder: Pillar[] = [
		"style",
		"build",
		"testing",
		"documentation",
		"devenv",
		"observability",
		"security",
		"taskdiscovery",
		"product",
	];

	scores.sort(
		(a, b) => pillarOrder.indexOf(a.pillar) - pillarOrder.indexOf(b.pillar),
	);

	return scores;
}

/**
 * Calculate overall score using strict mode (minimum level)
 *
 * This is the original behavior: maturity = min(pillar levels)
 * One weak pillar drags the entire score down.
 */
export function calculateStrict(pillars: PillarScore[]): {
	level: Level;
	score: number;
} {
	if (pillars.length === 0) {
		return { level: 1, score: 0 };
	}

	// Minimum level across all pillars
	const minLevel = Math.min(...pillars.map((p) => p.level)) as Level;

	// Average score for reporting
	const avgScore =
		pillars.reduce((sum, p) => sum + p.score, 0) / pillars.length;

	return {
		level: minLevel,
		score: Math.round(avgScore * 10) / 10,
	};
}

/**
 * Calculate overall score using weighted mode
 *
 * Pillars have different importance weights.
 * This better reflects Factory.ai's apparent scoring behavior.
 */
export function calculateWeighted(
	pillars: PillarScore[],
	weights: Record<Pillar, number> = DEFAULT_PILLAR_WEIGHTS,
): { level: Level; score: number } {
	if (pillars.length === 0) {
		return { level: 1, score: 0 };
	}

	let weightedSum = 0;
	let totalWeight = 0;

	for (const pillar of pillars) {
		const weight = weights[pillar.pillar] ?? 1.0;
		weightedSum += pillar.score * weight;
		totalWeight += weight;
	}

	const score = totalWeight > 0 ? weightedSum / totalWeight : 0;

	return {
		level: scoreToLevel(score),
		score: Math.round(score * 10) / 10,
	};
}

/**
 * Calculate overall score using average mode
 *
 * Simple average of all pillar scores.
 * Most lenient mode, good for progress tracking.
 */
export function calculateAverage(pillars: PillarScore[]): {
	level: Level;
	score: number;
} {
	if (pillars.length === 0) {
		return { level: 1, score: 0 };
	}

	const avgScore =
		pillars.reduce((sum, p) => sum + p.score, 0) / pillars.length;

	return {
		level: scoreToLevel(avgScore),
		score: Math.round(avgScore * 10) / 10,
	};
}

// ============================================================================
// Application Scoring
// ============================================================================

/**
 * Calculate score for a single application
 */
export function calculateAppScore(
	app: DetectedApp,
	checks: CheckResultWithMeta[],
	config: ScoringConfig = { mode: "weighted" },
): AppScore {
	const startTime = Date.now();

	// Calculate pillar scores
	const pillars = calculatePillarScores(checks);

	// Get weights (merge custom with defaults)
	const weights = {
		...DEFAULT_PILLAR_WEIGHTS,
		...(config.pillarWeights ?? {}),
	};

	// Calculate overall score based on mode
	let result: { level: Level; score: number };

	switch (config.mode) {
		case "strict":
			result = calculateStrict(pillars);
			break;
		case "average":
			result = calculateAverage(pillars);
			break;
		case "weighted":
		default:
			result = calculateWeighted(pillars, weights);
			break;
	}

	// Sum up check durations
	const durationMs = checks.reduce((sum, c) => sum + (c.durationMs ?? 0), 0);

	return {
		app,
		pillars,
		level: result.level,
		score: result.score,
		checks,
		durationMs,
	};
}

// ============================================================================
// Organization Aggregation
// ============================================================================

/**
 * Aggregate scores across multiple applications
 *
 * This implements Factory.ai's numerator/denominator pattern:
 * "5 of 7 apps pass security at L3+"
 */
export function aggregateOrgScore(
	appScores: AppScore[],
	config: ScoringConfig = { mode: "weighted" },
): OrgScore {
	if (appScores.length === 0) {
		return {
			apps: [],
			pillars: [],
			level: 1,
			score: 0,
			mode: config.mode,
			totalChecks: 0,
			totalPassed: 0,
		};
	}

	const passThreshold = config.passThreshold ?? 80;

	// Collect all pillars across all apps
	const pillarSet = new Set<Pillar>();
	for (const app of appScores) {
		for (const pillar of app.pillars) {
			pillarSet.add(pillar.pillar);
		}
	}

	// Aggregate each pillar
	const aggregatedPillars: AggregatedPillarScore[] = [];

	for (const pillar of pillarSet) {
		const appPillarScores: number[] = [];

		for (const app of appScores) {
			const pillarScore = app.pillars.find((p) => p.pillar === pillar);
			if (pillarScore) {
				appPillarScores.push(pillarScore.score);
			}
		}

		const numerator = appPillarScores.filter((s) => s >= passThreshold).length;
		const denominator = appPillarScores.length;
		const percentage = denominator > 0 ? (numerator / denominator) * 100 : 0;
		const averageScore =
			appPillarScores.length > 0
				? appPillarScores.reduce((a, b) => a + b, 0) / appPillarScores.length
				: 0;

		aggregatedPillars.push({
			pillar,
			name: PILLAR_NAMES[pillar],
			numerator,
			denominator,
			percentage,
			level: scoreToLevel(percentage),
			averageScore: Math.round(averageScore * 10) / 10,
		});
	}

	// Sort pillars by standard order
	const pillarOrder: Pillar[] = [
		"style",
		"build",
		"testing",
		"documentation",
		"devenv",
		"observability",
		"security",
		"taskdiscovery",
		"product",
	];

	aggregatedPillars.sort(
		(a, b) => pillarOrder.indexOf(a.pillar) - pillarOrder.indexOf(b.pillar),
	);

	// Calculate overall org score
	const weights = {
		...DEFAULT_PILLAR_WEIGHTS,
		...(config.pillarWeights ?? {}),
	};

	// Convert aggregated pillars to PillarScore format for reuse
	const pillarScoresForCalc: PillarScore[] = aggregatedPillars.map((ap) => ({
		pillar: ap.pillar,
		name: ap.name,
		score: ap.averageScore,
		level: scoreToLevel(ap.averageScore),
		passed: ap.numerator,
		total: ap.denominator,
		checks: [],
	}));

	let result: { level: Level; score: number };

	switch (config.mode) {
		case "strict":
			result = calculateStrict(pillarScoresForCalc);
			break;
		case "average":
			result = calculateAverage(pillarScoresForCalc);
			break;
		case "weighted":
		default:
			result = calculateWeighted(pillarScoresForCalc, weights);
			break;
	}

	// Tally total checks
	let totalChecks = 0;
	let totalPassed = 0;

	for (const app of appScores) {
		for (const check of app.checks) {
			if (!check.skipped) {
				totalChecks++;
				if (check.pass) {
					totalPassed++;
				}
			}
		}
	}

	return {
		apps: appScores,
		pillars: aggregatedPillars,
		level: result.level,
		score: result.score,
		mode: config.mode,
		totalChecks,
		totalPassed,
	};
}

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Generate a summary line for an app score
 */
export function formatAppSummary(appScore: AppScore): string {
	const levelName = LEVEL_NAMES[appScore.level];
	const passedTotal = appScore.checks.filter(
		(c) => !c.skipped && c.pass,
	).length;
	const total = appScore.checks.filter((c) => !c.skipped).length;

	return `${appScore.app.name}: L${appScore.level} (${levelName}) - ${appScore.score}% (${passedTotal}/${total} checks)`;
}

/**
 * Generate a summary line for org score
 */
export function formatOrgSummary(orgScore: OrgScore): string {
	const levelName = LEVEL_NAMES[orgScore.level];
	const appCount = orgScore.apps.length;
	const appWord = appCount === 1 ? "app" : "apps";

	return `Organization: L${orgScore.level} (${levelName}) - ${orgScore.score}% across ${appCount} ${appWord}`;
}

/**
 * Get top improvement recommendations
 *
 * Identifies the highest-impact changes to improve the score.
 */
export function getTopRecommendations(
	appScore: AppScore,
	limit = 3,
): Array<{
	pillar: Pillar;
	check: CheckDefinition;
	impact: "high" | "medium" | "low";
	reason: string;
}> {
	// Find failing checks in important pillars
	const failingChecks: Array<{
		pillar: Pillar;
		check: CheckDefinition;
		weight: number;
		level: Level;
	}> = [];

	for (const pillarScore of appScore.pillars) {
		for (const checkResult of pillarScore.checks) {
			if (!checkResult.pass && !checkResult.skipped) {
				failingChecks.push({
					pillar: pillarScore.pillar,
					check: checkResult.check,
					weight: DEFAULT_PILLAR_WEIGHTS[pillarScore.pillar],
					level: checkResult.check.level,
				});
			}
		}
	}

	// Sort by: weight * (6 - level) to prioritize high-weight, low-level checks
	failingChecks.sort((a, b) => {
		const aScore = a.weight * (6 - a.level);
		const bScore = b.weight * (6 - b.level);
		return bScore - aScore;
	});

	// Take top N and format
	return failingChecks.slice(0, limit).map((fc) => ({
		pillar: fc.pillar,
		check: fc.check,
		impact: fc.weight >= 1.2 ? "high" : fc.weight >= 0.8 ? "medium" : "low",
		reason: `Improve ${PILLAR_NAMES[fc.pillar]} (L${fc.level} requirement)`,
	}));
}

/**
 * Compare two scores and describe the difference
 */
export function compareScores(
	before: AppScore,
	after: AppScore,
): {
	levelChange: number;
	scoreChange: number;
	improved: Pillar[];
	regressed: Pillar[];
} {
	const levelChange = after.level - before.level;
	const scoreChange = Math.round((after.score - before.score) * 10) / 10;

	const improved: Pillar[] = [];
	const regressed: Pillar[] = [];

	for (const afterPillar of after.pillars) {
		const beforePillar = before.pillars.find(
			(p) => p.pillar === afterPillar.pillar,
		);
		if (beforePillar) {
			if (afterPillar.score > beforePillar.score) {
				improved.push(afterPillar.pillar);
			} else if (afterPillar.score < beforePillar.score) {
				regressed.push(afterPillar.pillar);
			}
		}
	}

	return { levelChange, scoreChange, improved, regressed };
}
