import { expect, test } from "bun:test";
import { chmod, mkdir, mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import type { CheckContext, LanguageAdapter } from "../check-registry.js";
import { createFileCache } from "../file-cache.js";
import { goAdapter } from "./go.js";
import { pythonAdapter } from "./python.js";
import { rustAdapter } from "./rust.js";
import { typescriptAdapter } from "./typescript.js";

const cases: {
	adapter: LanguageAdapter;
	check: string;
	file: string;
	line: string;
}[] = [
	{
		adapter: typescriptAdapter,
		check: "no-lint-ignores",
		file: "src/a.ts",
		line: "// eslint-disable-next-line no-console",
	},
	{
		adapter: typescriptAdapter,
		check: "no-lint-ignores",
		file: "src/b.tsx",
		line: "// biome-ignore lint/style: reason",
	},
	{
		adapter: goAdapter,
		check: "no-lint-ignores",
		file: "pkg/a.go",
		line: "x := 1 //nolint:errcheck",
	},
	{
		adapter: goAdapter,
		check: "no-unsafe-types",
		file: "pkg/a.go",
		line: "p := unsafe.Pointer(&x)",
	},
	{
		adapter: pythonAdapter,
		check: "no-lint-ignores",
		file: "app/a.py",
		line: "import os  # noqa: F401",
	},
	{
		adapter: pythonAdapter,
		check: "no-lint-ignores",
		file: "app/b.py",
		line: "x = f()  # type: ignore[attr-defined]",
	},
];

async function run(
	adapter: LanguageAdapter,
	check: string,
	files: Record<string, string>,
	unreadable: string[] = [],
) {
	const directory = await mkdtemp(join(tmpdir(), "readiness-suppress-"));
	try {
		for (const [file, body] of Object.entries(files)) {
			await mkdir(join(directory, dirname(file)), { recursive: true });
			await Bun.write(join(directory, file), body);
		}
		for (const file of unreadable) await chmod(join(directory, file), 0o000);
		const ctx: CheckContext = {
			app: {
				id: ".",
				name: "fixture",
				path: directory,
				relativePath: ".",
				type: "app",
				language: adapter.language,
				manifest: "package.json",
				manifestPath: join(directory, "package.json"),
				isRoot: true,
			},
			repoRoot: directory,
			options: { timeout: 10000 },
			cache: createFileCache(),
		};
		const runner = adapter.getRunner(check);
		if (!runner)
			throw new Error(`${adapter.language} has no runner for ${check}`);
		return await runner(ctx);
	} finally {
		await rm(directory, { recursive: true, force: true });
	}
}

for (const { adapter, check, file, line } of cases) {
	const many = `${Array.from({ length: 12 }, () => line).join("\n")}\n`;
	test(`${adapter.language} ${check}: counts ${JSON.stringify(line)}`, async () => {
		const dirty = await run(adapter, check, { [file]: many });
		expect(dirty.pass).toBe(false);
		expect(dirty.details).toContain("12");
		expect((await run(adapter, check, { [file]: "clean\n" })).pass).toBe(true);
		// Vendored and generated trees are not the project's own suppressions.
		for (const vendored of ["node_modules", "vendor", ".venv", "dist"]) {
			expect(
				(await run(adapter, check, { [join(vendored, file)]: many })).pass,
			).toBe(true);
		}
	});
}

const taskRunners: { adapter: LanguageAdapter; file: string; body: string }[] = [
	{ adapter: goAdapter, file: "Makefile", body: "build:\n\tgo build ./...\n" },
	{ adapter: goAdapter, file: "Taskfile.yml", body: "version: '3'\ntasks:\n  test:\n    cmds: [go test ./...]\n" },
	{ adapter: goAdapter, file: "justfile", body: "test:\n  go test ./...\n" },
	{ adapter: pythonAdapter, file: "Makefile", body: "test:\n\tpytest\n" },
	{ adapter: pythonAdapter, file: "noxfile.py", body: "import nox\n" },
	{ adapter: pythonAdapter, file: "tox.ini", body: "[tox]\nenv_list = py312\n" },
	{ adapter: pythonAdapter, file: "pyproject.toml", body: "[tool.poe.tasks]\ntest = 'pytest'\n" },
];

for (const { adapter, file, body } of taskRunners) {
	test(`${adapter.language} npm-scripts: finds tasks in ${file}`, async () => {
		const found = await run(adapter, "npm-scripts", { [file]: body });
		expect(found).toMatchObject({ pass: true });
		expect(found.skipped).toBeUndefined();
	});
}

for (const adapter of [goAdapter, pythonAdapter]) {
	test(`${adapter.language} npm-scripts: fails without a task runner`, async () => {
		const missing = await run(adapter, "npm-scripts", { "README.md": "# x\n", "Makefile": "# no targets\n" });
		expect(missing).toMatchObject({ pass: false });
	});
}

test("an unreadable source file is skipped, not a failed check", async () => {
	const result = await run(typescriptAdapter, "no-lint-ignores", { "src/a.ts": "clean\n", "src/locked.ts": "// eslint-disable\n" }, ["src/locked.ts"]);
	expect(result).toMatchObject({ pass: true, details: "0 lint suppression comments" });
});

for (const adapter of [goAdapter, pythonAdapter, rustAdapter]) {
	test(`${adapter.language} npm-scripts: reads Makefile targets, not variables`, async () => {
		const variablesOnly = await run(adapter, "npm-scripts", { Makefile: "CC:=gcc\nCFLAGS ::= -O2\n" });
		expect(variablesOnly).toMatchObject({ pass: false });
		const targets = await run(adapter, "npm-scripts", { Makefile: "py312:\n\ttox\nlint.fix:\n\truff\n" });
		expect(targets).toMatchObject({ pass: true, details: "2 Makefile targets" });
	});
}

const literals: { adapter: LanguageAdapter; file: string; line: string }[] = [
	{ adapter: typescriptAdapter, file: "test/a.test.ts", line: 'const fixture = "// eslint-disable-next-line no-console";' },
	{ adapter: typescriptAdapter, file: "test/b.test.ts", line: "write(`/* biome-ignore lint: x */`);" },
	{ adapter: goAdapter, file: "pkg/a_test.go", line: 'src := "x := 1 //nolint:errcheck"' },
	{ adapter: pythonAdapter, file: "tests/test_a.py", line: 'SAMPLE = "import os  # noqa: F401"' },
];

for (const { adapter, file, line } of literals) {
	test(`${adapter.language} no-lint-ignores: ${JSON.stringify(line)} is a string, not a suppression`, async () => {
		const body = `${Array.from({ length: 12 }, () => line).join("\n")}\n`;
		expect(await run(adapter, "no-lint-ignores", { [file]: body })).toMatchObject({ pass: true });
	});
}

test("python no-lint-ignores: apostrophes in a comment do not hide its directive", async () => {
	const line = "x = f()  # don't do this  # type: ignore  # it won't";
	const body = `${Array.from({ length: 12 }, () => line).join("\n")}\n`;
	expect(await run(pythonAdapter, "no-lint-ignores", { "app/a.py": body })).toMatchObject({ pass: false });
});

test("typescript no-lint-ignores: a JSDoc-style block suppression counts", async () => {
	const body = `${Array.from({ length: 12 }, () => "/** eslint-disable no-console */").join("\n")}\n`;
	expect(await run(typescriptAdapter, "no-lint-ignores", { "src/a.ts": body })).toMatchObject({ pass: false });
});

test("npm-scripts: pattern and variable rules are targets", async () => {
	const rules = "%.o: %.c\n\tcc -c $<\n$(BIN): $(OBJS)\n\tcc -o $@ $^\n";
	expect(await run(goAdapter, "npm-scripts", { Makefile: rules })).toMatchObject({ pass: true, details: "2 Makefile targets" });
});

test("npm-scripts: a GNU ::= or :::= assignment is not a target; a multi-target line is", async () => {
	expect(await run(goAdapter, "npm-scripts", { Makefile: "A:::=b\nB ::= c\n" })).toMatchObject({ pass: false });
	expect(await run(goAdapter, "npm-scripts", { Makefile: "build test: deps\n\tgo test\n" })).toMatchObject({ pass: true, details: "1 Makefile targets" });
});

test("npm-scripts: a long non-rule line does not stall Makefile scanning", async () => {
	const directory = await mkdtemp(join(tmpdir(), "readiness-makefile-"));
	try {
		await Bun.write(join(directory, "Makefile"), `A${" ".repeat(100_000)}\nbuild:\n\tgo build\n`);
		const child = Bun.spawn([process.execPath, "--eval", "import { findTaskRunner } from './lib/adapters/base.ts'; console.log(JSON.stringify(await findTaskRunner(process.argv[1])))", directory], {
			cwd: join(import.meta.dir, "../.."),
			stdout: "pipe",
			stderr: "pipe",
			timeout: 3_000,
		});
		expect(await child.exited).toBe(0);
		expect(JSON.parse(await new Response(child.stdout).text())).toMatchObject({ pass: true, details: "1 Makefile targets" });
	} finally {
		await rm(directory, { recursive: true, force: true });
	}
});
