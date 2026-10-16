import { afterEach, expect, test } from "bun:test";
import { mkdtemp, rm } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { parseCargoToml } from "./cargo-toml.js";

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
	const directory = await mkdtemp(join(tmpdir(), "readiness-cargo-"));
	directories.push(directory);
	const filepath = join(directory, "Cargo.toml");
	await Bun.write(filepath, content);
	return parseCargoToml(filepath);
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
		`[[${path}.${marker}]]\nvalue = "polluted"`,
		`[dependencies]\npackage = { ${path} = "polluted" }`,
	]) {
		test(`rejects unsafe Cargo path in ${content.split("\n")[0]}`, async () => {
			const result = await parse(content);
			expect(Reflect.get({}, marker)).toBeUndefined();
			expect(Reflect.get(Object, marker)).toBeUndefined();
			expect(result).toBeNull();
		});
	}
}

test("preserves Cargo dotted keys, nested dependencies and inline tables", async () => {
	const result = await parse(`
package.name = "safe-project"
package.version = "1.0.0"
[dependencies]
serde = { version = "1.0", features = ["derive"] }
toString = "2.0"
[dependencies.tokio]
version = "1.0"
optional = true
[dev-dependencies]
proptest = "1.0"
[[bin]]
name = "safe-project"
`);
	expect(result).toMatchObject({
		name: "safe-project",
		version: "1.0.0",
		dependencies: [
			{ name: "serde", version: "1.0" },
			{ name: "toString", version: "2.0" },
			{ name: "tokio", version: "1.0", optional: true },
		],
		devDependencies: [
			{ name: "proptest", version: "1.0", type: "development" },
		],
	});
	expect(Reflect.get({}, marker)).toBeUndefined();
});
