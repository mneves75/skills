import { describe, expect, test } from "bun:test";
import { getOptionInt, parseArgs } from "./cli.js";

const cfg = { flags: ["verbose", "v"], options: ["offset", "n", "ratio", "days"] };
const intOf = (value: string, def = -999) =>
	getOptionInt(parseArgs([`--days=${value}`], cfg), "days", undefined, def);

describe("hidden: getOptionInt strict", () => {
	test("accepts plain, padded, signed integers", () => {
		expect(intOf("12")).toBe(12);
		expect(intOf(" 7 ")).toBe(7);
		expect(intOf("+3")).toBe(3);
		expect(intOf("-3")).toBe(-3);
	});
	test("rejects partial, exponent, decimal, empty, unsafe", () => {
		expect(intOf("12abc")).toBe(-999);
		expect(intOf("1e3")).toBe(-999);
		expect(intOf("3.5")).toBe(-999);
		expect(intOf("")).toBe(-999);
		expect(intOf("99999999999999999999")).toBe(-999);
	});
	test("missing option returns default", () => {
		expect(getOptionInt(parseArgs([], cfg), "days", undefined, 5)).toBe(5);
	});
	test("existing caller shape: no default means 0", () => {
		expect(getOptionInt(parseArgs(["--days=abc"], cfg), "days")).toBe(0);
	});
});

describe("hidden: negative-number values", () => {
	test("long option consumes negative integer", () => {
		expect(parseArgs(["--offset", "-5"], cfg).options.get("offset")).toBe("-5");
	});
	test("short option consumes negative integer", () => {
		expect(parseArgs(["-n", "-3"], cfg).options.get("n")).toBe("-3");
	});
	test("negative decimal consumed", () => {
		expect(parseArgs(["--ratio", "-0.5"], cfg).options.get("ratio")).toBe("-0.5");
	});
	test("a following flag is not consumed", () => {
		const a = parseArgs(["--offset", "-v"], cfg);
		expect(a.options.has("offset")).toBe(false);
		expect(a.flags.has("v")).toBe(true);
	});
	test("a following long flag is not consumed", () => {
		const a = parseArgs(["--offset", "--verbose"], cfg);
		expect(a.options.has("offset")).toBe(false);
		expect(a.flags.has("verbose")).toBe(true);
	});
	test("= form still works with negatives", () => {
		expect(parseArgs(["--offset=-5"], cfg).options.get("offset")).toBe("-5");
	});
	test("end to end", () => {
		expect(getOptionInt(parseArgs(["--offset", "-5"], cfg), "offset")).toBe(-5);
	});
});
