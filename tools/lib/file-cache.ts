/**
 * @fileoverview File caching layer for readiness checks
 * @module kb-tools/lib/file-cache
 *
 * @description
 * Provides a caching layer for file operations during readiness assessment.
 * Files are read once per assessment run and cached in memory, reducing
 * redundant I/O operations when multiple checks read the same files.
 */

import fs from "node:fs";
import path from "node:path";

// ============================================================================
// Types
// ============================================================================

export interface FileCache {
	/** Check if a file exists (cached) */
	exists(filepath: string): Promise<boolean>;

	/** Read file as text (cached) */
	text(filepath: string): Promise<string | null>;

	/** Read file as JSON (cached) */
	json<T = unknown>(filepath: string): Promise<T | null>;

	/** Read directory contents (cached) */
	readdir(dirpath: string): Promise<string[]>;

	/** Read directory entries with file types (cached) */
	readdirWithTypes(dirpath: string): Promise<fs.Dirent[]>;

	/** Get cache statistics */
	stats(): CacheStats;

	/** Clear all caches */
	clear(): void;
}

export interface CacheStats {
	/** Number of existence checks cached */
	existsCached: number;
	/** Number of text reads cached */
	textCached: number;
	/** Number of JSON reads cached */
	jsonCached: number;
	/** Number of directory reads cached */
	readdirCached: number;
	/** Number of cache hits */
	hits: number;
	/** Number of cache misses (actual I/O operations) */
	misses: number;
}

// ============================================================================
// Implementation
// ============================================================================

/**
 * Creates a new file cache instance
 * Each assessment run should create a fresh cache
 */
export function createFileCache(): FileCache {
	// Cache storage
	const existsCache = new Map<string, boolean>();
	const textCache = new Map<string, string | null>();
	const jsonCache = new Map<string, unknown | null>();
	const readdirCache = new Map<string, string[]>();
	const readdirTypesCache = new Map<string, fs.Dirent[]>();

	// Statistics
	let hits = 0;
	let misses = 0;

	return {
		async exists(filepath: string): Promise<boolean> {
			const normalized = path.resolve(filepath);

			if (existsCache.has(normalized)) {
				hits++;
				return existsCache.get(normalized)!;
			}

			misses++;
			try {
				const result = await Bun.file(normalized).exists();
				existsCache.set(normalized, result);
				return result;
			} catch {
				existsCache.set(normalized, false);
				return false;
			}
		},

		async text(filepath: string): Promise<string | null> {
			const normalized = path.resolve(filepath);

			if (textCache.has(normalized)) {
				hits++;
				return textCache.get(normalized)!;
			}

			misses++;
			try {
				const file = Bun.file(normalized);
				if (!(await file.exists())) {
					textCache.set(normalized, null);
					return null;
				}
				const content = await file.text();
				textCache.set(normalized, content);
				return content;
			} catch {
				textCache.set(normalized, null);
				return null;
			}
		},

		async json<T = unknown>(filepath: string): Promise<T | null> {
			const normalized = path.resolve(filepath);

			if (jsonCache.has(normalized)) {
				hits++;
				return jsonCache.get(normalized) as T | null;
			}

			misses++;
			try {
				const file = Bun.file(normalized);
				if (!(await file.exists())) {
					jsonCache.set(normalized, null);
					return null;
				}
				const content = await file.json() as T;
				jsonCache.set(normalized, content);
				return content;
			} catch {
				jsonCache.set(normalized, null);
				return null;
			}
		},

		readdir(dirpath: string): Promise<string[]> {
			const normalized = path.resolve(dirpath);

			if (readdirCache.has(normalized)) {
				hits++;
				return Promise.resolve(readdirCache.get(normalized)!);
			}

			misses++;
			try {
				const entries = fs.readdirSync(normalized);
				readdirCache.set(normalized, entries);
				return Promise.resolve(entries);
			} catch {
				readdirCache.set(normalized, []);
				return Promise.resolve([]);
			}
		},

		readdirWithTypes(dirpath: string): Promise<fs.Dirent[]> {
			const normalized = path.resolve(dirpath);

			if (readdirTypesCache.has(normalized)) {
				hits++;
				return Promise.resolve(readdirTypesCache.get(normalized)!);
			}

			misses++;
			try {
				const entries = fs.readdirSync(normalized, { withFileTypes: true });
				readdirTypesCache.set(normalized, entries);
				return Promise.resolve(entries);
			} catch {
				readdirTypesCache.set(normalized, []);
				return Promise.resolve([]);
			}
		},

		stats(): CacheStats {
			return {
				existsCached: existsCache.size,
				textCached: textCache.size,
				jsonCached: jsonCache.size,
				readdirCached: readdirCache.size + readdirTypesCache.size,
				hits,
				misses,
			};
		},

		clear(): void {
			existsCache.clear();
			textCache.clear();
			jsonCache.clear();
			readdirCache.clear();
			readdirTypesCache.clear();
			hits = 0;
			misses = 0;
		},
	};
}

// ============================================================================
// Singleton for global use (optional)
// ============================================================================

let globalCache: FileCache | null = null;

/**
 * Get or create the global file cache
 * Use this when you don't want to pass cache through context
 */
export function getGlobalCache(): FileCache {
	if (!globalCache) {
		globalCache = createFileCache();
	}
	return globalCache;
}

/**
 * Clear the global cache
 * Call this at the start of each assessment run
 */
export function clearGlobalCache(): void {
	if (globalCache) {
		globalCache.clear();
	}
}
