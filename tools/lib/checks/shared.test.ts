import { expect, test } from "bun:test";
import { chmod, mkdir, mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

const cases = [
	{ check: "claude-md-recent", language: "typescript", command: "git", output: String(Math.floor(Date.now() / 1000)) },
	{ check: "test-framework", language: "go", command: "find", output: "example_test.go" },
	{ check: "test-framework", language: "rust", command: "grep", output: "example.rs:#[test]" },
	{ check: "test-framework", language: "java", command: "grep", output: "Example.java:@Test" },
	{ check: "release-process", language: "typescript", command: "ls", output: "release.yml" },
	{ check: "security-scanning", language: "typescript", command: "ls", output: "security.yml" },
];

for (const scenario of cases) {
	// Bun Shell implements ls internally, so PATH interception covers the external tools.
	for (const mode of scenario.command === "ls" ? ["fast"] : ["slow", "fast", "fail"]) {
		test(`${scenario.check} (${scenario.language}) bounds ${scenario.command}: ${mode}`, async () => {
			const directory = await mkdtemp(join(tmpdir(), "readiness-shared-"));
			const bin = join(directory, "bin");
			const pidFile = join(directory, "pid");
			const marker = join(directory, "finished");
			await mkdir(bin);
			await mkdir(join(directory, ".github/workflows"), { recursive: true });
			if (scenario.command === "ls") {
				await Bun.write(join(directory, ".github/workflows", scenario.output), "name: fixture");
			}
			await Bun.write(join(directory, "README.md"), "# Fixture");
			await Bun.write(join(bin, scenario.command), `#!/bin/sh
printf '%s' "$$" > '${pidFile}'
trap '' TERM
if [ '${mode}' = fail ]; then exit 7; fi
if [ '${mode}' = slow ]; then
  /bin/sleep 0.9
  printf finished > '${marker}'
fi
printf '%s\\n' '${scenario.output}'
`);
			await chmod(join(bin, scenario.command), 0o755);
			const script = `
				import { sharedChecks } from ${JSON.stringify(new URL("./shared.ts", import.meta.url).pathname)};
				import { createFileCache } from ${JSON.stringify(new URL("../file-cache.ts", import.meta.url).pathname)};
				const start = performance.now();
				const result = await sharedChecks[${JSON.stringify(scenario.check)}]({
					app: { path: ${JSON.stringify(directory)}, language: ${JSON.stringify(scenario.language)} },
					repoRoot: ${JSON.stringify(directory)}, options: { timeout: 150 }, cache: createFileCache(),
				});
				console.log(JSON.stringify({ result, elapsed: performance.now() - start }));
			`;
			const child = Bun.spawn([process.execPath, "--eval", script], {
				env: { PATH: `${bin}:${process.env["PATH"]}`, HOME: directory },
				stdout: "pipe", stderr: "pipe",
			});
			try {
				const stdout = new Response(child.stdout).text();
				const stderr = new Response(child.stderr).text();
				expect(await Promise.race([child.exited, Bun.sleep(2500).then(() => "hung")])).toBe(0);
				const { result, elapsed } = JSON.parse(await stdout) as { result: { pass: boolean }; elapsed: number };
				expect(await stderr).toBe("");
				if (mode === "slow") {
					expect(elapsed).toBeLessThan(700);
					expect(result.pass).toBe(false);
					const pid = Number(await Bun.file(pidFile).text());
					expect(() => process.kill(pid, 0)).toThrow();
					await Bun.sleep(1000);
					expect(await Bun.file(marker).exists()).toBe(false);
				} else {
					expect(result.pass).toBe(mode === "fast");
				}
			} finally {
				child.kill("SIGKILL");
				await child.exited;
				if (await Bun.file(pidFile).exists()) {
					try { process.kill(Number(await Bun.file(pidFile).text()), "SIGKILL"); } catch { /* already exited */ }
				}
				await rm(directory, { recursive: true, force: true });
			}
		});
	}
}
