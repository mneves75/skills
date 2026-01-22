/**
 * @fileoverview CLI argument parsing and help generation utilities
 * @module kb-tools/cli
 *
 * @description
 * Provides a minimal, dependency-free CLI argument parser.
 * Supports flags, options with values, and positional arguments.
 *
 * @example
 * ```typescript
 * const args = parseArgs(process.argv.slice(2), {
 *   flags: ["verbose", "v", "help", "h"],
 *   options: ["output", "o", "days", "d"],
 * });
 *
 * if (args.flags.has("help") || args.flags.has("h")) {
 *   showHelp();
 *   process.exit(0);
 * }
 *
 * const verbose = args.flags.has("verbose") || args.flags.has("v");
 * const output = args.options.get("output") || args.options.get("o");
 * ```
 */

/** Configuration for argument parser */
export interface ArgConfig {
	/** Flag arguments (no value, boolean) */
	flags?: string[];
	/** Option arguments (with value) */
	options?: string[];
	/** Positional argument names (for validation/help) */
	positional?: string[];
}

/** Parsed arguments result */
export interface ParsedArgs {
	/** Set of flag names that were present */
	flags: Set<string>;
	/** Map of option names to their values */
	options: Map<string, string>;
	/** Positional arguments in order */
	positional: string[];
	/** Any unknown arguments */
	unknown: string[];
}

/**
 * Parses command line arguments.
 *
 * @param argv - Arguments to parse (typically process.argv.slice(2))
 * @param config - Configuration specifying which args are flags vs options
 * @returns Parsed arguments object
 *
 * @example
 * ```typescript
 * // Input: ["--verbose", "--output", "file.txt", "input.md"]
 * const args = parseArgs(argv, {
 *   flags: ["verbose"],
 *   options: ["output"],
 * });
 * // args.flags = Set { "verbose" }
 * // args.options = Map { "output" => "file.txt" }
 * // args.positional = ["input.md"]
 * ```
 */
export function parseArgs(argv: string[], config: ArgConfig = {}): ParsedArgs {
	const flagSet = new Set(config.flags ?? []);
	const optionSet = new Set(config.options ?? []);
	const hasConfig = flagSet.size > 0 || optionSet.size > 0;

	const result: ParsedArgs = {
		flags: new Set(),
		options: new Map(),
		positional: [],
		unknown: [],
	};

	let i = 0;
	let stopParsing = false; // After --, treat everything as positional

	while (i < argv.length) {
		const arg = argv[i];
		if (arg === undefined) {
			i++;
			continue;
		}

		// Handle -- separator (POSIX: everything after is positional)
		if (arg === "--" && !stopParsing) {
			stopParsing = true;
			i++;
			continue;
		}

		// After --, everything is positional
		if (stopParsing) {
			result.positional.push(arg);
			i++;
			continue;
		}

		// If no config provided, treat everything as positional
		if (!hasConfig) {
			result.positional.push(arg);
			i++;
			continue;
		}

		if (arg.startsWith("--")) {
			const name = arg.slice(2);

			// Handle --option=value syntax
			if (name.includes("=")) {
				const parts = name.split("=", 2);
				const optName = parts[0] ?? "";
				const optValue = parts[1] ?? "";
				if (optionSet.has(optName)) {
					result.options.set(optName, optValue);
				} else {
					result.unknown.push(arg);
				}
				i++;
				continue;
			}

			if (flagSet.has(name)) {
				result.flags.add(name);
			} else if (optionSet.has(name)) {
				// Next arg is the value
				const nextArg = argv[i + 1];
				if (nextArg !== undefined && !nextArg.startsWith("-")) {
					result.options.set(name, nextArg);
					i++;
				}
			} else {
				result.unknown.push(arg);
			}
		} else if (arg.startsWith("-") && arg.length > 1) {
			const name = arg.slice(1);

			// Handle -o=value syntax
			if (name.includes("=")) {
				const parts = name.split("=", 2);
				const optName = parts[0] ?? "";
				const optValue = parts[1] ?? "";
				if (optionSet.has(optName)) {
					result.options.set(optName, optValue);
				} else {
					result.unknown.push(arg);
				}
				i++;
				continue;
			}

			if (flagSet.has(name)) {
				result.flags.add(name);
			} else if (optionSet.has(name)) {
				// Next arg is the value
				const nextArg = argv[i + 1];
				if (nextArg !== undefined && !nextArg.startsWith("-")) {
					result.options.set(name, nextArg);
					i++;
				}
			} else {
				// Could be combined short flags like -vf
				let allFlags = true;
				for (const char of name) {
					if (!flagSet.has(char)) {
						allFlags = false;
						break;
					}
				}
				if (allFlags) {
					for (const char of name) {
						result.flags.add(char);
					}
				} else {
					result.unknown.push(arg);
				}
			}
		} else {
			result.positional.push(arg);
		}

		i++;
	}

	return result;
}

