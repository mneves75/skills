import { expect, test } from "bun:test";
import { runWithTimeout } from "./check-registry.js";

test("timeout kills its subprocess and awaits exit before rejecting", async () => {
	const child = Bun.spawn(
		[
			process.execPath,
			"-e",
			'console.log("ready"); setInterval(() => {}, 1000)',
		],
		{
			stdout: "pipe",
			stderr: "pipe",
		},
	);
	try {
		const reader = child.stdout.getReader();
		await reader.read();
		reader.releaseLock();
		await expect(
			runWithTimeout(child.exited, 20, async () => {
				child.kill("SIGKILL");
				await child.exited;
			}),
		).rejects.toThrow("Timeout");
		expect(child.signalCode).toBe("SIGKILL");
	} finally {
		child.kill("SIGKILL");
		await child.exited;
	}
});

test("fast work returns its output without cancellation", async () => {
	let cancelled = false;
	expect(
		await runWithTimeout(Promise.resolve("command output"), 1000, async () => {
			cancelled = true;
		}),
	).toBe("command output");
	expect(cancelled).toBe(false);
});

for (const outcome of [
	'Promise.resolve("output")',
	'Promise.reject(new Error("failed"))',
]) {
	test(`settled work clears its deadline timer: ${outcome}`, async () => {
		const script = `
			import { runWithTimeout } from ${JSON.stringify(new URL("./check-registry.ts", import.meta.url).pathname)};
			try { await runWithTimeout(${outcome}, 60000, async () => {}); } catch {}
			console.log("settled");
		`;
		const child = Bun.spawn([process.execPath, "--eval", script], {
			stdout: "pipe",
			stderr: "pipe",
		});
		let guard: ReturnType<typeof setTimeout> | undefined;
		try {
			const reader = child.stdout.getReader();
			await reader.read();
			reader.releaseLock();
			const exitCode = await Promise.race([
				child.exited,
				new Promise<null>((resolve) => {
					guard = setTimeout(() => resolve(null), 500);
				}),
			]);
			expect(exitCode).toBe(0);
		} finally {
			clearTimeout(guard);
			child.kill("SIGKILL");
			await child.exited;
		}
	});
}
