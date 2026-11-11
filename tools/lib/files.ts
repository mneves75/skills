/**
 * @fileoverview File helpers for discovery, language detection and check runners
 * @module kb-tools/lib/files
 *
 * Every helper answers "absent" (false or null) instead of throwing, so an unreadable
 * file counts as a missing one.
 */

import { statSync } from "node:fs";

export async function fileExists(filepath: string): Promise<boolean> {
	try {
		return await Bun.file(filepath).exists();
	} catch {
		return false;
	}
}

export function dirExists(dirpath: string): boolean {
	try {
		return statSync(dirpath).isDirectory();
	} catch {
		return false;
	}
}

export async function readJson<T>(filepath: string): Promise<T | null> {
	try {
		const file = Bun.file(filepath);
		if (!(await file.exists())) return null;
		return await file.json();
	} catch {
		return null;
	}
}

export async function readText(filepath: string): Promise<string | null> {
	try {
		const file = Bun.file(filepath);
		if (!(await file.exists())) return null;
		return await file.text();
	} catch {
		return null;
	}
}
