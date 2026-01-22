/**
 * @fileoverview Progress indicators for CLI operations
 * @module kb-tools/progress
 *
 * @description
 * Provides progress bars and spinners for long-running operations.
 * Handles non-TTY environments gracefully.
 *
 * @example
 * ```typescript
 * // Progress bar for known count
 * const bar = new ProgressBar(100, { label: "Processing" });
 * for (let i = 0; i < 100; i++) {
 *   await processItem(i);
 *   bar.increment();
 * }
 *
 * // Spinner for indeterminate operations
 * const spin = spinner("Fetching data...");
 * await fetchData();
 * spin.stop("Done!");
 * ```
 */

/** Check if stdout is a TTY */
const isTTY = process.stdout.isTTY ?? false;

/** Progress bar options */
export interface ProgressBarOptions {
	/** Width of the progress bar in characters */
	width?: number;
	/** Label shown before the bar */
	label?: string;
	/** Show percentage */
	showPercent?: boolean;
	/** Show count (current/total) */
	showCount?: boolean;
}

/**
 * Terminal progress bar for operations with known count.
 *
 * @example
 * ```typescript
 * const bar = new ProgressBar(files.length, { label: "Copying" });
 * for (const file of files) {
 *   await copyFile(file);
 *   bar.increment();
 * }
 * bar.complete();
 * ```
 */
export class ProgressBar {
	private current = 0;
	private readonly total: number;
	private readonly width: number;
	private readonly label: string;
	private readonly showPercent: boolean;
	private readonly showCount: boolean;
	private lastRender = 0;
	private readonly throttleMs = 50;

	constructor(total: number, options: ProgressBarOptions = {}) {
		this.total = Math.max(1, total);
		this.width = options.width ?? 30;
		this.label = options.label ?? "Progress";
		this.showPercent = options.showPercent ?? true;
		this.showCount = options.showCount ?? true;
	}

	/**
	 * Updates progress to specific value.
	 *
	 * @param value - New progress value
	 */
	update(value: number): void {
		this.current = Math.min(value, this.total);
		this.render();
	}

	/**
	 * Increments progress by one.
	 */
	increment(): void {
		this.update(this.current + 1);
	}

	/**
	 * Marks progress as complete.
	 */
	complete(): void {
		this.update(this.total);
		if (isTTY) {
			process.stdout.write("\n");
		}
	}

	private render(): void {
		// Throttle renders
		const now = Date.now();
		if (now - this.lastRender < this.throttleMs && this.current < this.total) {
			return;
		}
		this.lastRender = now;

		if (!isTTY) {
			// Non-TTY: just log milestones
			const percent = Math.floor((this.current / this.total) * 100);
			if (percent % 25 === 0 || this.current === this.total) {
				console.log(`${this.label}: ${percent}%`);
			}
			return;
		}

		const percent = Math.min(
			100,
			Math.round((this.current / this.total) * 100),
		);
		const filled = Math.round((percent / 100) * this.width);
		const empty = this.width - filled;

		const bar = "\u2588".repeat(filled) + "\u2591".repeat(empty);

		const parts: string[] = [`${this.label}: [${bar}]`];
		if (this.showPercent) {
			parts.push(`${percent}%`);
		}
		if (this.showCount) {
			parts.push(`(${this.current}/${this.total})`);
		}

		const line = `\r${parts.join(" ")}`;
		process.stdout.write(line);
	}
}

/** Spinner control interface */
export interface SpinnerControl {
	/** Stops the spinner with optional final message */
	stop: (message?: string) => void;
	/** Updates the spinner text */
	update: (text: string) => void;
}

/** Spinner frame characters */
const SPINNER_FRAMES = [
	"\u280B",
	"\u2819",
	"\u2839",
	"\u2838",
	"\u283C",
	"\u2834",
	"\u2826",
	"\u2827",
	"\u2807",
	"\u280F",
];

/**
 * Creates a terminal spinner for indeterminate operations.
 *
 * @param label - Text to show next to spinner
 * @returns Spinner control object
 *
 * @example
 * ```typescript
 * const spin = spinner("Downloading...");
 * await download();
 * spin.stop("Downloaded!");
 * ```
 */
export function spinner(label: string): SpinnerControl {
	let i = 0;
	let currentLabel = label;
	let stopped = false;

	const interval = isTTY
		? setInterval(() => {
				if (stopped) return;
				const frameCount = SPINNER_FRAMES.length;
				const frame =
					frameCount > 0 ? (SPINNER_FRAMES[i % frameCount] ?? "") : "";
				i += 1;
				process.stdout.write(`\r${frame} ${currentLabel}`);
			}, 80)
		: null;

	if (!isTTY) {
		console.log(`... ${label}`);
	}

	return {
		stop: (message?: string) => {
			stopped = true;
			if (interval) {
				clearInterval(interval);
			}
			if (isTTY) {
				// Clear the line
				process.stdout.write(`\r${" ".repeat(currentLabel.length + 3)}\r`);
				if (message) {
					console.log(message);
				}
			} else if (message) {
				console.log(message);
			}
		},
		update: (text: string) => {
			currentLabel = text;
			if (!isTTY) {
				console.log(`... ${text}`);
			}
		},
	};
}

/**
 * Simple status line that can be updated.
 *
 * @param initial - Initial text
 * @returns Control object with update and done methods
 */
export function statusLine(initial: string): {
	update: (text: string) => void;
	done: (text?: string) => void;
} {
	let lastLen = 0;

	const update = (text: string): void => {
		if (isTTY) {
			const clearPart = " ".repeat(Math.max(0, lastLen - text.length));
			process.stdout.write(`\r${text}${clearPart}`);
			lastLen = text.length;
		} else {
			console.log(text);
		}
	};

	const done = (text?: string): void => {
		if (isTTY) {
			if (text) {
				const clearPart = " ".repeat(Math.max(0, lastLen - text.length));
				process.stdout.write(`\r${text}${clearPart}\n`);
			} else {
				process.stdout.write("\n");
			}
		} else if (text) {
			console.log(text);
		}
	};

	update(initial);

	return { update, done };
}

/**
 * Formats a duration in milliseconds to human-readable string.
 *
 * @param ms - Duration in milliseconds
 * @returns Formatted string like "1.2s" or "45ms"
 */
export function formatDuration(ms: number): string {
	if (ms < 1000) {
		return `${Math.round(ms)}ms`;
	}
	if (ms < 60000) {
		return `${(ms / 1000).toFixed(1)}s`;
	}
	const minutes = Math.floor(ms / 60000);
	const seconds = ((ms % 60000) / 1000).toFixed(0);
	return `${minutes}m ${seconds}s`;
}
