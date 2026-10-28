import { afterEach, expect, test } from "bun:test";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { parsePyProject } from "./pyproject.js";

const directories: string[] = [];
const marker = "readinessPollutionMarker";

afterEach(async () => {
	Reflect.deleteProperty(Object.prototype, marker);
	Reflect.deleteProperty(Object, marker);
	for (const directory of directories.splice(0)) {
		await rm(directory, { recursive: true, force: true });
	}
});

async function parse(content: string) {
	const directory = await mkdtemp(join(tmpdir(), "readiness-pyproject-"));
	directories.push(directory);
	const filepath = join(directory, "pyproject.toml");
	await Bun.write(filepath, content);
	return parsePyProject(filepath);
}

for (const path of [
	"__proto__",
	"constructor.prototype",
	"constructor",
	"prototype",
]) {
	for (const content of [
		`[${path}]\n${marker} = "polluted"`,
		`${path}.${marker} = "polluted"`,
		`[tool.poetry.dependencies]\npackage = { ${path} = "polluted" }`,
	]) {
		test(`rejects unsafe pyproject path in ${content.split("\n")[0]}`, async () => {
			const result = await parse(content);
			expect(Reflect.get({}, marker)).toBeUndefined();
			expect(Reflect.get(Object, marker)).toBeUndefined();
			expect(result).toBeNull();
		});
	}
}

test("preserves Poetry dotted keys, nested dependencies and inline tables", async () => {
	const result = await parse(`
tool.poetry.name = "safe-project"
tool.poetry.version = "1.0.0"
[tool.poetry.dependencies]
python = "^3.10"
requests = "^2.0"
rich = { version = "^13.0", optional = true }
[tool.poetry.dependencies.httpx]
version = "^0.27"
[tool.poetry.group.dev.dependencies]
pytest = "^8.0"
`);
	expect(result).toMatchObject({
		type: "python-poetry",
		name: "safe-project",
		version: "1.0.0",
		dependencies: [
			{ name: "requests", version: "^2.0" },
			{ name: "rich", version: "^13.0", optional: true },
			{ name: "httpx", version: "^0.27" },
		],
		devDependencies: [{ name: "pytest", version: "^8.0", type: "development" }],
	});
	expect(Reflect.get({}, marker)).toBeUndefined();
});

test("preserves PEP 621 dependencies and optional development dependencies", async () => {
	const result = await parse(`
project.name = "safe-project"
[project]
dependencies = ["requests>=2.0"]
[project.optional-dependencies]
test = ["pytest>=8.0"]
`);
	expect(result).toMatchObject({
		type: "python-pyproject",
		name: "safe-project",
		dependencies: [{ name: "requests", version: ">=2.0" }],
		devDependencies: [
			{ name: "pytest", version: ">=8.0", type: "development" },
		],
	});
});

test("a long run of brackets in a section header parses in linear time", async () => {
	// The header pattern's inner class overlapped `\[+`, so this input backtracked quadratically.
	const started = performance.now();
	await parse(`${"[".repeat(100_000)}x\n[project]\nname = "a"\n`);
	expect(performance.now() - started).toBeLessThan(1000);
});
