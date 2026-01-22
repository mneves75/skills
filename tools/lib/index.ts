/**
 * @fileoverview kb-tools shared utilities index
 * @module kb-tools/lib
 *
 * @description
 * Central export point for all kb-tools shared utilities.
 * Import from this file to access all utilities.
 *
 * @example
 * ```typescript
 * import {
 *   findRepoRoot,
 *   resolvePath,
 *   Result, ok, err,
 *   setupSignalHandlers,
 *   parseArgs,
 *   EXIT_CODES
 * } from "./lib/index.js";
 * ```
 */

// CLI utilities
export {
	type ArgConfig,
	generateHelp,
	getOption,
	getOptionInt,
	type HelpConfig,
	type HelpOption,
	hasFlag,
	hasHelpFlag,
	type ParsedArgs,
	parseArgs,
} from "./cli.js";
// Constants
export {
	CACHE_TTL_MS,
	EXIT_CODES,
	MAX_AUDIT_DAYS,
	MAX_BACKUP_COUNT,
	PATHS,
	RATE_LIMITS,
	RETRY_CONFIG,
	TIMEOUTS,
} from "./constants.js";
// HTTP fetch utilities
export {
	clearRateLimiters,
	fetchGitHubVersion,
	fetchJson,
	fetchNpmVersion,
	fetchWithRetry,
} from "./fetch.js";
// Progress indicators
export {
	formatDuration,
	ProgressBar,
	type ProgressBarOptions,
	type SpinnerControl,
	spinner,
	statusLine,
} from "./progress.js";
// Reference/path helpers
export {
	formatError,
	type ResolveRefInput,
	resolveRefPath,
	stripVendoredPrefix,
} from "./refs.js";
// Repository utilities
export {
	clearRepoCache,
	findRepoRoot,
	getCurrentBranch,
	getCurrentCommit,
	getGitUser,
	hasUncommittedChanges,
	listMarkdownFiles,
	pathExists,
	readJsonFile,
	readText,
	readTextFile,
	resolvePath,
	toPosixPath,
	writeJsonFile,
} from "./repo.js";
// Result type
export {
	chain,
	collect,
	err,
	isErr,
	isOk,
	map,
	mapErr,
	ok,
	type Result,
	tryCatch,
	tryCatchAsync,
	unwrap,
	unwrapOr,
} from "./result.js";
// Signal handling
export {
	clearCleanupHandlers,
	getCleanupHandlerCount,
	onCleanup,
	setupSignalHandlers,
} from "./signals.js";

// Types
export type {
	AuditAction,
	AuditEvent,
	BackupEntry,
	BackupManifest,
	BaseAuditEvent,
	BaselinesConfig,
	CacheEntry,
	CheckEvent,
	CheckIssue,
	CheckResult,
	CheckStatus,
	CiteEvent,
	FeedbackEvent,
	FeedbackType,
	FetchOptions,
	GuidelineDomain,
	GuidelineItem,
	GuidelineKind,
	GuidelinePriority,
	GuidelinesIndex,
	PackageBaseline,
	ReadEvent,
	SchemaError,
	SchemaValidationResult,
	SkillEvent,
	TldrQuality,
	TldrValidation,
} from "./types.js";
