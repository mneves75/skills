import { spawn } from "node:child_process";
import { runWithTimeout } from "./check-registry.js";

/** Run a quiet POSIX shell command with a deadline, escaping interpolated arguments. */
export function runCommand(timeoutMs = 60000) {
	return async (
		strings: TemplateStringsArray,
		...values: (string | number)[]
	) => {
		let script = strings.raw[0] ?? "";
		for (let i = 0; i < values.length; i++) {
			const quoted = `'${String(values[i]).replaceAll("'", "'\"'\"'")}'`;
			script += quoted + (strings.raw[i + 1] ?? "");
		}

		// A separate process group lets cancellation also stop pipelines and tool children.
		const child = spawn("/bin/sh", ["-c", script], {
			detached: true,
			stdio: ["ignore", "pipe", "pipe"],
		});
		const stdout: Buffer[] = [];
		const stderr: Buffer[] = [];
		child.stdout.on("data", (chunk: Buffer) => stdout.push(chunk));
		child.stderr.on("data", (chunk: Buffer) => stderr.push(chunk));
		const exited = new Promise<void>((resolve, reject) => {
			child.once("error", reject);
			child.once("close", () => resolve());
		});

		await runWithTimeout(exited, timeoutMs, async () => {
			if (child.pid !== undefined) {
				try {
					process.kill(-child.pid, "SIGKILL");
				} catch (error) {
					if (
						!(
							error instanceof Error &&
							"code" in error &&
							error.code === "ESRCH"
						)
					) {
						throw error;
					}
				}
			}
			// Detached daemons may retain pipe handles after the owned group has exited.
			child.stdout.destroy();
			child.stderr.destroy();
			await exited;
		});

		if (child.exitCode !== 0) {
			throw new Error(
				`Command failed (${child.signalCode ?? child.exitCode}): ${Buffer.concat(stderr).toString()}`,
			);
		}
		return { text: () => Buffer.concat(stdout).toString() };
	};
}
