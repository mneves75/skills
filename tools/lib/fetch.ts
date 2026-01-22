/**
 * @fileoverview HTTP fetch utilities with retry and rate limiting
 * @module kb-tools/fetch
 *
 * @description
 * Provides fetch wrapper with:
 * - Automatic retries with exponential backoff
 * - Per-host rate limiting
 * - Request timeouts
 * - Structured error handling via Result type
 *
 * @example
 * ```typescript
 * import { fetchWithRetry } from "./lib/fetch.js";
 *
 * const result = await fetchWithRetry("https://api.example.com/data", {
 *   retries: 3,
 *   timeout: 5000,
 *   rateLimit: 10
 * });
 *
 * if (result.ok) {
 *   const data = await result.value.json();
 * } else {
 *   console.error(result.error.message);
 * }
 * ```
 */

import { RATE_LIMITS, RETRY_CONFIG, TIMEOUTS } from "./constants.js";
import type { Result } from "./result.js";
import { err, ok } from "./result.js";
import type { FetchOptions } from "./types.js";

/** Per-host rate limiter state */
const rateLimiters = new Map<string, number>();

/**
 * Sleeps for specified milliseconds.
 *
 * @param ms - Duration in milliseconds
 * @returns Promise that resolves after delay
 */
function sleep(ms: number): Promise<void> {
	return new Promise((resolve) => setTimeout(resolve, ms));
}

/**
 * Fetch with automatic retry, timeout, and rate limiting.
 *
 * @param url - URL to fetch
 * @param options - Fetch options
 * @returns Result containing Response or Error
 *
 * @remarks
 * - Retries with exponential backoff (1s, 2s, 4s...)
 * - Does not retry 4xx errors (client errors)
 * - Respects per-host rate limits
 * - Aborts on timeout
 *
 * @example
 * ```typescript
 * // Fetch with defaults
 * const result = await fetchWithRetry("https://api.example.com");
 *
 * // Fetch with custom options
 * const result = await fetchWithRetry("https://api.github.com/repos/...", {
 *   retries: 5,
 *   timeout: 15000,
 *   rateLimit: 5, // GitHub rate limit
 *   headers: { "Accept": "application/vnd.github.v3+json" }
 * });
 * ```
 */
export async function fetchWithRetry(
	url: string,
	options: FetchOptions = {},
): Promise<Result<Response, Error>> {
	const {
		retries = RETRY_CONFIG.RETRIES,
		retryDelay = RETRY_CONFIG.INITIAL_DELAY,
		timeout = TIMEOUTS.DEFAULT,
		rateLimit = RATE_LIMITS.NPM,
		headers = {},
	} = options;

	// Apply rate limiting
	const host = new URL(url).host;
	const now = Date.now();
	const lastRequest = rateLimiters.get(host) || 0;
	const minInterval = 1000 / rateLimit;

	if (now - lastRequest < minInterval) {
		await sleep(minInterval - (now - lastRequest));
	}
	rateLimiters.set(host, Date.now());

	// Retry loop
	let lastError: Error | null = null;

	for (let attempt = 0; attempt <= retries; attempt++) {
		const controller = new AbortController();
		const timeoutId = setTimeout(() => controller.abort(), timeout);

		try {
			const response = await fetch(url, {
				signal: controller.signal,
				headers: {
					"User-Agent": "kb-tools/1.0",
					Accept: "application/json",
					...headers,
				},
			});

			if (response.ok) {
				return ok(response);
			}

			// Don't retry most 4xx errors (client errors)
			if (
				response.status >= 400 &&
				response.status < 500 &&
				response.status !== 429
			) {
				return err(
					new Error(`HTTP ${response.status}: ${response.statusText}`),
				);
			}

			// Server error or rate limit - will retry
			lastError = new Error(`HTTP ${response.status}: ${response.statusText}`);
		} catch (e) {
			if (e instanceof Error && e.name === "AbortError") {
				lastError = new Error(`Request timeout after ${timeout}ms`);
			} else {
				lastError = e instanceof Error ? e : new Error(String(e));
			}
		} finally {
			clearTimeout(timeoutId);
		}

		// Retry with exponential backoff
		if (attempt < retries) {
			const delay = Math.min(retryDelay * 2 ** attempt, RETRY_CONFIG.MAX_DELAY);
			await sleep(delay);
		}
	}

	return err(lastError || new Error("Unknown fetch error"));
}

/**
 * Fetches JSON data with retry support.
 *
 * @param url - URL to fetch
 * @param options - Fetch options
 * @returns Result containing parsed JSON or Error
 *
 * @example
 * ```typescript
 * const result = await fetchJson<PackageInfo>(
 *   "https://registry.npmjs.org/typescript/latest"
 * );
 *
 * if (result.ok) {
 *   console.log(result.value.version);
 * }
 * ```
 */
export async function fetchJson<T>(
	url: string,
	options: FetchOptions = {},
): Promise<Result<T, Error>> {
	const responseResult = await fetchWithRetry(url, options);

	if (!responseResult.ok) {
		return responseResult;
	}

	try {
		const data = (await responseResult.value.json()) as T;
		return ok(data);
	} catch (e) {
		return err(e instanceof Error ? e : new Error("Failed to parse JSON"));
	}
}

/**
 * Fetches the latest version from npm registry.
 *
 * @param packageName - npm package name
 * @returns Result containing version string or Error
 *
 * @example
 * ```typescript
 * const result = await fetchNpmVersion("typescript");
 * if (result.ok) {
 *   console.log(`Latest: ${result.value}`);
 * }
 * ```
 */
export async function fetchNpmVersion(
	packageName: string,
): Promise<Result<string, Error>> {
	const result = await fetchJson<{ version: string }>(
		`https://registry.npmjs.org/${packageName}/latest`,
		{
			timeout: TIMEOUTS.NPM,
			rateLimit: RATE_LIMITS.NPM,
		},
	);

	if (!result.ok) {
		return result;
	}

	return ok(result.value.version);
}

/**
 * Fetches the latest release version from GitHub.
 *
 * @param repo - Repository in "owner/repo" format
 * @returns Result containing version string (without 'v' prefix) or Error
 *
 * @example
 * ```typescript
 * const result = await fetchGitHubVersion("microsoft/typescript");
 * if (result.ok) {
 *   console.log(`Latest: ${result.value}`);
 * }
 * ```
 */
export async function fetchGitHubVersion(
	repo: string,
): Promise<Result<string, Error>> {
	const result = await fetchJson<{ tag_name: string }>(
		`https://api.github.com/repos/${repo}/releases/latest`,
		{
			timeout: TIMEOUTS.GITHUB,
			rateLimit: RATE_LIMITS.GITHUB,
			headers: {
				Accept: "application/vnd.github.v3+json",
			},
		},
	);

	if (!result.ok) {
		return result;
	}

	// Remove 'v' prefix if present
	const version = result.value.tag_name?.replace(/^v/, "") || "0.0.0";
	return ok(version);
}

/**
 * Clears rate limiter state.
 * @internal For testing only.
 */
export function clearRateLimiters(): void {
	rateLimiters.clear();
}
