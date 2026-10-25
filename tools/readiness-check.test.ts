import { expect, test } from "bun:test";
import { chmod, mkdir, mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";

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
		for (const flag of ["--min-level=L5", "--min-level=0", "--min-level=6", "--min-level=3x", "--scoring=bogus", "--format=bogus", "--language=cobol"]) {
			const { code, stderr } = await run(flag);
			expect({ flag, code }).toEqual({ flag, code: 2 });
			expect(stderr).toContain(flag.slice(2, flag.indexOf("=")));
		}
	} finally {
		await rm(directory, { recursive: true, force: true });
	}
}, 60000);
