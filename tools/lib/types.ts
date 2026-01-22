/**
 * @fileoverview Shared TypeScript types and interfaces for kb-tools
 * @module kb-tools/types
 */

// ============================================================================
// Guideline Index Types
// ============================================================================

/** Document kind classification */
export type GuidelineKind =
	| "guideline"
	| "rulebook"
	| "playbook"
	| "checklist"
	| "reference"
	| "process"
	| "meta"
	| "exec-spec"
	| "guide"
	| "directory"
	| "runbook";

/** Reading priority level */
export type GuidelinePriority =
	| "start-here"
	| "core"
	| "domain-specific"
	| "reference"
	| "required"
	| "recommended"
	| "optional";

/** Applicable domain */
export type GuidelineDomain =
	| "all"
	| "web"
	| "mobile"
	| "ios"
	| "android"
	| "backend"
	| "database"
	| "db"
	| "security"
	| "ai"
	| "infra"
	| "testing"
	| "observability"
	| "devops"
	| "api"
	| "data"
	| "design"
	| "integrations"
	| "ops"
	| "seo"
	| "tooling";

/** Single guideline entry in the index */
export interface GuidelineItem {
	/** File or directory path relative to repo root */
	path: string;
	/** Human-readable title */
	title: string;
	/** Document type classification */
	kind: GuidelineKind;
	/** Applicable domains */
	domains: GuidelineDomain[];
	/** Reading priority level */
	priority: GuidelinePriority;
	/** Conflict resolution priority (1 = highest) */
	conflictPriority?: number;
	/** One-line description of when to use */
	whenToUse: string;
	/** Recommended review frequency in days */
	reviewCadenceDays?: number;
	/** Last review date (YYYY-MM-DD) */
	lastReviewed?: string;
	/** Whether the document is deprecated */
	deprecated?: boolean;
	/** Path to replacement document if deprecated */
	replacedBy?: string;
}

/** Guidelines index structure */
export interface GuidelinesIndex {
	/** Schema version */
	schemaVersion: number;
	/** Last update date (YYYY-MM-DD) */
	updatedAt: string;
	/** List of all guideline documents */
	items: GuidelineItem[];
}

// ============================================================================
// Baseline Types
// ============================================================================

/** Package baseline entry */
export interface PackageBaseline {
	/** Package name */
	name: string;
	/** Minimum required version */
	minVersion: string;
	/** npm package name (if different) */
	npm?: string;
	/** GitHub repo (owner/repo) */
	github?: string;
	/** Last updated date (YYYY-MM-DD) */
	lastUpdated?: string;
}

/** Baselines configuration */
export interface BaselinesConfig {
	/** Schema version */
	schemaVersion: number;
	/** Last update date (YYYY-MM-DD) */
	updatedAt: string;
	/** Package baselines */
	packages: PackageBaseline[];
}

// ============================================================================
// Check Result Types
// ============================================================================

/** Check result status */
export type CheckStatus = "pass" | "fail" | "warn" | "skip";

/** Single check issue */
export interface CheckIssue {
	/** File path where issue was found */
	file?: string;
	/** Line number (1-indexed) */
	line?: number;
	/** Issue message */
	message: string;
	/** Issue severity */
	severity: "error" | "warning" | "info";
}

/** Check execution result */
export interface CheckResult {
	/** Tool name */
	name: string;
	/** Human-readable description */
	description: string;
	/** Whether this is a critical check */
	critical: boolean;
	/** Result status */
	status: CheckStatus;
	/** Exit code */
	exitCode: number;
	/** Number of issues found */
	issueCount: number;
	/** Detailed issues (if any) */
	issues: CheckIssue[];
	/** Execution duration in ms */
	duration?: number;
}

// ============================================================================
// Audit Types
// ============================================================================

/** Audit event action type */
export type AuditAction = "cite" | "check" | "read" | "skill" | "feedback";

/** Feedback type */
export type FeedbackType = "correction" | "suggestion" | "question" | "bug";

/** Base audit event */
export interface BaseAuditEvent {
	/** Unique event ID */
	id: string;
	/** ISO 8601 timestamp */
	timestamp: string;
	/** User name */
	user: string;
	/** User email */
	email: string;
	/** Git branch */
	branch: string;
}

/** Citation audit event */
export interface CiteEvent extends BaseAuditEvent {
	action: "cite";
	/** Guideline path */
	guideline: string;
	/** Specific section (optional) */
	section?: string;
}

/** Check audit event */
export interface CheckEvent extends BaseAuditEvent {
	action: "check";
	/** Tool name */
	tool: string;
	/** Check result */
	result: CheckStatus;
	/** Number of issues */
	issues?: number;
}

/** Read audit event */
export interface ReadEvent extends BaseAuditEvent {
	action: "read";
	/** Guideline path */
	guideline: string;
}

/** Skill invocation audit event */
export interface SkillEvent extends BaseAuditEvent {
	action: "skill";
	/** Skill name */
	skill: string;
}

/** Feedback audit event */
export interface FeedbackEvent extends BaseAuditEvent {
	action: "feedback";
	/** Guideline path */
	guideline: string;
	/** Feedback type */
	type: FeedbackType;
	/** Feedback message */
	message: string;
}

/** Union of all audit event types */
export type AuditEvent =
	| CiteEvent
	| CheckEvent
	| ReadEvent
	| SkillEvent
	| FeedbackEvent;

// ============================================================================
// Backup Types
// ============================================================================

/** Backup entry in manifest */
export interface BackupEntry {
	/** Backup name/ID */
	name: string;
	/** Creation timestamp (ISO 8601) */
	created: string;
	/** Reason for backup */
	reason?: string;
	/** Number of files */
	fileCount: number;
	/** Total size in bytes */
	size: number;
}

/** Backup manifest */
export interface BackupManifest {
	/** List of backups */
	backups: BackupEntry[];
}

// ============================================================================
// Essentials (formerly TL;DR) Types
// ============================================================================

/** Essentials quality score category */
export type TldrQuality = "excellent" | "good" | "acceptable" | "needsWork";

/** Essentials validation result */
export interface TldrValidation {
	/** File path */
	file: string;
	/** Quality score (0-5) */
	score: number;
	/** Quality category */
	quality: TldrQuality;
	/** Issues found */
	issues: string[];
	/** Has Essentials section */
	hasTldr: boolean;
	/** Number of bullets */
	bulletCount: number;
}

// ============================================================================
// Schema Validation Types
// ============================================================================

/** Schema validation error */
export interface SchemaError {
	/** JSON path where error occurred */
	path: string;
	/** Error message */
	message: string;
}

/** Schema validation result */
export interface SchemaValidationResult {
	/** Whether validation passed */
	valid: boolean;
	/** Validation errors */
	errors: SchemaError[];
}

// ============================================================================
// Network Types
// ============================================================================

/** Fetch options with retry support */
export interface FetchOptions {
	/** Number of retry attempts */
	retries?: number;
	/** Initial retry delay in ms */
	retryDelay?: number;
	/** Request timeout in ms */
	timeout?: number;
	/** Rate limit (requests per second) */
	rateLimit?: number;
	/** Additional headers */
	headers?: Record<string, string>;
}

/** Cache entry */
export interface CacheEntry<T> {
	/** Cached value */
	value: T;
	/** Cache timestamp */
	timestamp: number;
}
