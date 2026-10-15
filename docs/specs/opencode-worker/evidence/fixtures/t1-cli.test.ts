import { describe, expect, test } from "bun:test";
import { parseArgs } from "./cli.js";

describe("parseArgs --name=value", () => {
	test("keeps every '=' after the first in a long option value", () => {
		const args = parseArgs(["--output=a=b.txt"], { options: ["output"] });
		expect(args.options.get("output")).toBe("a=b.txt");
	});
});
