import { spawn } from "node:child_process";
import { runWithTimeout } from "./check-registry.js";

const activeCommands = new Set<() => Promise<void>>();
let terminating = false;

/** Install once at the CLI boundary; repeated signals cannot interrupt cleanup. */
export function installCommandSignalHandlers(): void {
	const terminate = (exitCode: number) => {
		if (terminating) return;
		terminating = true;
		void Promise.all([...activeCommands].map((stop) => stop())).then(
			() => process.exit(exitCode),
			(error: unknown) => {
				console.error("readiness-check: Command cleanup failed:", error);
				process.exit(exitCode);
			},
		);
	};
	process.on("SIGINT", () => terminate(130));
	process.on("SIGTERM", () => terminate(143));
}

/** Run a quiet POSIX shell command with a deadline, escaping interpolated arguments. */
export function runCommand(timeoutMs = 60000) {
	return async (
		strings: TemplateStringsArray,
		...values: (string | number)[]
	) => {
		if (terminating) throw new Error("Checker is terminating");
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

		let stopped: Promise<void> | undefined;
		const stop = () => stopped ??= stopGroup();
		const stopGroup = async () => {
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
		};
		activeCommands.add(stop);

		try {
			await runWithTimeout(exited, timeoutMs, stop);
			if (child.exitCode !== 0) {
				throw new Error(
					`Command failed (${child.signalCode ?? child.exitCode}): ${Buffer.concat(stderr).toString()}`,
				);
			}
			return { text: () => Buffer.concat(stdout).toString() };
		} finally {
			try {
				await stop();
			} finally {
				activeCommands.delete(stop);
			}
		}
	};
}
