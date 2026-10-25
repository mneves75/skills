/**
 * @fileoverview Shared constants for readiness-check tools
 * @module skills-tools/constants
 */

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
