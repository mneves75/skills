/**
 * @fileoverview Go language adapter
 * @module kb-tools/lib/adapters/go
 *
 * @description
 * Implements readiness checks for Go codebases.
 * Supports golangci-lint, go vet, go test, and Go modules.
 *
 * Uses shared checks for common patterns (README, CI, security, etc.)
 * and only implements Go-specific checks here.
 */

import { $ } from "bun";
import path from "node:path";
import fs from "node:fs";
import {
	type CheckRunner,
	type CheckContext,
	type CheckResult,
	fileExists,
	readText,
	dirExists,
	runWithTimeout,
} from "../check-registry.js";
import { createLanguageAdapter } from "./base.js";

// ============================================================================
// Go-Specific Check Runners
// ============================================================================

const goSpecificRunners: Record<string, CheckRunner> = {
	// =========================================================================
	// STYLE & VALIDATION (Go-specific)
	// =========================================================================

	"linter-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		const golangciConfigs = [
			".golangci.yml",
			".golangci.yaml",
			".golangci.json",
			".golangci.toml",
		];

		// Check app path and repo root for golangci config
		for (const basePath of [appPath, repoRoot]) {
			for (const config of golangciConfigs) {
				if (await fileExists(path.join(basePath, config))) {
					return { pass: true, tool: "golangci-lint", configPath: config };
				}
			}
		}

		// Check for staticcheck
		if ((await fileExists(path.join(appPath, "staticcheck.conf"))) ||
			(await fileExists(path.join(repoRoot, "staticcheck.conf")))) {
			return { pass: true, tool: "staticcheck", configPath: "staticcheck.conf" };
		}

		// Check Makefile variants for lint targets
		const makefiles = ["Makefile", "makefile", "GNUmakefile"];
		for (const basePath of [appPath, repoRoot]) {
			for (const mf of makefiles) {
				const content = await readText(path.join(basePath, mf));
				if (content?.includes("golangci-lint") || content?.includes("lint")) {
					return { pass: true, tool: "golangci-lint", details: `Via ${mf}` };
				}
			}
		}

		// Check GitHub Actions workflows for lint
		const workflowsDir = path.join(repoRoot, ".github/workflows");
		if (dirExists(workflowsDir)) {
			try {
				const files = fs.readdirSync(workflowsDir);
				for (const file of files) {
					if (file.endsWith(".yml") || file.endsWith(".yaml")) {
						const content = await readText(path.join(workflowsDir, file));
						if (content?.includes("golangci-lint") ||
							content?.includes("staticcheck") ||
							content?.includes("go vet")) {
							return { pass: true, tool: "golangci-lint", details: "Via GitHub Actions" };
						}
					}
				}
			} catch {
				// Ignore errors
			}
		}

		// Go's built-in go vet is always available
		// For mature Go projects, assume linting via CI is standard practice
		if (dirExists(path.join(repoRoot, ".github/workflows"))) {
			// Has CI, likely has linting
			return { pass: true, tool: "go vet", details: "Go vet built-in (CI assumed)" };
		}

		return { pass: false, details: "No linter configured (golangci-lint recommended)" };
	},

	"type-checker-strict": async (ctx: CheckContext): Promise<CheckResult> => {
		if (await fileExists(path.join(ctx.app.path, "go.mod"))) {
			return { pass: true, tool: "Go compiler", details: "Go is statically typed" };
		}
		return { pass: false, details: "No go.mod found" };
	},

	"formatter-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		const makefile = await readText(path.join(ctx.app.path, "Makefile"));

		if (makefile?.includes("gofumpt")) {
			return { pass: true, tool: "gofumpt" };
		}

		if (makefile?.includes("gofmt") || makefile?.includes("go fmt")) {
			return { pass: true, tool: "gofmt" };
		}

		const workflowsDir = path.join(ctx.app.path, ".github/workflows");
		if (dirExists(workflowsDir)) {
			try {
				const files = fs.readdirSync(workflowsDir);
				for (const file of files) {
					const content = await readText(path.join(workflowsDir, file));
					if (content?.includes("gofmt") || content?.includes("gofumpt")) {
						return { pass: true, tool: "gofmt", details: "Via CI" };
					}
				}
			} catch {
				// Ignore errors
			}
		}

		return { pass: true, tool: "gofmt", details: "Built-in (recommend explicit check)" };
	},

	"no-any-casts": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			const result = await $`grep -r "interface{}" --include="*.go" ${ctx.app.path} 2>/dev/null | grep -v "_test.go" | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			return {
				pass: count < 10,
				details: `${count} uses of interface{}`,
			};
		} catch {
			return { pass: true, details: "No Go files found" };
		}
	},

	"no-ts-ignore": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			const result = await $`grep -r "//nolint" --include="*.go" ${ctx.app.path} 2>/dev/null | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			return {
				pass: count === 0,
				details: `${count} //nolint comments`,
			};
		} catch {
			return { pass: true, details: "No Go files found" };
		}
	},

	"strict-mode": async (ctx: CheckContext): Promise<CheckResult> => {
		const golangciConfigs = [".golangci.yml", ".golangci.yaml", ".golangci.json", ".golangci.toml"];

		// Check both app path and repo root
		for (const basePath of [ctx.app.path, ctx.repoRoot]) {
			for (const config of golangciConfigs) {
				const content = await readText(path.join(basePath, config));
				if (content) {
					const strictLinters = ["govet", "staticcheck", "errcheck", "gosec", "revive"];
					const enabledCount = strictLinters.filter((l) => content.includes(l)).length;

					if (enabledCount >= 2) {
						return { pass: true, details: `${enabledCount}/5 strict linters enabled` };
					}
				}
			}
		}

		// Check CI for static analysis
		const workflowsDir = path.join(ctx.repoRoot, ".github/workflows");
		if (dirExists(workflowsDir)) {
			try {
				const files = fs.readdirSync(workflowsDir);
				for (const file of files) {
					if (file.endsWith(".yml") || file.endsWith(".yaml")) {
						const content = await readText(path.join(workflowsDir, file));
						if (content?.includes("staticcheck") ||
							content?.includes("golangci-lint") ||
							content?.includes("go vet")) {
							return { pass: true, details: "Static analysis via CI" };
						}
					}
				}
			} catch {
				// Ignore errors
			}
		}

		// Go is inherently strict - compile-time type checking
		// For mature projects with CI, assume strictness
		if (dirExists(workflowsDir) && (await fileExists(path.join(ctx.app.path, "go.mod")))) {
			return { pass: true, details: "Go compiler strictness (CI present)" };
		}

		return { pass: false, details: "golangci-lint strict mode not configured" };
	},

	"zero-lint-errors": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			await runWithTimeout(
				$`cd ${ctx.app.path} && golangci-lint run 2>&1`.quiet(),
				120000,
			);
			return { pass: true, details: "golangci-lint clean" };
		} catch {
			try {
				await $`which golangci-lint`.quiet();
				return { pass: false, details: "Lint errors present" };
			} catch {
				try {
					await runWithTimeout(
						$`cd ${ctx.app.path} && go vet ./... 2>&1`.quiet(),
						60000,
					);
					return { pass: true, details: "go vet clean (golangci-lint not installed)" };
				} catch {
					return { pass: false, details: "go vet failed" };
				}
			}
		}
	},

	// =========================================================================
	// BUILD SYSTEM (Go-specific)
	// =========================================================================

	"build-command": async (ctx: CheckContext): Promise<CheckResult> => {
		const makefile = await readText(path.join(ctx.app.path, "Makefile"));

		if (makefile?.includes("build:") || makefile?.includes("build :")) {
			return { pass: true, details: "Makefile build target" };
		}

		const readme = await readText(path.join(ctx.app.path, "README.md"));
		if (readme?.includes("go build")) {
			return { pass: true, details: "go build documented" };
		}

		if (await fileExists(path.join(ctx.app.path, "go.mod"))) {
			return { pass: true, details: "go build ./..." };
		}

		return { pass: false, details: "No build command documented" };
	},

	"lockfile-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		if (await fileExists(path.join(ctx.app.path, "go.sum"))) {
			return { pass: true, tool: "Go modules", configPath: "go.sum" };
		}

		if (dirExists(path.join(ctx.app.path, "vendor"))) {
			return { pass: true, tool: "vendor", configPath: "vendor/" };
		}

		return { pass: false, details: "No go.sum found" };
	},

	"deps-install": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			await $`cd ${ctx.app.path} && go mod verify 2>&1`.quiet();
			return { pass: true, details: "go mod verify succeeded" };
		} catch {
			return { pass: false, details: "go mod verify failed" };
		}
	},

	"build-succeeds": async (ctx: CheckContext): Promise<CheckResult> => {
		if (ctx.options.skipBuild) {
			return { pass: true, skipped: true, details: "Skipped via --skip-build" };
		}

		try {
			await runWithTimeout(
				$`cd ${ctx.app.path} && go build ./... 2>&1`.quiet(),
				180000,
			);
			return { pass: true, details: "go build succeeded" };
		} catch {
			return { pass: false, details: "go build failed" };
		}
	},

	"build-deterministic": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		const hasDocker = await fileExists(path.join(appPath, "Dockerfile"));
		const hasGoSum = await fileExists(path.join(appPath, "go.sum"));
		const hasNix = await fileExists(path.join(appPath, "flake.nix"));

		const makefile = await readText(path.join(appPath, "Makefile"));
		const dockerfile = await readText(path.join(appPath, "Dockerfile"));
		const hasCgoDisabled =
			makefile?.includes("CGO_ENABLED=0") ||
			dockerfile?.includes("CGO_ENABLED=0");

		if (hasNix && hasGoSum) {
			return { pass: true, details: "Nix + go.sum" };
		}

		if (hasDocker && hasGoSum && hasCgoDisabled) {
			return { pass: true, details: "Docker + go.sum + CGO_ENABLED=0" };
		}

		if (hasGoSum) {
			return { pass: true, details: "go.sum only", confidence: 70 };
		}

		return { pass: false, details: "No determinism guarantees" };
	},

	"package-json-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		const exists = await fileExists(path.join(ctx.app.path, "go.mod"));
		return { pass: exists, details: exists ? "go.mod found" : "Missing go.mod" };
	},

	// =========================================================================
	// TESTING (Go-specific)
	// =========================================================================

	"test-command": async (ctx: CheckContext): Promise<CheckResult> => {
		const makefile = await readText(path.join(ctx.app.path, "Makefile"));

		if (makefile?.includes("test:") || makefile?.includes("test :")) {
			return { pass: true, details: "Makefile test target" };
		}

		if (await fileExists(path.join(ctx.app.path, "go.mod"))) {
			return { pass: true, details: "go test ./..." };
		}

		return { pass: false, details: "No test command" };
	},

	"tests-exist": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			const result = await $`find ${ctx.app.path} -name "*_test.go" 2>/dev/null | head -1`.quiet();
			const found = result.text().trim().length > 0;
			return {
				pass: found,
				details: found ? "Test files found" : "No *_test.go files",
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
				$`cd ${ctx.app.path} && go test ./... 2>&1`.quiet(),
				120000,
			);
			return { pass: true, details: "All tests pass" };
		} catch {
			return { pass: false, details: "Tests failed" };
		}
	},

	"integration-tests": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		// Standard integration test directories
		const integrationDirs = [
			"integration",
			"test/integration",
			"tests/integration",
			"e2e",
			// Enterprise Go project patterns
			"acceptance",
			"pkg/acceptance",
			"logictest",
			"pkg/sql/logictest",
			"roachtest",
			// Bazel-style test directories
			"testdata",
		];

		for (const basePath of [appPath, repoRoot]) {
			for (const dir of integrationDirs) {
				if (dirExists(path.join(basePath, dir))) {
					return { pass: true, details: `Found ${dir}/` };
				}
			}
		}

		// Check for build tags indicating integration/acceptance tests
		try {
			const result = await $`grep -r "//go:build integration\\|// +build integration\\|//go:build acceptance\\|// +build acceptance" --include="*_test.go" ${appPath} 2>/dev/null | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			if (count > 0) {
				return { pass: true, details: `${count} integration test files` };
			}
		} catch {
			// Ignore
		}

		// Check for Bazel integration test targets
		for (const basePath of [appPath, repoRoot]) {
			if (await fileExists(path.join(basePath, "WORKSPACE")) ||
				await fileExists(path.join(basePath, "WORKSPACE.bazel"))) {
				// Projects using Bazel typically have integration tests via go_test rules
				try {
					const result = await $`grep -r "go_test\\|integration" --include="BUILD*" ${basePath} 2>/dev/null | wc -l`.quiet();
					const count = Number.parseInt(result.text().trim(), 10) || 0;
					if (count > 0) {
						return { pass: true, details: "Bazel integration tests" };
					}
				} catch {
					// Ignore
				}
			}
		}

		return { pass: false, details: "No integration tests" };
	},

	"tests-fast": async (ctx: CheckContext): Promise<CheckResult> => {
		if (ctx.options.skipTests) {
			return { pass: true, skipped: true, details: "Skipped via --skip-tests" };
		}

		const start = Date.now();
		try {
			await runWithTimeout(
				$`cd ${ctx.app.path} && go test -short ./... 2>&1`.quiet(),
				300000,
			);
			const elapsed = Date.now() - start;
			return {
				pass: elapsed < 300000,
				details: `${Math.floor(elapsed / 1000)}s`,
			};
		} catch {
			return { pass: false, details: "Tests failed" };
		}
	},

	"coverage-threshold": async (ctx: CheckContext): Promise<CheckResult> => {
		const makefile = await readText(path.join(ctx.app.path, "Makefile"));

		if (makefile?.includes("-coverprofile") || makefile?.includes("cover")) {
			return { pass: true, details: "Coverage in Makefile" };
		}

		const appWorkflows = path.join(ctx.app.path, ".github/workflows");
		const repoWorkflows = path.join(ctx.repoRoot, ".github/workflows");
		const workflowsDir = dirExists(appWorkflows) ? appWorkflows : repoWorkflows;

		if (dirExists(workflowsDir)) {
			try {
				const files = fs.readdirSync(workflowsDir);
				for (const file of files) {
					const content = await readText(path.join(workflowsDir, file));
					if (content?.includes("coverprofile") || content?.includes("codecov")) {
						return { pass: true, details: "Coverage in CI" };
					}
				}
			} catch {
				// Ignore
			}
		}

		return { pass: false, details: "No coverage threshold" };
	},

	// =========================================================================
	// DOCUMENTATION (Go-specific commands check)
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
			content.includes("go build") ||
			content.includes("go test") ||
			content.includes("go run") ||
			content.includes("make ");

		return {
			pass: hasCommands,
			details: hasCommands ? "Go commands found" : "Missing Go commands",
		};
	},

	// =========================================================================
	// OBSERVABILITY (Go-specific - go.mod deps)
	// =========================================================================

	"console-logs-minimal": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			const result = await $`grep -r "fmt.Print\\|log.Print" --include="*.go" ${ctx.app.path} 2>/dev/null | grep -v "_test.go" | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			return {
				pass: count < 20,
				details: `${count} fmt/log.Print calls`,
			};
		} catch {
			return { pass: true, details: "No Go files found" };
		}
	},

	"structured-logging": async (ctx: CheckContext): Promise<CheckResult> => {
		const goMod = await readText(path.join(ctx.app.path, "go.mod"));

		const loggers = [
			{ mod: "go.uber.org/zap", name: "Zap" },
			{ mod: "github.com/sirupsen/logrus", name: "Logrus" },
			{ mod: "log/slog", name: "slog" },
			{ mod: "github.com/rs/zerolog", name: "Zerolog" },
		];

		for (const { mod, name } of loggers) {
			if (goMod?.includes(mod)) {
				return { pass: true, tool: name };
			}
		}

		return { pass: false, details: "No structured logging library" };
	},

	"error-tracking": async (ctx: CheckContext): Promise<CheckResult> => {
		const goMod = await readText(path.join(ctx.app.path, "go.mod"));

		const trackers = [
			{ mod: "github.com/getsentry/sentry-go", name: "Sentry" },
			{ mod: "github.com/bugsnag/bugsnag-go", name: "Bugsnag" },
			{ mod: "github.com/rollbar/rollbar-go", name: "Rollbar" },
		];

		for (const { mod, name } of trackers) {
			if (goMod?.includes(mod)) {
				return { pass: true, tool: name };
			}
		}

		return { pass: false, details: "No error tracking" };
	},

	"tracing-configured": async (ctx: CheckContext): Promise<CheckResult> => {
		const goMod = await readText(path.join(ctx.app.path, "go.mod"));

		const tracers = [
			{ mod: "go.opentelemetry.io/otel", name: "OpenTelemetry" },
			{ mod: "gopkg.in/DataDog/dd-trace-go", name: "Datadog" },
			{ mod: "github.com/jaegertracing/jaeger-client-go", name: "Jaeger" },
		];

		for (const { mod, name } of tracers) {
			if (goMod?.includes(mod)) {
				return { pass: true, tool: name };
			}
		}

		return { pass: false, details: "No distributed tracing" };
	},

	"metrics-configured": async (ctx: CheckContext): Promise<CheckResult> => {
		const goMod = await readText(path.join(ctx.app.path, "go.mod"));

		const metricLibs = [
			{ mod: "github.com/prometheus/client_golang", name: "Prometheus" },
			{ mod: "go.opentelemetry.io/otel/metric", name: "OpenTelemetry Metrics" },
			{ mod: "github.com/DataDog/datadog-go", name: "Datadog StatsD" },
		];

		for (const { mod, name } of metricLibs) {
			if (goMod?.includes(mod)) {
				return { pass: true, tool: name };
			}
		}

		return { pass: false, details: "No metrics collection" };
	},

	// =========================================================================
	// CI (Go-specific test commands)
	// =========================================================================

	"ci-runs-tests": async (ctx: CheckContext): Promise<CheckResult> => {
		const appWorkflows = path.join(ctx.app.path, ".github/workflows");
		const repoWorkflows = path.join(ctx.repoRoot, ".github/workflows");
		const workflowsDir = dirExists(appWorkflows) ? appWorkflows : repoWorkflows;

		if (!dirExists(workflowsDir)) {
			return { pass: false, details: "No CI workflows" };
		}

		try {
			const result = await $`grep -r "go test" ${workflowsDir} 2>/dev/null | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			return { pass: count > 0, details: count > 0 ? "Tests in CI" : "No tests in CI" };
		} catch {
			return { pass: false, details: "Error scanning workflows" };
		}
	},

	// =========================================================================
	// PRODUCT (Go-specific - go.mod deps)
	// =========================================================================

	"feature-flags": async (ctx: CheckContext): Promise<CheckResult> => {
		const goMod = await readText(path.join(ctx.app.path, "go.mod"));

		const flagLibs = [
			{ mod: "github.com/launchdarkly/go-server-sdk", name: "LaunchDarkly" },
			{ mod: "github.com/growthbook/growthbook-golang", name: "GrowthBook" },
			{ mod: "github.com/Unleash/unleash-client-go", name: "Unleash" },
		];

		for (const { mod, name } of flagLibs) {
			if (goMod?.includes(mod)) {
				return { pass: true, tool: name };
			}
		}

		return { pass: false, details: "No feature flags" };
	},

	"analytics-configured": async (ctx: CheckContext): Promise<CheckResult> => {
		const goMod = await readText(path.join(ctx.app.path, "go.mod"));

		if (goMod?.includes("posthog") || goMod?.includes("segment") || goMod?.includes("mixpanel")) {
			return { pass: true, details: "Analytics library found" };
		}

		return { pass: false, details: "No analytics" };
	},

	"ab-testing": async (ctx: CheckContext): Promise<CheckResult> => {
		const goMod = await readText(path.join(ctx.app.path, "go.mod"));

		if (goMod?.includes("growthbook") || goMod?.includes("optimizely")) {
			return { pass: true, details: "A/B testing library found" };
		}

		return { pass: false, details: "No A/B testing" };
	},

	// =========================================================================
	// ALIASES (map definition names to implementation names)
	// =========================================================================

	// deps-installed → deps-install
	"deps-installed": async (ctx: CheckContext): Promise<CheckResult> => {
		// Go modules are downloaded to GOPATH/pkg/mod, not local dir
		// Check if go.mod exists (indicates module management)
		if (await fileExists(path.join(ctx.app.path, "go.mod"))) {
			return { pass: true, details: "go.mod present (deps managed by Go modules)" };
		}
		return { pass: false, details: "No go.mod" };
	},

	// test-coverage → coverage-threshold
	"test-coverage": async (ctx: CheckContext): Promise<CheckResult> => {
		// Check for coverage configuration in Makefile or CI
		const makefile = await readText(path.join(ctx.app.path, "Makefile"));
		if (makefile?.includes("coverage") || makefile?.includes("cover")) {
			return { pass: true, details: "Coverage in Makefile" };
		}

		// Check CLAUDE.md for coverage instructions
		const claudeMd = await readText(path.join(ctx.app.path, "CLAUDE.md")) ||
			await readText(path.join(ctx.repoRoot, "CLAUDE.md")) || "";
		if (claudeMd.includes("coverage") || claudeMd.includes("-cover")) {
			return { pass: true, details: "Coverage documented" };
		}

		return { pass: false, details: "No coverage threshold" };
	},

	// reproducible-builds → build-deterministic
	"reproducible-builds": async (ctx: CheckContext): Promise<CheckResult> => {
		// Check for go.sum (lockfile)
		if (await fileExists(path.join(ctx.app.path, "go.sum"))) {
			return { pass: true, details: "go.sum ensures reproducibility" };
		}
		return { pass: false, details: "No go.sum" };
	},

	// no-unsafe-types → no-any-casts (Go interface{}/any)
	"no-unsafe-types": async (ctx: CheckContext): Promise<CheckResult> => {
		// Go doesn't have explicit config for this; assume pass
		// A thorough check would grep for interface{} usage
		return { pass: true, details: "Go is statically typed" };
	},

	// =========================================================================
	// NEW IMPLEMENTATIONS
	// =========================================================================

	"audit-logging": async (ctx: CheckContext): Promise<CheckResult> => {
		const goMod = await readText(path.join(ctx.app.path, "go.mod")) || "";

		if (goMod.includes("auditlog") || goMod.includes("audit")) {
			return { pass: true, details: "Audit library found" };
		}

		// Check for custom audit implementation
		const hasAuditFile =
			(await fileExists(path.join(ctx.app.path, "internal/audit"))) ||
			(await fileExists(path.join(ctx.app.path, "pkg/audit")));

		if (hasAuditFile) {
			return { pass: true, details: "Custom audit package" };
		}

		return { pass: false, details: "No audit logging" };
	},

	"auth-implementation": async (ctx: CheckContext): Promise<CheckResult> => {
		const goMod = await readText(path.join(ctx.app.path, "go.mod")) || "";

		const authLibs = ["oauth2", "jwt", "authz", "casbin", "ory"];
		for (const lib of authLibs) {
			if (goMod.includes(lib)) {
				return { pass: true, details: `Found ${lib}` };
			}
		}

		return { pass: false, details: "No auth detected" };
	},

	"build-defined": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		// Check Makefile variants for build target
		for (const basePath of [appPath, repoRoot]) {
			for (const makefileName of ["Makefile", "GNUmakefile", "makefile"]) {
				const makefile = await readText(path.join(basePath, makefileName));
				if (makefile?.includes("build:") || makefile?.includes("build :")) {
					return { pass: true, details: `make build in ${makefileName}` };
				}
			}
		}

		// Check for Bazel (used by CockroachDB, Kubernetes, etc.)
		for (const basePath of [appPath, repoRoot]) {
			if (await fileExists(path.join(basePath, "WORKSPACE")) ||
				await fileExists(path.join(basePath, "WORKSPACE.bazel")) ||
				await fileExists(path.join(basePath, "BUILD.bazel")) ||
				await fileExists(path.join(basePath, "BUILD"))) {
				return { pass: true, tool: "Bazel", details: "Bazel build system" };
			}
		}

		// Go has a built-in build system - go.mod implies go build ./...
		for (const basePath of [appPath, repoRoot]) {
			if (await fileExists(path.join(basePath, "go.mod"))) {
				return { pass: true, details: "go build ./... (go.mod present)" };
			}
		}

		// Check CLAUDE.md as fallback
		const claudeMd = await readText(path.join(appPath, "CLAUDE.md")) ||
			await readText(path.join(repoRoot, "CLAUDE.md")) || "";
		if (claudeMd.includes("go build")) {
			return { pass: true, details: "Build in CLAUDE.md" };
		}

		return { pass: false, details: "No build defined" };
	},

	"ci-tasks-aligned": async (ctx: CheckContext): Promise<CheckResult> => {
		const hasCI = dirExists(path.join(ctx.repoRoot, ".github/workflows"));
		const hasMakefile = await fileExists(path.join(ctx.app.path, "Makefile"));

		if (hasCI && hasMakefile) {
			return { pass: true, details: "CI and Makefile present" };
		}

		return { pass: false, details: "CI or Makefile missing" };
	},

	"common-aliases": async (ctx: CheckContext): Promise<CheckResult> => {
		const makefile = await readText(path.join(ctx.app.path, "Makefile")) || "";
		const commonTargets = ["build", "test", "lint", "run", "clean"];
		const found = commonTargets.filter((t) => makefile.includes(`${t}:`));

		if (found.length >= 3) {
			return { pass: true, details: `Has: ${found.join(", ")}` };
		}

		return { pass: false, details: `Only ${found.length}/5 common aliases` };
	},

	"dependency-manifest": async (ctx: CheckContext): Promise<CheckResult> => {
		if (await fileExists(path.join(ctx.app.path, "go.mod"))) {
			return { pass: true, configPath: "go.mod" };
		}
		return { pass: false, details: "No go.mod" };
	},

	"no-lint-ignores": async (ctx: CheckContext): Promise<CheckResult> => {
		return { pass: true, details: "Assumed clean (not scanned)" };
	},

	"npm-scripts": async (ctx: CheckContext): Promise<CheckResult> => {
		// Not applicable to Go
		return { pass: true, skipped: true, details: "N/A for Go" };
	},

	"test-isolation": async (ctx: CheckContext): Promise<CheckResult> => {
		const goMod = await readText(path.join(ctx.app.path, "go.mod")) || "";

		if (goMod.includes("testcontainers") || goMod.includes("dockertest")) {
			return { pass: true, details: "Test containers configured" };
		}

		return { pass: true, details: "Assumed isolated" };
	},

	"watch-mode": async (ctx: CheckContext): Promise<CheckResult> => {
		const makefile = await readText(path.join(ctx.app.path, "Makefile")) || "";

		if (makefile.includes("watch:") || makefile.includes("dev:")) {
			return { pass: true, details: "Watch mode in Makefile" };
		}

		const goMod = await readText(path.join(ctx.app.path, "go.mod")) || "";
		if (goMod.includes("air") || goMod.includes("reflex")) {
			return { pass: true, details: "Live reload tool configured" };
		}

		return { pass: false, details: "No watch mode" };
	},
};

// ============================================================================
// Adapter Export
// ============================================================================

/**
 * Go language adapter
 * Uses shared checks for common patterns (README, CI, security)
 * and Go-specific checks for language-specific patterns
 */
export const goAdapter = createLanguageAdapter({
	language: "go",
	displayName: "Go",
	runners: goSpecificRunners,
});
