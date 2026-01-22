/**
 * @fileoverview Reference path utilities for markdown links
 * @module kb-tools/refs
 */

import path from "node:path";
import { toPosixPath } from "./repo.js";

/**
 * Strips the vendored DOCS/ prefix if present.
 */
export function stripVendoredPrefix(p: string): string {
	const normalized = p.replace(/\\/g, "/");
	const prefix = "DOCS/";
	if (normalized.startsWith(prefix)) return normalized.slice(prefix.length);
	return normalized;
}

/**
 * Normalizes unknown errors into readable strings.
 */
export function formatError(err: unknown): string {
	return err instanceof Error ? err.message : String(err);
}

export interface ResolveRefInput {
	repoRoot: string;
	fromRelPath: string;
	refPath: string;
}

/**
 * Resolves a markdown reference to a repo-relative path when applicable.
 * Returns null for external or unsupported references.
 */
export function resolveRefPath({
	repoRoot,
	fromRelPath,
	refPath,
}: ResolveRefInput): string | null {
	const raw = refPath.trim();
	const noAngles =
		raw.startsWith("<") && raw.endsWith(">") ? raw.slice(1, -1) : raw;
	const withoutHash = noAngles.split("#")[0] ?? "";
	const withoutQuery = withoutHash.split("?")[0] ?? "";
	const firstToken = withoutQuery.trim().split(/\s+/)[0] ?? "";
	const stripped = stripVendoredPrefix(firstToken);

	if (stripped === "") return ".";

	if (stripped.startsWith("/")) return null;
	if (stripped.startsWith("#")) return null;
	if (/^[a-zA-Z][a-zA-Z0-9+.-]*:/.test(stripped)) return null;

	// Relative to the file that referenced it (Markdown link behavior).
	if (firstToken.startsWith("./") || firstToken.startsWith("../")) {
		const fromDir = path.dirname(path.join(repoRoot, fromRelPath));
		const abs = path.resolve(fromDir, stripped);
		return toPosixPath(path.relative(repoRoot, abs));
	}

	// Default: interpret as repo-root relative.
	return stripped;
}
