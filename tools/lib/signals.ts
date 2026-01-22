/**
 * @fileoverview Signal handling for graceful shutdown
 * @module kb-tools/signals
 *
 * @description
 * Provides utilities for handling SIGINT and SIGTERM signals gracefully.
 * Ensures cleanup handlers run before process exits.
 *
 * @example
 * ```typescript
 * import { setupSignalHandlers, onCleanup } from "./lib/signals.js";
 *
 * setupSignalHandlers();
 *
 * // Register cleanup handler
 * const tempFile = createTempFile();
 * onCleanup(() => {
 *   fs.unlinkSync(tempFile);
 * });
 *
 * // When SIGINT/SIGTERM received, cleanup runs automatically
 * ```
 */

import { EXIT_CODES } from "./constants.js";

/** Cleanup function type - can be sync or async */
type CleanupFn = () => void | Promise<void>;

/** Registered cleanup handlers (LIFO order) */
const cleanupHandlers: CleanupFn[] = [];

/** Flag to prevent multiple signal handlers from running */
let isCleaningUp = false;

/** Flag to track if handlers are set up */
let handlersSetUp = false;

/**
 * Registers a cleanup function to run on process termination.
 *
 * Cleanup functions are called in LIFO order (last registered, first called).
 * Both sync and async functions are supported.
 *
 * @param fn - The cleanup function to register
 * @returns A function to unregister the cleanup handler
 *
 * @example
 * ```typescript
 * const unregister = onCleanup(() => {
 *   console.log("Cleaning up...");
 * });
 *
 * // Later, to remove the handler:
 * unregister();
 * ```
 */
export function onCleanup(fn: CleanupFn): () => void {
	cleanupHandlers.push(fn);

	return () => {
		const index = cleanupHandlers.indexOf(fn);
		if (index !== -1) {
			cleanupHandlers.splice(index, 1);
		}
	};
}

/**
 * Runs all registered cleanup handlers.
 *
 * @param signal - The signal that triggered cleanup
 * @returns Promise that resolves when all handlers complete
 */
async function runCleanup(signal: string): Promise<void> {
	if (isCleaningUp) {
		return;
	}
	isCleaningUp = true;

	try {
		console.log(`\nReceived ${signal}, cleaning up...`);

		// Run handlers in reverse order (LIFO) without mutating original array
		for (const fn of [...cleanupHandlers].reverse()) {
			try {
				await fn();
			} catch (e) {
				// Log but don't fail - we want to run all handlers
				console.error(
					`Cleanup error: ${e instanceof Error ? e.message : String(e)}`,
				);
			}
		}
	} finally {
		isCleaningUp = false;
	}
}

/**
 * Sets up SIGINT and SIGTERM signal handlers.
 *
 * Should be called once at application startup.
 * Safe to call multiple times (only sets up handlers once).
 *
 * @example
 * ```typescript
 * // At start of main()
 * setupSignalHandlers();
 * ```
 */
export function setupSignalHandlers(): void {
	if (handlersSetUp) {
		return;
	}
	handlersSetUp = true;

	const handler = async (signal: NodeJS.Signals): Promise<void> => {
		await runCleanup(signal);
		process.exit(EXIT_CODES.SIGNAL_INTERRUPT);
	};

	process.on("SIGINT", () => {
		void handler("SIGINT");
	});

	process.on("SIGTERM", () => {
		void handler("SIGTERM");
	});

	// Handle uncaught errors
	process.on("uncaughtException", async (error) => {
		console.error(`Uncaught exception: ${error.message}`);
		await runCleanup("uncaughtException");
		process.exit(EXIT_CODES.FATAL_ERROR);
	});

	process.on("unhandledRejection", async (reason) => {
		console.error(
			`Unhandled rejection: ${reason instanceof Error ? reason.message : String(reason)}`,
		);
		await runCleanup("unhandledRejection");
		process.exit(EXIT_CODES.FATAL_ERROR);
	});
}

/**
 * Clears all registered cleanup handlers.
 * @internal For testing only.
 */
export function clearCleanupHandlers(): void {
	cleanupHandlers.length = 0;
}

/**
 * Gets the count of registered cleanup handlers.
 * @internal For testing only.
 */
export function getCleanupHandlerCount(): number {
	return cleanupHandlers.length;
}
