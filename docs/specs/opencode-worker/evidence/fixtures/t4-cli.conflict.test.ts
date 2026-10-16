import { expect, test } from "bun:test";
import { getOptionInt, parseArgs } from "./cli.js";

const cfg = { options: ["days"] };

test("space-separated value is decimal", () => {
	expect(getOptionInt(parseArgs(["--days", "010"], cfg), "days")).toBe(10);
});

test("equals-separated value keeps legacy octal", () => {
	expect(getOptionInt(parseArgs(["--days=010"], cfg), "days")).toBe(8);
});
