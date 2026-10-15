import { describe, expect, test } from "bun:test";
import { parseArgs } from "./cli.js";

const cfg = { flags: ["verbose", "v", "f"], options: ["output", "o"] };

describe("hidden: = handling", () => {
	test("long option keeps all '=' in value", () => {
		expect(parseArgs(["--output=a=b=c"], cfg).options.get("output")).toBe("a=b=c");
	});
	test("short option keeps all '=' in value", () => {
		expect(parseArgs(["-o=x=y"], cfg).options.get("o")).toBe("x=y");
	});
	test("empty value after = stays empty", () => {
		expect(parseArgs(["--output="], cfg).options.get("output")).toBe("");
	});
	test("plain value unchanged", () => {
		expect(parseArgs(["--output=plain"], cfg).options.get("output")).toBe("plain");
	});
	test("unknown option with = goes to unknown verbatim", () => {
		const a = parseArgs(["--nope=a=b"], cfg);
		expect(a.unknown).toEqual(["--nope=a=b"]);
		expect(a.options.size).toBe(0);
	});
	test("space-separated value and flags unchanged", () => {
		const a = parseArgs(["-vf", "--output", "f.txt", "pos"], cfg);
		expect([...a.flags].sort()).toEqual(["f", "v"]);
		expect(a.options.get("output")).toBe("f.txt");
		expect(a.positional).toEqual(["pos"]);
	});
});
