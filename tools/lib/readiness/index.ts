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
	detectLanguage,
	detectLanguageQuick,
	getLanguageName,
	isPolyglot,
	type Language,
	type LanguageDetection,
	type LanguageSignal,
	type SignalSource,
} from "../language-detection.js";

// ============================================================================
// Application Discovery
// ============================================================================

export {
	type AppType,
	type DetectedApp,
	type DiscoveryResult,
	discoverApps,
	getDeployableApps,
	getPrimaryApp,
	type ManifestType,
	type WorkspaceConfig,
} from "../app-discovery.js";

// ============================================================================
// Check Registry
// ============================================================================

export {
	type CheckContext,
	type CheckDefinition,
	type CheckOptions,
	type CheckResult,
	type CheckResultWithMeta,
	type CheckRunner,
	checkRegistry,
	createAdapter,
	defineCheck,
	dirExists,
	fileExists,
	type LanguageAdapter,
	type LanguageAdapterFactory,
	LEVEL_NAMES,
	type Level,
	PILLAR_NAMES,
	type Pillar,
	type RegisteredCheck,
	readJson,
	readText,
	runWithTimeout,
} from "../check-registry.js";

// ============================================================================
// Scoring
// ============================================================================

export {
	type AggregatedPillarScore,
	type AppScore,
	aggregateOrgScore,
	calculateAppScore,
	calculateAverage,
	calculatePillarScores,
	calculateStrict,
	calculateWeighted,
	compareScores,
	DEFAULT_PILLAR_WEIGHTS,
	formatAppSummary,
	formatOrgSummary,
	getTopRecommendations,
	LEVEL_THRESHOLDS,
	type OrgScore,
	type PillarScore,
	type ScoringConfig,
	type ScoringMode,
	scoreToLevel,
} from "../scoring.js";

// ============================================================================
// Adapters
// ============================================================================

export {
	ALL_CHECK_IDS,
	type CheckId,
	getAdapter,
	getAllAdapters,
	getSupportedLanguages,
	goAdapter,
	hasAdapter,
	javascriptAdapter,
	pythonAdapter,
	typescriptAdapter,
} from "../adapters/index.js";
