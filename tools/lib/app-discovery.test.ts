import { afterEach, expect, test } from "bun:test";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { discoverApps } from "./app-discovery.js";

const directories: string[] = [];

afterEach(async () => {
	for (const directory of directories.splice(0)) {
		await rm(directory, { recursive: true, force: true });
	}
});

test("pnpm discovery bounds crafted lines and preserves ordinary quoted patterns", async () => {
	const directory = await mkdtemp(join(tmpdir(), "readiness-discovery-"));
	directories.push(directory);
	await Bun.write(join(directory, "pnpm-workspace.yaml"), [
		"packages:",
		`  - 'apps/${" ".repeat(65536)}tail'`,
		`  - '${"x".repeat(4096)}'`,
		"  - 'apps/*'   ",
		'  - "packages/*"\t',
		"  - modules/*",
	].join("\n"));
	const start = performance.now();
	const result = await discoverApps(directory);
	expect(performance.now() - start).toBeLessThan(500);
	expect(result.workspaceConfig?.patterns).toEqual([
		"apps/*", "packages/*", "modules/*",
	]);
});
