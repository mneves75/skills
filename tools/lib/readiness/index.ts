/**
 * @fileoverview Agent Readiness Assessment v2.0 - Main exports
 * @module kb-tools/lib/readiness
 *
 * @description
 * Factory.ai-aligned codebase readiness assessment.
 *
 * Key features:
 * - Multi-language support (Go, Python, Rust, TypeScript, JavaScript)
 * - Monorepo application discovery
 * - Pluggable check registry
 * - Multiple scoring modes (weighted/strict/average)
 *
 * Usage:
 * ```typescript
 * import { discoverApps, detectLanguage, checkRegistry, calculateAppScore } from './lib/readiness';
 *
 * const result = await discoverApps('/path/to/repo');
 * for (const app of result.apps) {
 *   const results = await checkRegistry.runAllChecks({
 *     app,
 *     repoRoot: apps.repoRoot,
 *     options: { skipTests: true }
 *   });
 *   const score = calculateAppScore(app, results);
 *   console.log(`${app.name}: L${score.level} (${score.score}%)`);
 * }
 * ```
 */

// ============================================================================
// Language Detection
// ============================================================================

export {
	type Language,
	type SignalSource,
	type LanguageSignal,
	type LanguageDetection,
	detectLanguage,
	detectLanguageQuick,
	isPolyglot,
	getLanguageName,
} from "../language-detection.js";

// ============================================================================
// Application Discovery
// ============================================================================

export {
	type AppType,
	type ManifestType,
	type DetectedApp,
	type DiscoveryResult,
	type WorkspaceConfig,
	discoverApps,
	getDeployableApps,
	getPrimaryApp,
} from "../app-discovery.js";

// ============================================================================
// Check Registry
// ============================================================================

export {
	type Pillar,
	type Level,
	type CheckResult,
	type CheckDefinition,
	type CheckContext,
	type CheckOptions,
	type CheckRunner,
	type RegisteredCheck,
	type CheckResultWithMeta,
	type LanguageAdapter,
	type LanguageAdapterFactory,
	checkRegistry,
	defineCheck,
	createAdapter,
	fileExists,
	dirExists,
	readJson,
	readText,
	runWithTimeout,
	PILLAR_NAMES,
	LEVEL_NAMES,
} from "../check-registry.js";

// ============================================================================
// Scoring
// ============================================================================

export {
	type ScoringMode,
	type ScoringConfig,
	type PillarScore,
	type AppScore,
	type AggregatedPillarScore,
	type OrgScore,
	scoreToLevel,
	calculatePillarScores,
	calculateStrict,
	calculateWeighted,
	calculateAverage,
	calculateAppScore,
	aggregateOrgScore,
	formatAppSummary,
	formatOrgSummary,
	getTopRecommendations,
	compareScores,
	DEFAULT_PILLAR_WEIGHTS,
	LEVEL_THRESHOLDS,
} from "../scoring.js";

// ============================================================================
// Adapters
// ============================================================================

export {
	getAdapter,
	getAllAdapters,
	hasAdapter,
	getSupportedLanguages,
	typescriptAdapter,
	javascriptAdapter,
	goAdapter,
	pythonAdapter,
	ALL_CHECK_IDS,
	type CheckId,
} from "../adapters/index.js";
