/**
 * @fileoverview Shared constants for readiness-check tools
 * @module skills-tools/constants
 */

/** Standard directory paths used by kb-tools */
export const PATHS = {
	/** Cache directory for API responses */
	CACHE_DIR: ".kb-cache",
	/** Audit log directory */
	AUDIT_DIR: ".kb-audit",
	/** Backup directory */
	BACKUP_DIR: ".kb-backups",
	/** Version baselines file */
	BASELINES: "baselines.json",
	/** Guidelines index file */
	INDEX: "GUIDELINES_INDEX.json",
	/** Schemas directory */
	SCHEMAS_DIR: "schemas",
} as const;

/** Standardized exit codes for consistent CI/CD behavior */
export const EXIT_CODES = {
	/** Successful execution */
	SUCCESS: 0,
	/** Validation or check failure */
	VALIDATION_ERROR: 1,
	/** Fatal/unexpected error */
	FATAL_ERROR: 2,
	/** Interrupted by signal (128 + SIGINT=2) */
	SIGNAL_INTERRUPT: 130,
} as const;

/** Cache time-to-live in milliseconds (1 hour) */
export const CACHE_TTL_MS = 3600000;

/** Maximum number of backups to retain */
export const MAX_BACKUP_COUNT = 10;

/** Maximum days of audit logs to retain */
export const MAX_AUDIT_DAYS = 90;

/** Rate limits for external APIs (requests per second) */
export const RATE_LIMITS = {
	/** npm registry */
	NPM: 20,
	/** GitHub API */
	GITHUB: 5,
} as const;

/** Network request timeouts in milliseconds */
export const TIMEOUTS = {
	/** Default request timeout */
	DEFAULT: 10000,
	/** npm registry timeout */
	NPM: 5000,
	/** GitHub API timeout */
	GITHUB: 10000,
} as const;

/** Default retry configuration */
export const RETRY_CONFIG = {
	/** Number of retry attempts */
	RETRIES: 3,
	/** Initial delay between retries (ms) */
	INITIAL_DELAY: 1000,
	/** Maximum delay between retries (ms) */
	MAX_DELAY: 10000,
} as const;