/**
 * Checks if help flag is present.
 *
 * @param args - Parsed arguments
 * @returns True if --help or -h is present
 */
export function hasHelpFlag(args: ParsedArgs): boolean {
	return args.flags.has("help") || args.flags.has("h");
}

/**
 * Gets an option value with fallback.
 *
 * @param args - Parsed arguments
 * @param long - Long option name
 * @param short - Short option name (optional)
 * @param defaultValue - Default value if not found
 * @returns The option value or default
 */
export function getOption(
	args: ParsedArgs,
	long: string,
	short?: string,
	defaultValue?: string,
): string | undefined {
	return (
		args.options.get(long) ??
		(short ? args.options.get(short) : undefined) ??
		defaultValue
	);
}

/**
 * Gets an option value as integer.
 *
 * @param args - Parsed arguments
 * @param long - Long option name
 * @param short - Short option name (optional)
 * @param defaultValue - Default value if not found or invalid
 * @returns The option value as integer or default
 */
export function getOptionInt(
	args: ParsedArgs,
	long: string,
	short?: string,
	defaultValue = 0,
): number {
	const value = getOption(args, long, short);
	if (value === undefined) return defaultValue;
	const parsed = Number.parseInt(value, 10);
	return Number.isNaN(parsed) ? defaultValue : parsed;
}

/**
 * Checks if a flag is present.
 *
 * @param args - Parsed arguments
 * @param long - Long flag name
 * @param short - Short flag name (optional)
 * @returns True if flag is present
 */
export function hasFlag(
	args: ParsedArgs,
	long: string,
	short?: string,
): boolean {
	return args.flags.has(long) || (short ? args.flags.has(short) : false);
}

/** Help text option definition */
export interface HelpOption {
	/** Long flag name (without --) */
	long: string;
	/** Short flag name (without -) */
	short?: string;
	/** Description of the option */
	description: string;
	/** Argument placeholder for options with values */
	arg?: string;
}

/** Help text configuration */
export interface HelpConfig {
	/** Tool name */
	name: string;
	/** Tool description */
	description: string;
	/** Usage examples */
	usage?: string[];
	/** Option definitions */
	options?: HelpOption[];
	/** Example commands */
	examples?: { command: string; description: string }[];
}

/**
 * Generates formatted help text.
 *
 * @param config - Help configuration
 * @returns Formatted help string
 *
 * @example
 * ```typescript
 * console.log(generateHelp({
 *   name: "kb-check-all",
 *   description: "Run all validation checks",
 *   options: [
 *     { long: "verbose", short: "v", description: "Show detailed output" },
 *     { long: "output", short: "o", description: "Output file", arg: "FILE" },
 *   ],
 * }));
 * ```
 */
export function generateHelp(config: HelpConfig): string {
	const lines: string[] = [];

	lines.push(`${config.name}: ${config.description}`);
	lines.push("");

	// Usage
	lines.push("Usage:");
	if (config.usage && config.usage.length > 0) {
		for (const usage of config.usage) {
			lines.push(`  ${usage}`);
		}
	} else {
		lines.push(`  bun tools/${config.name}.ts [options]`);
	}
	lines.push("");

	// Options
	if (config.options && config.options.length > 0) {
		lines.push("Options:");

		// Calculate max width for alignment
		let maxWidth = 0;
		for (const opt of config.options) {
			const width =
				(opt.short ? `-${opt.short}, ` : "    ").length +
				`--${opt.long}`.length +
				(opt.arg ? ` ${opt.arg}`.length : 0);
			maxWidth = Math.max(maxWidth, width);
		}

		for (const opt of config.options) {
			const shortPart = opt.short ? `-${opt.short}, ` : "    ";
			const longPart = `--${opt.long}${opt.arg ? ` ${opt.arg}` : ""}`;
			const padding = " ".repeat(
				maxWidth - shortPart.length - longPart.length + 2,
			);
			lines.push(`  ${shortPart}${longPart}${padding}${opt.description}`);
		}
		lines.push("");
	}

	// Examples
	if (config.examples && config.examples.length > 0) {
		lines.push("Examples:");
		for (const example of config.examples) {
			lines.push(`  ${example.command}`);
			lines.push(`      ${example.description}`);
		}
		lines.push("");
	}

	return lines.join("\n");
}
