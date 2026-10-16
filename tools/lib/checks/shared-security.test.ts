import { expect, test } from "bun:test";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import type { CheckContext } from "../check-registry.js";
import { createFileCache } from "../file-cache.js";
import { sharedChecks } from "./shared.js";

for (const suspicious of [".env", "credentials.json", "secrets.json", "private.key", undefined]) {
	for (const example of [false, true]) {
		test(`secrets-management: ${suspicious ?? "clean"}, example=${example}`, async () => {
			const directory = await mkdtemp(join(tmpdir(), "readiness-secrets-"));
			try {
				if (suspicious) await Bun.write(join(directory, suspicious), "fixture");
				if (example) await Bun.write(join(directory, ".env.example"), "PLACEHOLDER=");
				const ctx: CheckContext = {
					app: {
						id: ".", name: "fixture", path: directory, relativePath: ".",
						type: "app", language: "typescript", manifest: "package.json",
						manifestPath: join(directory, "package.json"), isRoot: true,
					},
					repoRoot: directory, options: {}, cache: createFileCache(),
				};
				const result = await sharedChecks["secrets-management"]?.(ctx);
				expect(result?.pass).toBe(suspicious === undefined);
				if (suspicious) expect(result?.details).toContain("Potential secrets");
			} finally {
				await rm(directory, { recursive: true, force: true });
			}
		});
	}
}
