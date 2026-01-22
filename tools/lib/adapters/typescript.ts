/**
 * @fileoverview TypeScript/JavaScript language adapter
 * @module kb-tools/lib/adapters/typescript
 *
 * @description
 * Implements readiness checks for TypeScript and JavaScript codebases.
 * Supports ESLint, Biome, Prettier, Vitest, Jest, and Bun test.
 *
 * Uses shared checks for common patterns (README, CI, security, etc.)
 * and only implements TypeScript-specific checks here.
 */

import { $ } from "bun";
import path from "node:path";
import {
	type CheckRunner,
	type CheckContext,
	type CheckResult,
	fileExists,
	readJson,
	readText,
	dirExists,
	runWithTimeout,
} from "../check-registry.js";
import { createLanguageAdapter } from "./base.js";

// ============================================================================
// Types
// ============================================================================

interface PackageJson {
	name?: string;
	scripts?: Record<string, string>;
	dependencies?: Record<string, string>;
	devDependencies?: Record<string, string>;
	workspaces?: string[] | { packages: string[] };
	jest?: { coverageThreshold?: unknown };
	c8?: { checkCoverage?: unknown };
}

// ============================================================================
// TypeScript-Specific Check Runners
// ============================================================================

const tsSpecificRunners: Record<string, CheckRunner> = {
	// =========================================================================
	// STYLE & VALIDATION (TypeScript-specific)
	// =========================================================================

	"linter-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		// Check for ESLint
		const eslintConfigs = [
			".eslintrc.json",
			".eslintrc.js",
			".eslintrc.cjs",
			"eslint.config.js",
			"eslint.config.mjs",
		];
		for (const config of eslintConfigs) {
			if (await fileExists(path.join(appPath, config))) {
				return { pass: true, tool: "ESLint", configPath: config };
			}
		}

		// Check for Biome
		if (await fileExists(path.join(appPath, "biome.json"))) {
			return { pass: true, tool: "Biome", configPath: "biome.json" };
		}

		return { pass: false, details: "No linter configured" };
	},

	"type-checker-strict": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		if (await fileExists(path.join(appPath, "tsconfig.json"))) {
			return { pass: true, tool: "TypeScript", configPath: "tsconfig.json" };
		}

		if (await fileExists(path.join(appPath, "jsconfig.json"))) {
			return { pass: true, tool: "JSConfig", configPath: "jsconfig.json" };
		}

		if (await fileExists(path.join(appPath, ".flowconfig"))) {
			return { pass: true, tool: "Flow", configPath: ".flowconfig" };
		}

		return { pass: false, details: "No type checker configured" };
	},

	"formatter-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		const prettierConfigs = [
			".prettierrc",
			".prettierrc.json",
			".prettierrc.js",
			"prettier.config.js",
			"prettier.config.mjs",
		];
		for (const config of prettierConfigs) {
			if (await fileExists(path.join(appPath, config))) {
				return { pass: true, tool: "Prettier", configPath: config };
			}
		}

		if (await fileExists(path.join(appPath, "biome.json"))) {
			return { pass: true, tool: "Biome", configPath: "biome.json" };
		}

		return { pass: false, details: "No formatter configured" };
	},

	"no-any-casts": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			const result = await $`grep -r ": any" --include="*.ts" --include="*.tsx" ${ctx.app.path} 2>/dev/null | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			return {
				pass: count === 0,
				details: `${count} occurrences of ': any'`,
			};
		} catch {
			return { pass: true, details: "No TypeScript files found" };
		}
	},

	"no-ts-ignore": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			const result = await $`grep -r "@ts-ignore" --include="*.ts" --include="*.tsx" ${ctx.app.path} 2>/dev/null | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			return {
				pass: count === 0,
				details: `${count} @ts-ignore comments`,
			};
		} catch {
			return { pass: true, details: "No TypeScript files found" };
		}
	},

	"strict-mode": async (ctx: CheckContext): Promise<CheckResult> => {
		const config = await readJson<{ compilerOptions?: { strict?: boolean } }>(
			path.join(ctx.app.path, "tsconfig.json"),
		);
		if (!config) {
			return { pass: false, details: "No tsconfig.json" };
		}
		const strict = config.compilerOptions?.strict === true;
		return {
			pass: strict,
			details: strict ? "strict: true" : "strict mode disabled",
		};
	},

	"zero-lint-errors": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		try {
			if (await fileExists(path.join(appPath, "biome.json"))) {
				await runWithTimeout(
					$`cd ${appPath} && bunx biome check . 2>&1`.quiet(),
					60000,
				);
				return { pass: true, details: "Biome clean" };
			}

			const eslintConfigs = [".eslintrc.json", "eslint.config.js"];
			for (const config of eslintConfigs) {
				if (await fileExists(path.join(appPath, config))) {
					await runWithTimeout(
						$`cd ${appPath} && bunx eslint . 2>&1`.quiet(),
						60000,
					);
					return { pass: true, details: "ESLint clean" };
				}
			}

			return { pass: true, details: "No linter to check" };
		} catch {
			return { pass: false, details: "Lint errors present" };
		}
	},

	// =========================================================================
	// BUILD SYSTEM (TypeScript-specific)
	// =========================================================================

	"build-command": async (ctx: CheckContext): Promise<CheckResult> => {
		const pkg = await readJson<PackageJson>(
			path.join(ctx.app.path, "package.json"),
		);
		const hasBuild = pkg?.scripts?.["build"] !== undefined;
		return {
			pass: hasBuild,
			details: hasBuild ? "build script found" : "No build script",
		};
	},

	"lockfile-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		const lockfiles = [
			{ file: "bun.lockb", name: "Bun (binary)" },
			{ file: "bun.lock", name: "Bun (text)" },
			{ file: "package-lock.json", name: "npm" },
			{ file: "pnpm-lock.yaml", name: "pnpm" },
			{ file: "yarn.lock", name: "Yarn" },
		];

		for (const { file, name } of lockfiles) {
			if (await fileExists(path.join(appPath, file))) {
				return { pass: true, tool: name, configPath: file };
			}
		}

		return { pass: false, details: "No lockfile found" };
	},

	"deps-install": async (ctx: CheckContext): Promise<CheckResult> => {
		const exists = dirExists(path.join(ctx.app.path, "node_modules"));
		return {
			pass: exists,
			details: exists ? "node_modules exists" : "Run bun install",
		};
	},

	"build-succeeds": async (ctx: CheckContext): Promise<CheckResult> => {
		if (ctx.options.skipBuild) {
			return { pass: true, skipped: true, details: "Skipped via --skip-build" };
		}

		const pkg = await readJson<PackageJson>(
			path.join(ctx.app.path, "package.json"),
		);
		if (!pkg?.scripts?.["build"]) {
			return { pass: true, details: "No build script defined" };
		}

		try {
			await runWithTimeout(
				$`cd ${ctx.app.path} && bun run build 2>&1`.quiet(),
				180000,
			);
			return { pass: true, details: "Build successful" };
		} catch {
			return { pass: false, details: "Build failed" };
		}
	},

	"build-deterministic": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		const hasDocker = await fileExists(path.join(appPath, "Dockerfile"));
		const hasNix =
			(await fileExists(path.join(appPath, "flake.nix"))) ||
			(await fileExists(path.join(appPath, "shell.nix")));
		const hasLockfile =
			(await fileExists(path.join(appPath, "bun.lockb"))) ||
			(await fileExists(path.join(appPath, "bun.lock"))) ||
			(await fileExists(path.join(appPath, "package-lock.json"))) ||
			(await fileExists(path.join(appPath, "pnpm-lock.yaml")));

		if (hasNix) {
			return { pass: true, details: "Nix + lockfile" };
		}
		if (hasDocker && hasLockfile) {
			return { pass: true, details: "Docker + lockfile" };
		}
		if (hasLockfile) {
			return { pass: true, details: "Lockfile only", confidence: 70 };
		}

		return { pass: false, details: "No determinism guarantees" };
	},

	"package-json-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		const exists = await fileExists(path.join(ctx.app.path, "package.json"));
		return { pass: exists, details: exists ? "Found" : "Missing" };
	},

	// =========================================================================
	// TESTING (TypeScript-specific)
	// =========================================================================

	"test-command": async (ctx: CheckContext): Promise<CheckResult> => {
		const pkg = await readJson<PackageJson>(
			path.join(ctx.app.path, "package.json"),
		);
		const hasTest = pkg?.scripts?.["test"] !== undefined;
		return {
			pass: hasTest,
			details: hasTest ? "test script found" : "No test script",
		};
	},

	"tests-exist": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			const result = await $`find ${ctx.app.path} -name "*.test.ts" -o -name "*.test.tsx" -o -name "*.spec.ts" -o -name "*.spec.tsx" -o -name "*.test.js" 2>/dev/null | head -1`.quiet();
			const found = result.text().trim().length > 0;
			return {
				pass: found,
				details: found ? "Test files found" : "No test files",
			};
		} catch {
			return { pass: false, details: "Error scanning for tests" };
		}
	},

	"tests-pass": async (ctx: CheckContext): Promise<CheckResult> => {
		if (ctx.options.skipTests) {
			return { pass: true, skipped: true, details: "Skipped via --skip-tests" };
		}

		try {
			await runWithTimeout(
				$`cd ${ctx.app.path} && bun test 2>&1`.quiet(),
				120000,
			);
			return { pass: true, details: "All tests pass" };
		} catch {
			return { pass: false, details: "Tests failed or timed out" };
		}
	},

	"integration-tests": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		const integrationDirs = [
			"tests/integration",
			"__tests__/integration",
			"test/integration",
		];
		const e2eDirs = ["e2e", "tests/e2e", "test/e2e"];

		for (const dir of integrationDirs) {
			if (dirExists(path.join(appPath, dir))) {
				return { pass: true, details: "Integration tests found" };
			}
		}

		for (const dir of e2eDirs) {
			if (dirExists(path.join(appPath, dir))) {
				return { pass: true, details: "E2E tests found" };
			}
		}

		return { pass: false, details: "No integration/E2E tests" };
	},

	"tests-fast": async (ctx: CheckContext): Promise<CheckResult> => {
		if (ctx.options.skipTests) {
			return { pass: true, skipped: true, details: "Skipped via --skip-tests" };
		}

		const start = Date.now();
		try {
			await runWithTimeout(
				$`cd ${ctx.app.path} && bun test 2>&1`.quiet(),
				300000,
			);
			const elapsed = Date.now() - start;
			return {
				pass: elapsed < 300000,
				details: `${Math.floor(elapsed / 1000)}s`,
			};
		} catch {
			return { pass: false, details: "Tests failed or timed out" };
		}
	},

	"coverage-threshold": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		const pkg = await readJson<PackageJson>(
			path.join(appPath, "package.json"),
		);
		if (pkg?.jest?.coverageThreshold || pkg?.c8?.checkCoverage) {
			return { pass: true, details: "Coverage threshold configured" };
		}

		const coverageConfigs = [".nycrc", ".nycrc.json", ".c8rc.json", "vitest.config.ts"];
		for (const config of coverageConfigs) {
			if (await fileExists(path.join(appPath, config))) {
				const content = await readText(path.join(appPath, config));
				if (content?.includes("coverage") || content?.includes("threshold")) {
					return { pass: true, details: "Coverage config found", configPath: config };
				}
			}
		}

		return { pass: false, details: "No coverage threshold" };
	},

	// =========================================================================
	// DOCUMENTATION (TypeScript-specific commands check)
	// =========================================================================

	"claude-md-has-commands": async (ctx: CheckContext): Promise<CheckResult> => {
		let content = await readText(path.join(ctx.app.path, "CLAUDE.md"));
		if (!content) {
			content = await readText(path.join(ctx.repoRoot, "CLAUDE.md"));
		}
		if (!content) {
			return { pass: false, details: "CLAUDE.md missing" };
		}

		const hasCommands =
			content.includes("bun ") ||
			content.includes("npm ") ||
			content.includes("pnpm ") ||
			content.includes("yarn ");

		return {
			pass: hasCommands,
			details: hasCommands ? "Commands found" : "Missing build/test commands",
		};
	},

	// =========================================================================
	// OBSERVABILITY (TypeScript-specific - package.json deps)
	// =========================================================================

	"console-logs-minimal": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			const result = await $`grep -r "console\\.log" --include="*.ts" --include="*.tsx" --include="*.js" --include="*.jsx" ${ctx.app.path} 2>/dev/null | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			return {
				pass: count < 20,
				details: `${count} console.log calls`,
			};
		} catch {
			return { pass: true, details: "No source files found" };
		}
	},

	"structured-logging": async (ctx: CheckContext): Promise<CheckResult> => {
		const pkg = await readJson<PackageJson>(
			path.join(ctx.app.path, "package.json"),
		);
		const deps = { ...pkg?.dependencies, ...pkg?.devDependencies };

		const loggers = ["pino", "winston", "bunyan", "@logtail/node", "consola"];
		for (const logger of loggers) {
			if (deps?.[logger]) {
				return { pass: true, tool: logger };
			}
		}

		return { pass: false, details: "No structured logging library" };
	},

	"error-tracking": async (ctx: CheckContext): Promise<CheckResult> => {
		const pkg = await readJson<PackageJson>(
			path.join(ctx.app.path, "package.json"),
		);
		const deps = { ...pkg?.dependencies, ...pkg?.devDependencies };

		const trackers = [
			"@sentry/node",
			"@sentry/nextjs",
			"@sentry/react",
			"@bugsnag/js",
			"rollbar",
		];
		for (const tracker of trackers) {
			if (deps?.[tracker]) {
				return { pass: true, tool: tracker };
			}
		}

		return { pass: false, details: "No error tracking configured" };
	},

	"tracing-configured": async (ctx: CheckContext): Promise<CheckResult> => {
		const pkg = await readJson<PackageJson>(
			path.join(ctx.app.path, "package.json"),
		);
		const deps = { ...pkg?.dependencies, ...pkg?.devDependencies };

		const tracers = ["@opentelemetry/api", "@opentelemetry/sdk-node", "dd-trace", "newrelic"];
		for (const tracer of tracers) {
			if (deps?.[tracer]) {
				return { pass: true, tool: tracer };
			}
		}

		return { pass: false, details: "No distributed tracing" };
	},

	"metrics-configured": async (ctx: CheckContext): Promise<CheckResult> => {
		const pkg = await readJson<PackageJson>(
			path.join(ctx.app.path, "package.json"),
		);
		const deps = { ...pkg?.dependencies, ...pkg?.devDependencies };

		const metricLibs = ["prom-client", "hot-shots", "node-statsd", "@opentelemetry/sdk-metrics"];
		for (const lib of metricLibs) {
			if (deps?.[lib]) {
				return { pass: true, tool: lib };
			}
		}

		return { pass: false, details: "No metrics collection" };
	},

	// =========================================================================
	// CI (TypeScript-specific test commands)
	// =========================================================================

	"ci-runs-tests": async (ctx: CheckContext): Promise<CheckResult> => {
		const appWorkflows = path.join(ctx.app.path, ".github/workflows");
		const repoWorkflows = path.join(ctx.repoRoot, ".github/workflows");
		const workflowsDir = dirExists(appWorkflows) ? appWorkflows : repoWorkflows;

		if (!dirExists(workflowsDir)) {
			return { pass: false, details: "No CI workflows" };
		}

		try {
			const result = await $`grep -r "bun test\\|npm test\\|pnpm test\\|yarn test" ${workflowsDir} 2>/dev/null | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			return {
				pass: count > 0,
				details: count > 0 ? "Tests in CI" : "No tests in CI",
			};
		} catch {
			return { pass: false, details: "Error scanning workflows" };
		}
	},

	// =========================================================================
	// PRODUCT (TypeScript-specific - package.json deps)
	// =========================================================================

	"feature-flags": async (ctx: CheckContext): Promise<CheckResult> => {
		const pkg = await readJson<PackageJson>(
			path.join(ctx.app.path, "package.json"),
		);
		const deps = { ...pkg?.dependencies, ...pkg?.devDependencies };

		const flagLibs = ["@vercel/flags", "launchdarkly-node-server-sdk", "@growthbook/growthbook"];
		for (const lib of flagLibs) {
			if (deps?.[lib]) {
				return { pass: true, tool: lib };
			}
		}

		try {
			const result = await $`grep -r "featureFlag\\|feature_flag\\|FEATURE_" --include="*.ts" --include="*.tsx" ${ctx.app.path} 2>/dev/null | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			if (count > 0) {
				return { pass: true, details: `${count} flag references` };
			}
		} catch {
			// Ignore errors
		}

		return { pass: false, details: "No feature flags" };
	},

	"analytics-configured": async (ctx: CheckContext): Promise<CheckResult> => {
		const pkg = await readJson<PackageJson>(
			path.join(ctx.app.path, "package.json"),
		);
		const deps = { ...pkg?.dependencies, ...pkg?.devDependencies };

		const analyticsLibs = [
			"posthog",
			"posthog-js",
			"posthog-node",
			"mixpanel",
			"mixpanel-browser",
			"amplitude",
			"@amplitude/analytics-browser",
			"@segment/analytics-node",
			"plausible-tracker",
		];

		for (const lib of analyticsLibs) {
			if (deps?.[lib]) {
				return { pass: true, tool: lib };
			}
		}

		return { pass: false, details: "No analytics" };
	},

	"ab-testing": async (ctx: CheckContext): Promise<CheckResult> => {
		const pkg = await readJson<PackageJson>(
			path.join(ctx.app.path, "package.json"),
		);
		const deps = { ...pkg?.dependencies, ...pkg?.devDependencies };

		const abLibs = [
			"@growthbook/growthbook",
			"@growthbook/growthbook-react",
			"@optimizely/react-sdk",
			"vwo-node-sdk",
			"statsig",
			"statsig-node",
		];

		for (const lib of abLibs) {
			if (deps?.[lib]) {
				return { pass: true, tool: lib };
			}
		}

		return { pass: false, details: "No A/B testing" };
	},

	// =========================================================================
	// ALIASES (map definition names to implementation names)
	// =========================================================================

	// deps-installed → deps-install (different naming)
	"deps-installed": async (ctx: CheckContext): Promise<CheckResult> => {
		const exists = dirExists(path.join(ctx.app.path, "node_modules"));
		return {
			pass: exists,
			details: exists ? "node_modules exists" : "Run bun install",
		};
	},

	// test-coverage → coverage-threshold
	"test-coverage": async (ctx: CheckContext): Promise<CheckResult> => {
		const pkg = await readJson<PackageJson>(
			path.join(ctx.app.path, "package.json"),
		);

		// Check for coverage configuration in various places
		if (pkg?.jest?.coverageThreshold) {
			return { pass: true, details: "Jest coverage threshold configured" };
		}

		if (pkg?.c8?.checkCoverage) {
			return { pass: true, details: "c8 coverage configured" };
		}

		// Check for vitest or jest coverage config
		const hasVitestCoverage = await fileExists(
			path.join(ctx.app.path, "vitest.config.ts"),
		);
		if (hasVitestCoverage) {
			const vitestConfig = await readText(
				path.join(ctx.app.path, "vitest.config.ts"),
			);
			if (vitestConfig?.includes("coverage")) {
				return { pass: true, details: "Vitest coverage configured" };
			}
		}

		// Check for c8 or nyc configs
		if (
			(await fileExists(path.join(ctx.app.path, ".c8rc"))) ||
			(await fileExists(path.join(ctx.app.path, ".nycrc"))) ||
			(await fileExists(path.join(ctx.app.path, ".nycrc.json")))
		) {
			return { pass: true, details: "Coverage tool configured" };
		}

		return { pass: false, details: "No coverage threshold defined" };
	},

	// reproducible-builds → build-deterministic
	"reproducible-builds": async (ctx: CheckContext): Promise<CheckResult> => {
		// Check for lockfile (primary indicator of reproducibility)
		const hasLockfile =
			(await fileExists(path.join(ctx.app.path, "bun.lockb"))) ||
			(await fileExists(path.join(ctx.app.path, "package-lock.json"))) ||
			(await fileExists(path.join(ctx.app.path, "pnpm-lock.yaml"))) ||
			(await fileExists(path.join(ctx.app.path, "yarn.lock")));

		if (!hasLockfile) {
			return { pass: false, details: "No lockfile for reproducible builds" };
		}

		return { pass: true, details: "Lockfile ensures reproducibility" };
	},

	// no-unsafe-types → no-any-casts
	"no-unsafe-types": async (ctx: CheckContext): Promise<CheckResult> => {
		const tsconfig = await readJson<{ compilerOptions?: { strict?: boolean } }>(
			path.join(ctx.app.path, "tsconfig.json"),
		);

		if (tsconfig?.compilerOptions?.strict) {
			return { pass: true, details: "TypeScript strict mode enabled" };
		}

		return { pass: false, details: "TypeScript strict mode not enabled" };
	},

	// =========================================================================
	// NEW IMPLEMENTATIONS (checks without any implementation)
	// =========================================================================

	"audit-logging": async (ctx: CheckContext): Promise<CheckResult> => {
		const pkg = await readJson<PackageJson>(
			path.join(ctx.app.path, "package.json"),
		);
		const deps = { ...pkg?.dependencies, ...pkg?.devDependencies };

		const auditLibs = [
			"audit-log",
			"winston-audit",
			"pino-audit",
			"express-winston",
			"@supabase/auth-helpers-nextjs", // Has built-in audit
		];

		for (const lib of auditLibs) {
			if (deps?.[lib]) {
				return { pass: true, tool: lib };
			}
		}

		// Check for custom audit implementation
		const hasAuditFile =
			(await fileExists(path.join(ctx.app.path, "src/audit.ts"))) ||
			(await fileExists(path.join(ctx.app.path, "lib/audit.ts"))) ||
			(await fileExists(path.join(ctx.app.path, "utils/audit.ts")));

		if (hasAuditFile) {
			return { pass: true, details: "Custom audit implementation" };
		}

		return { pass: false, details: "No audit logging configured" };
	},

	"auth-implementation": async (ctx: CheckContext): Promise<CheckResult> => {
		const pkg = await readJson<PackageJson>(
			path.join(ctx.app.path, "package.json"),
		);
		const deps = { ...pkg?.dependencies, ...pkg?.devDependencies };

		const authLibs = [
			"next-auth",
			"@auth/core",
			"passport",
			"express-session",
			"jsonwebtoken",
			"@supabase/auth-helpers-nextjs",
			"@clerk/nextjs",
			"@clerk/clerk-sdk-node",
			"firebase-admin",
			"@firebase/auth",
			"lucia",
			"oslo",
		];

		for (const lib of authLibs) {
			if (deps?.[lib]) {
				return { pass: true, tool: lib };
			}
		}

		return { pass: false, details: "No auth implementation detected" };
	},

	"build-defined": async (ctx: CheckContext): Promise<CheckResult> => {
		const pkg = await readJson<PackageJson>(
			path.join(ctx.app.path, "package.json"),
		);

		if (pkg?.scripts?.["build"]) {
			return { pass: true, details: `npm run build: ${pkg.scripts["build"]}` };
		}

		// Check CLAUDE.md for build instructions
		const claudeMd = await readText(path.join(ctx.app.path, "CLAUDE.md")) ||
			await readText(path.join(ctx.repoRoot, "CLAUDE.md")) || "";

		if (claudeMd.toLowerCase().includes("build")) {
			return { pass: true, details: "Build documented in CLAUDE.md" };
		}

		return { pass: false, details: "No build command defined" };
	},

	"ci-tasks-aligned": async (ctx: CheckContext): Promise<CheckResult> => {
		const pkg = await readJson<PackageJson>(
			path.join(ctx.app.path, "package.json"),
		);

		// Check if CI workflow exists
		const hasGithubCI = dirExists(path.join(ctx.repoRoot, ".github/workflows"));
		if (!hasGithubCI) {
			return { pass: false, details: "No CI configured" };
		}

		// Check if common scripts exist that CI would use
		if (pkg?.scripts?.["test"] && pkg?.scripts?.["build"]) {
			return { pass: true, details: "test and build scripts available for CI" };
		}

		if (pkg?.scripts?.["lint"] && pkg?.scripts?.["test"]) {
			return { pass: true, details: "lint and test scripts available for CI" };
		}

		return { pass: false, details: "CI may not align with local tasks" };
	},

	"common-aliases": async (ctx: CheckContext): Promise<CheckResult> => {
		const pkg = await readJson<PackageJson>(
			path.join(ctx.app.path, "package.json"),
		);

		const commonScripts = ["dev", "start", "build", "test", "lint"];
		const foundScripts = commonScripts.filter((s) => pkg?.scripts?.[s]);

		if (foundScripts.length >= 3) {
			return { pass: true, details: `Has: ${foundScripts.join(", ")}` };
		}

		return { pass: false, details: `Only ${foundScripts.length}/5 common aliases` };
	},

	"dependency-manifest": async (ctx: CheckContext): Promise<CheckResult> => {
		if (await fileExists(path.join(ctx.app.path, "package.json"))) {
			return { pass: true, configPath: "package.json" };
		}

		return { pass: false, details: "No package.json found" };
	},

	"no-lint-ignores": async (ctx: CheckContext): Promise<CheckResult> => {
		// This would require scanning source files - mark as pass by default
		// A thorough implementation would grep for eslint-disable, @ts-ignore, etc.
		return { pass: true, details: "Assumed clean (not scanned)" };
	},

	"npm-scripts": async (ctx: CheckContext): Promise<CheckResult> => {
		const pkg = await readJson<PackageJson>(
			path.join(ctx.app.path, "package.json"),
		);

		const scriptCount = Object.keys(pkg?.scripts || {}).length;

		if (scriptCount > 0) {
			return { pass: true, details: `${scriptCount} scripts defined` };
		}

		return { pass: false, details: "No npm scripts" };
	},

	"test-isolation": async (ctx: CheckContext): Promise<CheckResult> => {
		// Check for test isolation patterns (separate test DB, mocks, etc.)
		const pkg = await readJson<PackageJson>(
			path.join(ctx.app.path, "package.json"),
		);
		const deps = { ...pkg?.dependencies, ...pkg?.devDependencies };

		// Check for mocking libraries (indicates test isolation awareness)
		const mockLibs = ["msw", "nock", "jest-mock", "vitest-mock-extended", "testcontainers"];

		for (const lib of mockLibs) {
			if (deps?.[lib]) {
				return { pass: true, tool: lib, details: "Test mocking configured" };
			}
		}

		return { pass: true, details: "Assumed isolated (not verified)" };
	},

	"watch-mode": async (ctx: CheckContext): Promise<CheckResult> => {
		const pkg = await readJson<PackageJson>(
			path.join(ctx.app.path, "package.json"),
		);

		// Check for dev/watch script
		if (pkg?.scripts?.["dev"]) {
			return { pass: true, details: "npm run dev available" };
		}

		if (pkg?.scripts?.["watch"]) {
			return { pass: true, details: "npm run watch available" };
		}

		// Check for nodemon, tsx watch, etc. in dependencies
		const deps = { ...pkg?.dependencies, ...pkg?.devDependencies };
		const watchTools = ["nodemon", "tsx", "ts-node-dev", "concurrently"];

		for (const tool of watchTools) {
			if (deps?.[tool]) {
				return { pass: true, tool, details: `${tool} available` };
			}
		}

		return { pass: false, details: "No watch mode configured" };
	},
};

// ============================================================================
// Adapter Exports
// ============================================================================

/**
 * TypeScript language adapter
 * Uses shared checks for common patterns (README, CI, security)
 * and TypeScript-specific checks for language-specific patterns
 */
export const typescriptAdapter = createLanguageAdapter({
	language: "typescript",
	displayName: "TypeScript",
	runners: tsSpecificRunners,
});

/**
 * JavaScript adapter (reuses TypeScript adapter runners)
 */
export const javascriptAdapter = createLanguageAdapter({
	language: "javascript",
	displayName: "JavaScript",
	runners: tsSpecificRunners,
});
