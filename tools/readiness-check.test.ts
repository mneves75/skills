import { expect, test } from "bun:test";
import { chmod, mkdir, mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { scoreToLevel } from "./lib/scoring.js";

for (const signal of ["SIGTERM", "SIGINT"] as const) {
	test(`checker ${signal} stops active command descendants before exiting`, async () => {
		const directory = await mkdtemp(join(tmpdir(), "readiness-parent-"));
		const bin = join(directory, "bin");
		const pidFile = join(directory, "pids.json");
		const marker = join(directory, "finished");
		const worker = join(directory, "worker.ts");
		await mkdir(bin);
		await Bun.write(join(directory, "package.json"), '{"name":"signal-fixture"}');
		await Bun.write(join(directory, "tsconfig.json"), "{}");
		await Bun.write(join(directory, "biome.json"), "{}");
		await Bun.write(worker, `
			import { spawn } from "node:child_process";
			import { writeFileSync } from "node:fs";
			process.on("SIGTERM", () => {});
			process.on("SIGINT", () => {});
			const child = spawn(process.execPath, ["--eval", 'setInterval(() => {}, 1000)'], { stdio: "inherit" });
			writeFileSync(${JSON.stringify(pidFile)}, JSON.stringify([process.pid, child.pid]));
			setTimeout(() => writeFileSync(${JSON.stringify(marker)}, "outlived parent"), 1000);
			setInterval(() => {}, 1000);
		`);
		await Bun.write(join(bin, "bunx"), `#!/bin/sh\nexec '${process.execPath}' '${worker}'\n`);
		await chmod(join(bin, "bunx"), 0o755);
		const checker = Bun.spawn([
			process.execPath,
			new URL("./readiness-check.ts", import.meta.url).pathname,
			"--language=typescript", "--skip-tests", "--skip-build", "--format=json",
		], {
			cwd: directory,
			env: { PATH: `${bin}:${process.env["PATH"]}`, HOME: directory },
			stdout: "ignore", stderr: "ignore",
		});
		let pids: number[] = [];
		try {
			const readyDeadline = Date.now() + 3000;
			while (!(await Bun.file(pidFile).exists()) && Date.now() < readyDeadline) {
				await Bun.sleep(10);
			}
			expect(await Bun.file(pidFile).exists()).toBe(true);
			pids = await Bun.file(pidFile).json();
			for (const pid of pids) process.kill(pid, 0);
			checker.kill(signal);
			const exited = await Promise.race([checker.exited, Bun.sleep(1000).then(() => "still running")]);
			expect(exited).not.toBe("still running");
			// SIGKILL is sent before exit, but delivery and reaping lag under heavy load.
			const isAlive = (pid: number) => { try { process.kill(pid, 0); return true; } catch { return false; } };
			const goneDeadline = Date.now() + 500;
			while (pids.some(isAlive) && Date.now() < goneDeadline) await Bun.sleep(10);
			for (const pid of pids) expect(() => process.kill(pid, 0)).toThrow();
			await Bun.sleep(1100);
			expect(await Bun.file(marker).exists()).toBe(false);
		} finally {
			checker.kill("SIGKILL");
			await checker.exited;
			for (const pid of pids) {
				try { process.kill(pid, "SIGKILL"); } catch { /* already exited */ }
			}
			await rm(directory, { recursive: true, force: true });
		}
	});
}

test("checker rejects invalid option values instead of passing a CI gate vacuously", async () => {
	const directory = await mkdtemp(join(tmpdir(), "readiness-options-"));
	await Bun.write(join(directory, "package.json"), '{"name":"options-fixture"}');
	const run = async (flag: string) => {
		const checker = Bun.spawn([
			process.execPath, new URL("./readiness-check.ts", import.meta.url).pathname,
			"--language=typescript", "--skip-tests", "--skip-build", flag,
		], { cwd: directory, stdout: "ignore", stderr: "pipe" });
		const stderr = await new Response(checker.stderr).text();
		return { code: await checker.exited, stderr };
	};
	try {
		// Positive control: a valid gate the fixture cannot meet still fails with the gate's code.
		expect((await run("--min-level=5")).code).toBe(1);
		// A known language without an adapter is refused, naming the supported ones, instead of scoring nothing.
		const php = await run("--language=php");
		expect(php.code).toBe(2);
		for (const language of ["typescript", "javascript", "go", "python", "rust", "java"]) expect(php.stderr).toContain(language);
		for (const flag of ["--min-level=L5", "--min-level=0", "--min-level=6", "--min-level=3x", "--scoring=bogus", "--scoring=", "--format=bogus", "--format=", "--language=cobol", "--language=php", "--language=unknown"]) {
			const { code, stderr } = await run(flag);
			expect({ flag, code }).toEqual({ flag, code: 2 });
			expect(stderr).toContain(flag.slice(2, flag.indexOf("=")));
		}
	} finally {
		await rm(directory, { recursive: true, force: true });
	}
}, 60000);

test("checker rejects unknown options, options without a value and stray arguments before assessing", async () => {
	const directory = await mkdtemp(join(tmpdir(), "readiness-arguments-"));
	await Bun.write(join(directory, "package.json"), '{"name":"arguments-fixture"}');
	const run = async (...extra: string[]) => {
		const checker = Bun.spawn([
			process.execPath, new URL("./readiness-check.ts", import.meta.url).pathname,
			"--language=typescript", "--skip-tests", "--skip-build", ...extra,
		], { cwd: directory, stdout: "pipe", stderr: "pipe" });
		const [stdout, stderr] = await Promise.all([new Response(checker.stdout).text(), new Response(checker.stderr).text()]);
		return { code: await checker.exited, stdout, stderr };
	};
	try {
		// Positive control: the space-separated value form still reaches the gate.
		expect((await run("--min-level", "5")).code).toBe(1);
		for (const extra of [["--min-levle=5"], ["--min-level"], ["-o"], ["--min-level", "--verbose"], ["stray"], ["--bogus", "stray"]]) {
			const { code, stdout, stderr } = await run(...extra);
			expect({ extra, code }).toEqual({ extra, code: 2 });
			expect(stdout).not.toContain("Agent Readiness Check");
			for (const argument of extra.filter((arg) => arg !== "--verbose")) expect(stderr).toContain(argument);
		}
	} finally {
		await rm(directory, { recursive: true, force: true });
	}
}, 60000);

test("a single-app pillar's level follows the score printed beside it", async () => {
	const directory = await mkdtemp(join(tmpdir(), "readiness-levels-"));
	try {
		await Bun.write(join(directory, "package.json"), '{"name":"levels-fixture","scripts":{"build":"tsc","test":"bun test"}}');
		await Bun.write(join(directory, "tsconfig.json"), '{"compilerOptions":{"strict":true}}');
		await Bun.write(join(directory, "README.md"), "# Fixture\n\nRun `bun run build`.\n");
		await Bun.write(join(directory, "src/index.ts"), "export const answer = 42;\n");
		const checker = Bun.spawn([
			process.execPath, new URL("./readiness-check.ts", import.meta.url).pathname,
			"--language=typescript", "--skip-tests", "--skip-build", "--format=json",
		], { cwd: directory, stdout: "pipe", stderr: "ignore" });
		const stdout = await new Response(checker.stdout).text();
		expect(await checker.exited).toBe(0);
		const report = JSON.parse(stdout) as { apps: unknown[]; pillars: { pillar: string; score: number; level: number }[] };
		expect(report.apps.length).toBe(1);
		const rows = report.pillars.map(({ pillar, score, level }) => ({ pillar, score, level }));
		expect(rows).toEqual(rows.map((row) => ({ ...row, level: scoreToLevel(row.score) })));
		// The fixture must exercise the middle levels, or the equality above proves nothing about L2-L4.
		expect(rows.some((row) => row.level > 1 && row.level < 5)).toBe(true);
	} finally {
		await rm(directory, { recursive: true, force: true });
	}
}, 60000);

for (const [language, files] of [
	["rust", { "Cargo.toml": '[package]\nname = "fixture"\nversion = "0.1.0"\n', "src/main.rs": "fn main() {}\n" }],
	["java", { "pom.xml": "<project><modelVersion>4.0.0</modelVersion></project>\n", "src/main/java/App.java": "class App {}\n" }],
] as const) {
	test(`${language}: a check with no ${language} runner is skipped and listed once, never a gap or a failure`, async () => {
		const directory = await mkdtemp(join(tmpdir(), "readiness-stubs-"));
		try {
			for (const [file, content] of Object.entries(files)) await Bun.write(join(directory, file), content);
			const run = async (format: string) => {
				const checker = Bun.spawn([
					process.execPath, new URL("./readiness-check.ts", import.meta.url).pathname,
					`--language=${language}`, "--skip-tests", "--skip-build", `--format=${format}`,
				], { cwd: directory, stdout: "pipe", stderr: "ignore" });
				const stdout = await new Response(checker.stdout).text();
				expect(await checker.exited).toBe(0);
				return stdout;
			};
			type Result = { pass: boolean; skipped?: boolean; details?: string; check: { id: string; name: string } };
			const report = JSON.parse(await run("json")) as {
				pillars: { checks: Result[] }[]; blockingGaps: Result[]; warnings: Result[]; passingChecks: Result[];
				notImplemented: { language: string; checks: { id: string; name: string }[] }[];
			};
			const results = report.pillars.flatMap((pillar) => pillar.checks);
			expect(results.filter((r) => r.details === "Override required").map((r) => r.check.id)).toEqual([]);
			const notImplemented = report.notImplemented.flatMap((entry) => entry.checks.map((check) => check.id));
			expect(report.notImplemented.map((entry) => entry.language)).toEqual([language]);
			expect(notImplemented).toContain("no-deprecated-deps");
			expect(new Set(notImplemented).size).toBe(notImplemented.length);
			for (const id of notImplemented) {
				expect(results.filter((r) => r.check.id === id).map((r) => r.skipped)).toEqual([true]);
				for (const list of [report.blockingGaps, report.warnings, report.passingChecks]) {
					expect(list.map((r) => r.check.id)).not.toContain(id);
				}
			}
			for (const format of ["md", "html"]) {
				const rendered = await run(format);
				expect(rendered.split(`Not implemented for ${language}`).length).toBe(2);
				expect(rendered).not.toContain("Override required");
			}
		} finally {
			await rm(directory, { recursive: true, force: true });
		}
	}, 60000);
}

test("checker keeps every = after the first in an option value and rejects an empty one", async () => {
	const directory = await mkdtemp(join(tmpdir(), "readiness-equals-"));
	await Bun.write(join(directory, "package.json"), '{"name":"equals-fixture"}');
	const run = async (...flags: string[]) => {
		const checker = Bun.spawn([
			process.execPath, new URL("./readiness-check.ts", import.meta.url).pathname,
			"--language=typescript", "--skip-tests", "--skip-build", "--format=json", ...flags,
		], { cwd: directory, stdout: "ignore", stderr: "pipe" });
		const stderr = await new Response(checker.stderr).text();
		return { code: await checker.exited, stderr };
	};
	try {
		expect((await run("--output=a=b")).code).toBe(0);
		expect(await Bun.file(join(directory, "a=b")).exists()).toBe(true);
		expect(await Bun.file(join(directory, "a")).exists()).toBe(false);
		for (const flags of [["--output="], ["-o="], ["--app="], ["--output", ""], ["-o", ""], ["--app", ""]]) {
			const { code, stderr } = await run(...flags);
			expect({ flags, code }).toEqual({ flags, code: 2 });
			expect(stderr).toContain(flags[0] ?? "");
		}
	} finally {
		await rm(directory, { recursive: true, force: true });
	}
}, 60000);

for (const [config, linter] of [["biome.json", "biome"], ["eslint.config.js", "eslint"]] as const) {
	test(`the ${linter} check never asks bunx to download a missing package`, async () => {
		const directory = await mkdtemp(join(tmpdir(), "readiness-bunx-"));
		const bin = join(directory, "bin");
		const argv = join(directory, "argv.txt");
		try {
			await mkdir(bin);
			await Bun.write(join(directory, "package.json"), '{"name":"bunx-fixture"}');
			await Bun.write(join(directory, config), "{}");
			await Bun.write(join(bin, "bunx"), `#!/bin/sh\nprintf '%s\\n' "$*" >> '${argv}'\n`);
			await chmod(join(bin, "bunx"), 0o755);
			const checker = Bun.spawn([
				process.execPath, new URL("./readiness-check.ts", import.meta.url).pathname,
				"--language=typescript", "--skip-tests", "--skip-build", "--format=json",
			], { cwd: directory, env: { PATH: `${bin}:${process.env["PATH"]}`, HOME: directory }, stdout: "ignore", stderr: "ignore" });
			await checker.exited;
			const calls = (await Bun.file(argv).text()).split("\n").filter((line) => line.includes(linter));
			expect(calls.length).toBeGreaterThan(0);
			for (const call of calls) expect(call.startsWith(`--no-install ${linter} `)).toBe(true);
		} finally {
			await rm(directory, { recursive: true, force: true });
		}
	});
}
