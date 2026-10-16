import { afterEach, expect, test } from "bun:test";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { runCommand } from "./command.js";

const directories: string[] = [];

afterEach(async () => {
	for (const directory of directories.splice(0)) {
		await rm(directory, { recursive: true, force: true });
	}
});

test("fast command preserves output and escapes interpolated arguments", async () => {
	const literal = "spaces ' quotes $(printf injected); `printf injected`";
	const output = await runCommand(1000)`printf '%s' ${literal}`;
	expect(output.text()).toBe(literal);
});

test("command failure still rejects", async () => {
	await expect(runCommand(1000)`exit 7`).rejects.toThrow();
});

test("pipelines and merged stderr preserve their output", async () => {
	const output = await runCommand(
		1000,
	)`(printf 'line\n'; printf 'error\n' >&2) 2>&1 | wc -l`;
	expect(output.text().trim()).toBe("2");
});

test("timeout kills shell descendants before they can finish work", async () => {
	const directory = await mkdtemp(join(tmpdir(), "readiness-command-"));
	directories.push(directory);
	const marker = join(directory, "finished");
	const pidFile = join(directory, "pid");
	const script = `
		import { writeFileSync } from "node:fs";
		writeFileSync(${JSON.stringify(pidFile)}, String(process.pid));
		process.on("SIGTERM", () => {});
		setTimeout(() => writeFileSync(${JSON.stringify(marker)}, "still running"), 600);
	`;
	let pid: number | undefined;
	try {
		await expect(
			runCommand(250)`${process.execPath} --eval ${script} & wait`,
		).rejects.toThrow("Timeout");
		const commandPid = Number(await Bun.file(pidFile).text());
		pid = commandPid;
		await Bun.sleep(700);
		expect(await Bun.file(marker).exists()).toBe(false);
		expect(() => process.kill(commandPid, 0)).toThrow();
	} finally {
		if (pid !== undefined) {
			killIfRunning(pid);
		}
	}
});

test("inherited pipes from a detached daemon cannot extend the deadline", async () => {
	const directory = await mkdtemp(join(tmpdir(), "readiness-daemon-"));
	directories.push(directory);
	const pidFile = join(directory, "pid");
	const daemon = 'setTimeout(() => console.log("done"), 1200)';
	const script = `
		import { spawn } from "node:child_process";
		import { writeFileSync } from "node:fs";
		const child = spawn(process.execPath, ["--eval", ${JSON.stringify(daemon)}], {
			detached: true, stdio: ["ignore", "inherit", "inherit"]
		});
		writeFileSync(${JSON.stringify(pidFile)}, String(child.pid));
		child.unref();
	`;
	const start = performance.now();
	try {
		await expect(
			runCommand(200)`${process.execPath} --eval ${script}`,
		).rejects.toThrow("Timeout");
		expect(performance.now() - start).toBeLessThan(800);
	} finally {
		if (await Bun.file(pidFile).exists()) {
			killIfRunning(Number(await Bun.file(pidFile).text()));
		}
	}
});

function killIfRunning(pid: number): void {
	try {
		process.kill(pid, "SIGKILL");
	} catch (error) {
		if (
			!(error instanceof Error && "code" in error && error.code === "ESRCH")
		) {
			throw error;
		}
	}
}
