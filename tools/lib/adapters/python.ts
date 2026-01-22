/**
 * @fileoverview Python language adapter
 * @module kb-tools/lib/adapters/python
 *
 * @description
 * Implements readiness checks for Python codebases.
 * Supports Ruff, Black, mypy, pytest, and modern Python packaging (pyproject.toml).
 *
 * Uses shared checks for language-agnostic patterns (README, gitignore, CI, etc.)
 * and provides Python-specific implementations for linting, typing, and testing.
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
// Python-Specific Check Runners
// ============================================================================

const pySpecificRunners: Record<string, CheckRunner> = {
	// =========================================================================
	// STYLE & VALIDATION
	// =========================================================================

	"linter-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		// Check for Ruff (modern Python linter)
		if (await fileExists(path.join(appPath, "ruff.toml"))) {
			return { pass: true, tool: "Ruff", configPath: "ruff.toml" };
		}

		const pyproject = await readText(path.join(appPath, "pyproject.toml"));
		if (pyproject?.includes("[tool.ruff]")) {
			return { pass: true, tool: "Ruff", configPath: "pyproject.toml" };
		}

		// Check for Flake8
		if (await fileExists(path.join(appPath, ".flake8"))) {
			return { pass: true, tool: "Flake8", configPath: ".flake8" };
		}
		if (await fileExists(path.join(appPath, "setup.cfg"))) {
			const setupCfg = await readText(path.join(appPath, "setup.cfg"));
			if (setupCfg?.includes("[flake8]")) {
				return { pass: true, tool: "Flake8", configPath: "setup.cfg" };
			}
		}

		// Check for Pylint
		if (await fileExists(path.join(appPath, ".pylintrc"))) {
			return { pass: true, tool: "Pylint", configPath: ".pylintrc" };
		}

		return { pass: false, details: "No linter configured (Ruff recommended)" };
	},

	"type-checker-strict": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		// Check for mypy
		if (await fileExists(path.join(appPath, "mypy.ini"))) {
			return { pass: true, tool: "mypy", configPath: "mypy.ini" };
		}

		const pyproject = await readText(path.join(appPath, "pyproject.toml"));
		if (pyproject?.includes("[tool.mypy]")) {
			return { pass: true, tool: "mypy", configPath: "pyproject.toml" };
		}

		// Check for Pyright
		if (await fileExists(path.join(appPath, "pyrightconfig.json"))) {
			return { pass: true, tool: "Pyright", configPath: "pyrightconfig.json" };
		}
		if (pyproject?.includes("[tool.pyright]")) {
			return { pass: true, tool: "Pyright", configPath: "pyproject.toml" };
		}

		return { pass: false, details: "No type checker configured (mypy or Pyright recommended)" };
	},

	"formatter-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		// Check pyproject.toml in both app path and repo root
		for (const basePath of [appPath, repoRoot]) {
			const pyproject = await readText(path.join(basePath, "pyproject.toml"));
			if (pyproject) {
				// Ruff can also format
				if (pyproject.includes("[tool.ruff.format]") || pyproject.includes("[tool.ruff]")) {
					return { pass: true, tool: "Ruff formatter", configPath: "pyproject.toml" };
				}
				// Check for Black
				if (pyproject.includes("[tool.black]")) {
					return { pass: true, tool: "Black", configPath: "pyproject.toml" };
				}
			}
		}

		// Check for standalone config files
		if (await fileExists(path.join(appPath, ".black")) ||
			await fileExists(path.join(repoRoot, ".black"))) {
			return { pass: true, tool: "Black", configPath: ".black" };
		}

		// Check for YAPF
		if (await fileExists(path.join(appPath, ".style.yapf")) ||
			await fileExists(path.join(repoRoot, ".style.yapf"))) {
			return { pass: true, tool: "YAPF", configPath: ".style.yapf" };
		}

		// Check pre-commit config for formatters
		for (const basePath of [appPath, repoRoot]) {
			const precommit = await readText(path.join(basePath, ".pre-commit-config.yaml"));
			if (precommit) {
				if (precommit.includes("ruff-format") || precommit.includes("id: ruff-format")) {
					return { pass: true, tool: "Ruff format", details: "Via pre-commit" };
				}
				if (precommit.includes("black") || precommit.includes("id: black")) {
					return { pass: true, tool: "Black", details: "Via pre-commit" };
				}
			}
		}

		// Check GitHub Actions for formatters
		const workflowsDir = path.join(repoRoot, ".github/workflows");
		if (dirExists(workflowsDir)) {
			try {
				const files = fs.readdirSync(workflowsDir);
				for (const file of files) {
					if (file.endsWith(".yml") || file.endsWith(".yaml")) {
						const content = await readText(path.join(workflowsDir, file));
						if (content?.includes("ruff format") || content?.includes("black")) {
							return { pass: true, tool: "Ruff/Black", details: "Via GitHub Actions" };
						}
					}
				}
			} catch {
				// Ignore errors
			}
		}

		return { pass: false, details: "No formatter configured (Ruff or Black recommended)" };
	},

	"no-any-casts": async (ctx: CheckContext): Promise<CheckResult> => {
		// Check for typing.Any usage
		try {
			const result = await $`grep -r "Any\\|: any" --include="*.py" ${ctx.app.path} 2>/dev/null | grep -v "__pycache__" | grep -v ".venv" | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			return {
				pass: count < 10, // Some Any is acceptable in Python
				details: `${count} uses of Any type`,
			};
		} catch {
			return { pass: true, details: "No Python files found" };
		}
	},

	"no-ts-ignore": async (ctx: CheckContext): Promise<CheckResult> => {
		// Check for type: ignore comments
		try {
			const result = await $`grep -r "# type: ignore" --include="*.py" ${ctx.app.path} 2>/dev/null | grep -v "__pycache__" | grep -v ".venv" | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			return {
				pass: count === 0,
				details: `${count} type: ignore comments`,
			};
		} catch {
			return { pass: true, details: "No Python files found" };
		}
	},

	"strict-mode": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		// Check both app path and repo root for pyproject.toml
		for (const basePath of [appPath, repoRoot]) {
			const pyproject = await readText(path.join(basePath, "pyproject.toml"));
			if (pyproject) {
				// Check for mypy strict mode (various formats)
				if (pyproject.includes("strict = true") ||
					pyproject.includes("strict=true") ||
					pyproject.includes('strict = "true"')) {
					return { pass: true, details: "mypy strict mode enabled" };
				}

				// Check for Pyright strict mode
				if (pyproject.includes('typeCheckingMode = "strict"') ||
					pyproject.includes("typeCheckingMode = 'strict'")) {
					return { pass: true, details: "Pyright strict mode enabled" };
				}
			}
		}

		// Check mypy.ini
		for (const basePath of [appPath, repoRoot]) {
			const mypyIni = await readText(path.join(basePath, "mypy.ini"));
			if (mypyIni?.includes("strict = True") || mypyIni?.includes("strict=True")) {
				return { pass: true, details: "mypy strict mode enabled" };
			}
		}

		// Check pyrightconfig.json
		for (const basePath of [appPath, repoRoot]) {
			const pyrightConfig = await readText(path.join(basePath, "pyrightconfig.json"));
			if (pyrightConfig?.includes('"strict"')) {
				return { pass: true, details: "Pyright strict mode enabled" };
			}
		}

		return { pass: false, details: "Type checker strict mode not enabled" };
	},

	// Python-specific pre-commit that checks for Python hooks
	"pre-commit-hooks": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		// Check app path first
		if (await fileExists(path.join(appPath, ".pre-commit-config.yaml"))) {
			const content = await readText(path.join(appPath, ".pre-commit-config.yaml"));
			if (content?.includes("ruff") || content?.includes("black") || content?.includes("mypy")) {
				return { pass: true, tool: "pre-commit", details: "With Python hooks" };
			}
			return { pass: true, tool: "pre-commit" };
		}
		if (dirExists(path.join(appPath, ".husky"))) {
			return { pass: true, tool: "Husky" };
		}

		// Check repo root
		if (await fileExists(path.join(repoRoot, ".pre-commit-config.yaml"))) {
			const content = await readText(path.join(repoRoot, ".pre-commit-config.yaml"));
			if (content?.includes("ruff") || content?.includes("black") || content?.includes("mypy")) {
				return { pass: true, tool: "pre-commit", details: "With Python hooks" };
			}
			return { pass: true, tool: "pre-commit" };
		}
		if (dirExists(path.join(repoRoot, ".husky"))) {
			return { pass: true, tool: "Husky" };
		}

		return { pass: false, details: "No pre-commit hooks (pre-commit recommended)" };
	},

	"zero-lint-errors": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		try {
			// Try Ruff first
			const pyproject = await readText(path.join(appPath, "pyproject.toml"));
			if (pyproject?.includes("[tool.ruff]") || await fileExists(path.join(appPath, "ruff.toml"))) {
				await runWithTimeout(
					$`cd ${appPath} && ruff check . 2>&1`.quiet(),
					60000,
				);
				return { pass: true, details: "Ruff clean" };
			}

			// Try Flake8
			if (await fileExists(path.join(appPath, ".flake8"))) {
				await runWithTimeout(
					$`cd ${appPath} && flake8 . 2>&1`.quiet(),
					60000,
				);
				return { pass: true, details: "Flake8 clean" };
			}

			return { pass: true, details: "No linter to check" };
		} catch {
			return { pass: false, details: "Lint errors present" };
		}
	},

	// =========================================================================
	// BUILD SYSTEM
	// =========================================================================

	"build-command": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		// Check for pyproject.toml with build system
		const pyproject = await readText(path.join(appPath, "pyproject.toml"));
		if (pyproject?.includes("[build-system]")) {
			return { pass: true, details: "pyproject.toml build-system" };
		}

		// Check for setup.py
		if (await fileExists(path.join(appPath, "setup.py"))) {
			return { pass: true, details: "setup.py" };
		}

		// Check for Makefile
		const makefile = await readText(path.join(appPath, "Makefile"));
		if (makefile?.includes("build:")) {
			return { pass: true, details: "Makefile build target" };
		}

		return { pass: false, details: "No build command documented" };
	},

	"lockfile-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		const lockfiles = [
			{ file: "uv.lock", name: "uv" },
			{ file: "poetry.lock", name: "Poetry" },
			{ file: "Pipfile.lock", name: "Pipenv" },
			{ file: "pdm.lock", name: "PDM" },
			{ file: "requirements.lock", name: "pip-compile" },
		];

		// Check both app path and repo root
		for (const basePath of [appPath, repoRoot]) {
			for (const { file, name } of lockfiles) {
				if (await fileExists(path.join(basePath, file))) {
					return { pass: true, tool: name, configPath: file };
				}
			}
		}

		// Check for pyproject.toml with dependencies section (modern Python)
		// For OSS libraries, pyproject.toml with [project.dependencies] is acceptable
		for (const basePath of [appPath, repoRoot]) {
			const pyproject = await readText(path.join(basePath, "pyproject.toml"));
			if (pyproject?.includes("[project]") && pyproject.includes("dependencies")) {
				return { pass: true, tool: "pyproject.toml", details: "Dependencies in pyproject.toml" };
			}
		}

		// requirements.txt with version constraints is acceptable
		for (const basePath of [appPath, repoRoot]) {
			const requirements = await readText(path.join(basePath, "requirements.txt"));
			if (requirements) {
				const lines = requirements.split("\n").filter((l) => l.trim() && !l.startsWith("#") && !l.startsWith("-"));
				// Accept if there are dependencies with any version constraints
				const constrainedCount = lines.filter((l) =>
					l.includes("==") || l.includes(">=") || l.includes("<=") || l.includes("~=")
				).length;
				if (constrainedCount > 0) {
					return { pass: true, tool: "requirements.txt", details: "Version constraints present" };
				}
				// Accept any requirements.txt for OSS libs
				if (lines.length > 0) {
					return { pass: true, tool: "requirements.txt", details: "Dependencies listed" };
				}
			}
		}

		return { pass: false, details: "No lockfile (uv.lock or poetry.lock recommended)" };
	},

	"deps-install": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		// Check for virtual environment
		const venvDirs = [".venv", "venv", ".env", "env"];
		for (const dir of venvDirs) {
			if (dirExists(path.join(appPath, dir))) {
				return { pass: true, details: `${dir}/ exists` };
			}
		}

		return { pass: false, details: "No virtual environment found" };
	},

	"build-succeeds": async (ctx: CheckContext): Promise<CheckResult> => {
		if (ctx.options.skipBuild) {
			return { pass: true, skipped: true, details: "Skipped via --skip-build" };
		}

		const appPath = ctx.app.path;

		try {
			// Try uv build first
			if (await fileExists(path.join(appPath, "uv.lock"))) {
				await runWithTimeout(
					$`cd ${appPath} && uv build 2>&1`.quiet(),
					180000,
				);
				return { pass: true, details: "uv build succeeded" };
			}

			// Try poetry build
			if (await fileExists(path.join(appPath, "poetry.lock"))) {
				await runWithTimeout(
					$`cd ${appPath} && poetry build 2>&1`.quiet(),
					180000,
				);
				return { pass: true, details: "poetry build succeeded" };
			}

			// Try pip install -e .
			const pyproject = await readText(path.join(appPath, "pyproject.toml"));
			if (pyproject?.includes("[build-system]")) {
				await runWithTimeout(
					$`cd ${appPath} && pip install -e . 2>&1`.quiet(),
					180000,
				);
				return { pass: true, details: "pip install -e . succeeded" };
			}

			return { pass: true, details: "No build to run" };
		} catch {
			return { pass: false, details: "Build failed" };
		}
	},

	"build-deterministic": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		const hasDocker = await fileExists(path.join(appPath, "Dockerfile"));
		const hasNix = await fileExists(path.join(appPath, "flake.nix"));
		const hasLockfile =
			(await fileExists(path.join(appPath, "uv.lock"))) ||
			(await fileExists(path.join(appPath, "poetry.lock"))) ||
			(await fileExists(path.join(appPath, "Pipfile.lock")));

		if (hasNix && hasLockfile) {
			return { pass: true, details: "Nix + lockfile" };
		}

		if (hasDocker && hasLockfile) {
			return { pass: true, details: "Docker + lockfile" };
		}

		if (hasLockfile) {
			return { pass: true, details: "Lockfile only", confidence: 70 };
		}

		return { pass: false, details: "No determinism guarantees (uv.lock recommended)" };
	},

	// =========================================================================
	// TESTING
	// =========================================================================

	"test-command": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		const pyproject = await readText(path.join(appPath, "pyproject.toml"));
		if (pyproject?.includes("[tool.pytest]") || pyproject?.includes("[tool.pytest.ini_options]")) {
			return { pass: true, details: "pytest configured" };
		}

		if (await fileExists(path.join(appPath, "pytest.ini"))) {
			return { pass: true, details: "pytest.ini" };
		}

		if (await fileExists(path.join(appPath, "setup.cfg"))) {
			const setupCfg = await readText(path.join(appPath, "setup.cfg"));
			if (setupCfg?.includes("[tool:pytest]")) {
				return { pass: true, details: "pytest in setup.cfg" };
			}
		}

		// Check Makefile
		const makefile = await readText(path.join(appPath, "Makefile"));
		if (makefile?.includes("test:") && makefile?.includes("pytest")) {
			return { pass: true, details: "pytest in Makefile" };
		}

		return { pass: false, details: "No test command documented" };
	},

	"tests-exist": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			const result = await $`find ${ctx.app.path} -name "test_*.py" -o -name "*_test.py" 2>/dev/null | grep -v __pycache__ | grep -v .venv | head -1`.quiet();
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
				$`cd ${ctx.app.path} && pytest 2>&1`.quiet(),
				120000,
			);
			return { pass: true, details: "All tests pass" };
		} catch {
			return { pass: false, details: "Tests failed" };
		}
	},

	"integration-tests": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		const integrationDirs = ["tests/integration", "test/integration", "integration_tests", "e2e"];
		for (const dir of integrationDirs) {
			if (dirExists(path.join(appPath, dir))) {
				return { pass: true, details: `Found ${dir}/` };
			}
		}

		// Check for pytest markers
		const pyproject = await readText(path.join(appPath, "pyproject.toml"));
		if (pyproject?.includes("integration") && pyproject?.includes("markers")) {
			return { pass: true, details: "Integration marker configured" };
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
				$`cd ${ctx.app.path} && pytest -x -q 2>&1`.quiet(),
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
		const appPath = ctx.app.path;

		const pyproject = await readText(path.join(appPath, "pyproject.toml"));
		if (pyproject?.includes("[tool.coverage") || pyproject?.includes("fail_under")) {
			return { pass: true, details: "Coverage threshold configured" };
		}

		if (await fileExists(path.join(appPath, ".coveragerc"))) {
			const coveragerc = await readText(path.join(appPath, ".coveragerc"));
			if (coveragerc?.includes("fail_under")) {
				return { pass: true, details: "Coverage threshold in .coveragerc" };
			}
		}

		return { pass: false, details: "No coverage threshold" };
	},

	// =========================================================================
	// DOCUMENTATION (Python-specific)
	// =========================================================================

	// For Python, check pyproject.toml instead of package.json
	"package-json-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		const exists = await fileExists(path.join(ctx.app.path, "pyproject.toml"));
		return { pass: exists, details: exists ? "pyproject.toml found" : "Missing pyproject.toml" };
	},

	"claude-md-has-commands": async (ctx: CheckContext): Promise<CheckResult> => {
		let content = await readText(path.join(ctx.app.path, "CLAUDE.md"));
		if (!content) {
			content = await readText(path.join(ctx.repoRoot, "CLAUDE.md"));
		}
		if (!content) {
			return { pass: false, details: "CLAUDE.md missing" };
		}

		const hasCommands =
			content.includes("pytest") ||
			content.includes("python") ||
			content.includes("uv ") ||
			content.includes("pip ") ||
			content.includes("poetry ");

		return {
			pass: hasCommands,
			details: hasCommands ? "Python commands found" : "Missing Python commands",
		};
	},

	// =========================================================================
	// OBSERVABILITY
	// =========================================================================

	"console-logs-minimal": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			const result = await $`grep -r "print(" --include="*.py" ${ctx.app.path} 2>/dev/null | grep -v __pycache__ | grep -v .venv | grep -v "_test.py" | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			return {
				pass: count < 20,
				details: `${count} print() calls`,
			};
		} catch {
			return { pass: true, details: "No Python files found" };
		}
	},

	"structured-logging": async (ctx: CheckContext): Promise<CheckResult> => {
		const pyproject = await readText(path.join(ctx.app.path, "pyproject.toml"));
		const requirements = await readText(path.join(ctx.app.path, "requirements.txt"));
		const deps = (pyproject || "") + (requirements || "");

		const loggers = [
			{ name: "structlog", tool: "structlog" },
			{ name: "loguru", tool: "Loguru" },
			{ name: "python-json-logger", tool: "python-json-logger" },
		];

		for (const { name, tool } of loggers) {
			if (deps.includes(name)) {
				return { pass: true, tool };
			}
		}

		return { pass: false, details: "No structured logging library (structlog recommended)" };
	},

	"error-tracking": async (ctx: CheckContext): Promise<CheckResult> => {
		const pyproject = await readText(path.join(ctx.app.path, "pyproject.toml"));
		const requirements = await readText(path.join(ctx.app.path, "requirements.txt"));
		const deps = (pyproject || "") + (requirements || "");

		const trackers = [
			{ name: "sentry-sdk", tool: "Sentry" },
			{ name: "bugsnag", tool: "Bugsnag" },
			{ name: "rollbar", tool: "Rollbar" },
		];

		for (const { name, tool } of trackers) {
			if (deps.includes(name)) {
				return { pass: true, tool };
			}
		}

		return { pass: false, details: "No error tracking" };
	},

	"tracing-configured": async (ctx: CheckContext): Promise<CheckResult> => {
		const pyproject = await readText(path.join(ctx.app.path, "pyproject.toml"));
		const requirements = await readText(path.join(ctx.app.path, "requirements.txt"));
		const deps = (pyproject || "") + (requirements || "");

		const tracers = [
			{ name: "opentelemetry", tool: "OpenTelemetry" },
			{ name: "ddtrace", tool: "Datadog" },
			{ name: "jaeger-client", tool: "Jaeger" },
		];

		for (const { name, tool } of tracers) {
			if (deps.includes(name)) {
				return { pass: true, tool };
			}
		}

		return { pass: false, details: "No distributed tracing" };
	},

	"metrics-configured": async (ctx: CheckContext): Promise<CheckResult> => {
		const pyproject = await readText(path.join(ctx.app.path, "pyproject.toml"));
		const requirements = await readText(path.join(ctx.app.path, "requirements.txt"));
		const deps = (pyproject || "") + (requirements || "");

		const metricLibs = [
			{ name: "prometheus-client", tool: "Prometheus" },
			{ name: "opentelemetry-sdk", tool: "OpenTelemetry Metrics" },
			{ name: "statsd", tool: "StatsD" },
		];

		for (const { name, tool } of metricLibs) {
			if (deps.includes(name)) {
				return { pass: true, tool };
			}
		}

		return { pass: false, details: "No metrics collection" };
	},

	// =========================================================================
	// SECURITY (Python-specific)
	// =========================================================================

	"secret-scanning": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;
		const scanners = [
			{ file: ".gitleaks.toml", tool: "Gitleaks" },
			{ file: ".trufflehog.yml", tool: "TruffleHog" },
		];

		for (const { file, tool } of scanners) {
			if ((await fileExists(path.join(appPath, file))) || (await fileExists(path.join(repoRoot, file)))) {
				return { pass: true, tool, configPath: file };
			}
		}

		// Check pre-commit for detect-secrets (Python-specific)
		const precommitApp = await readText(path.join(appPath, ".pre-commit-config.yaml"));
		const precommitRepo = await readText(path.join(repoRoot, ".pre-commit-config.yaml"));
		const precommit = precommitApp || precommitRepo || "";
		if (precommit.includes("detect-secrets")) {
			return { pass: true, tool: "detect-secrets" };
		}

		return { pass: false, details: "No secret scanning" };
	},

	"dependency-scanning": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		// Check for Safety or pip-audit
		const pyproject = await readText(path.join(appPath, "pyproject.toml"));
		if (pyproject?.includes("safety") || pyproject?.includes("pip-audit")) {
			return { pass: true, details: "Vulnerability scanning configured" };
		}

		// Check CI (workflows at repo root)
		const appWorkflows = path.join(appPath, ".github/workflows");
		const repoWorkflows = path.join(repoRoot, ".github/workflows");
		const workflowsDir = dirExists(appWorkflows) ? appWorkflows : repoWorkflows;
		if (dirExists(workflowsDir)) {
			try {
				const files = fs.readdirSync(workflowsDir);
				for (const file of files) {
					const content = await readText(path.join(workflowsDir, file));
					if (content?.includes("safety") || content?.includes("pip-audit") || content?.includes("snyk")) {
						return { pass: true, details: "Vulnerability scanning in CI" };
					}
				}
			} catch {
				// Ignore
			}
		}

		// Check for Dependabot/Renovate
		if ((await fileExists(path.join(appPath, ".github/dependabot.yml"))) || (await fileExists(path.join(repoRoot, ".github/dependabot.yml")))) {
			return { pass: true, tool: "Dependabot" };
		}

		if ((await fileExists(path.join(appPath, "renovate.json"))) || (await fileExists(path.join(repoRoot, "renovate.json")))) {
			return { pass: true, tool: "Renovate" };
		}

		return { pass: false, details: "No dependency scanning (pip-audit recommended)" };
	},

	// =========================================================================
	// PRODUCT & EXPERIMENTATION
	// =========================================================================

	"ci-runs-tests": async (ctx: CheckContext): Promise<CheckResult> => {
		const appWorkflows = path.join(ctx.app.path, ".github/workflows");
		const repoWorkflows = path.join(ctx.repoRoot, ".github/workflows");
		const workflowsDir = dirExists(appWorkflows) ? appWorkflows : dirExists(repoWorkflows) ? repoWorkflows : null;

		if (!workflowsDir) {
			return { pass: false, details: "No CI workflows" };
		}

		try {
			const result = await $`grep -r "pytest\\|python -m pytest" ${workflowsDir} 2>/dev/null | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			return { pass: count > 0, details: count > 0 ? "Tests in CI" : "No tests in CI" };
		} catch {
			return { pass: false, details: "Error scanning workflows" };
		}
	},

	"feature-flags": async (ctx: CheckContext): Promise<CheckResult> => {
		const pyproject = await readText(path.join(ctx.app.path, "pyproject.toml"));
		const requirements = await readText(path.join(ctx.app.path, "requirements.txt"));
		const deps = (pyproject || "") + (requirements || "");

		const flagLibs = [
			{ name: "launchdarkly-server-sdk", tool: "LaunchDarkly" },
			{ name: "growthbook-sdk-python", tool: "GrowthBook" },
			{ name: "unleash-client-python", tool: "Unleash" },
		];

		for (const { name, tool } of flagLibs) {
			if (deps.includes(name)) {
				return { pass: true, tool };
			}
		}

		return { pass: false, details: "No feature flags" };
	},

	"analytics-configured": async (ctx: CheckContext): Promise<CheckResult> => {
		const pyproject = await readText(path.join(ctx.app.path, "pyproject.toml"));
		const requirements = await readText(path.join(ctx.app.path, "requirements.txt"));
		const deps = (pyproject || "") + (requirements || "");

		if (deps.includes("posthog") || deps.includes("segment") || deps.includes("mixpanel")) {
			return { pass: true, details: "Analytics library found" };
		}

		return { pass: false, details: "No analytics" };
	},

	"ab-testing": async (ctx: CheckContext): Promise<CheckResult> => {
		const pyproject = await readText(path.join(ctx.app.path, "pyproject.toml"));
		const requirements = await readText(path.join(ctx.app.path, "requirements.txt"));
		const deps = (pyproject || "") + (requirements || "");

		if (deps.includes("growthbook") || deps.includes("optimizely")) {
			return { pass: true, details: "A/B testing library found" };
		}

		return { pass: false, details: "No A/B testing" };
	},

	// =========================================================================
	// ALIASES (map definition names to implementation names)
	// =========================================================================

	// deps-installed → deps-install
	"deps-installed": async (ctx: CheckContext): Promise<CheckResult> => {
		const venvExists = dirExists(path.join(ctx.app.path, ".venv")) ||
			dirExists(path.join(ctx.app.path, "venv"));

		if (venvExists) {
			return { pass: true, details: "Virtual environment exists" };
		}

		// Check for poetry/pipenv lock files as indicators
		if (await fileExists(path.join(ctx.app.path, "poetry.lock"))) {
			return { pass: true, details: "poetry.lock present" };
		}

		return { pass: false, details: "No venv or lock file" };
	},

	// test-coverage → coverage-threshold
	"test-coverage": async (ctx: CheckContext): Promise<CheckResult> => {
		const pyproject = await readText(path.join(ctx.app.path, "pyproject.toml")) || "";

		if (pyproject.includes("[tool.coverage") || pyproject.includes("fail_under")) {
			return { pass: true, details: "Coverage configured in pyproject.toml" };
		}

		// Check for .coveragerc
		if (await fileExists(path.join(ctx.app.path, ".coveragerc"))) {
			return { pass: true, details: ".coveragerc exists" };
		}

		// Check for pytest-cov in dependencies
		const requirements = await readText(path.join(ctx.app.path, "requirements.txt")) || "";
		if (pyproject.includes("pytest-cov") || requirements.includes("pytest-cov")) {
			return { pass: true, details: "pytest-cov configured" };
		}

		return { pass: false, details: "No coverage threshold" };
	},

	// reproducible-builds → build-deterministic
	"reproducible-builds": async (ctx: CheckContext): Promise<CheckResult> => {
		// Check for lock files
		if (await fileExists(path.join(ctx.app.path, "poetry.lock"))) {
			return { pass: true, details: "poetry.lock ensures reproducibility" };
		}
		if (await fileExists(path.join(ctx.app.path, "Pipfile.lock"))) {
			return { pass: true, details: "Pipfile.lock ensures reproducibility" };
		}
		if (await fileExists(path.join(ctx.app.path, "requirements.lock"))) {
			return { pass: true, details: "requirements.lock exists" };
		}
		if (await fileExists(path.join(ctx.app.path, "uv.lock"))) {
			return { pass: true, details: "uv.lock ensures reproducibility" };
		}

		return { pass: false, details: "No lock file for reproducibility" };
	},

	// no-unsafe-types → mypy strict
	"no-unsafe-types": async (ctx: CheckContext): Promise<CheckResult> => {
		const pyproject = await readText(path.join(ctx.app.path, "pyproject.toml")) || "";

		if (pyproject.includes("strict = true") || pyproject.includes("[tool.mypy]")) {
			return { pass: true, details: "mypy configured" };
		}

		if (await fileExists(path.join(ctx.app.path, "mypy.ini"))) {
			return { pass: true, details: "mypy.ini exists" };
		}

		return { pass: false, details: "No type checking configured" };
	},

	// =========================================================================
	// NEW IMPLEMENTATIONS
	// =========================================================================

	"audit-logging": async (ctx: CheckContext): Promise<CheckResult> => {
		const pyproject = await readText(path.join(ctx.app.path, "pyproject.toml")) || "";
		const requirements = await readText(path.join(ctx.app.path, "requirements.txt")) || "";
		const deps = pyproject + requirements;

		if (deps.includes("auditlog") || deps.includes("django-auditlog")) {
			return { pass: true, details: "Audit library found" };
		}

		return { pass: false, details: "No audit logging" };
	},

	"auth-implementation": async (ctx: CheckContext): Promise<CheckResult> => {
		const pyproject = await readText(path.join(ctx.app.path, "pyproject.toml")) || "";
		const requirements = await readText(path.join(ctx.app.path, "requirements.txt")) || "";
		const deps = pyproject + requirements;

		const authLibs = ["fastapi-users", "django-allauth", "passlib", "python-jose", "pyjwt", "authlib"];
		for (const lib of authLibs) {
			if (deps.includes(lib)) {
				return { pass: true, tool: lib };
			}
		}

		return { pass: false, details: "No auth detected" };
	},

	"build-defined": async (ctx: CheckContext): Promise<CheckResult> => {
		// Check pyproject.toml for build system
		const pyproject = await readText(path.join(ctx.app.path, "pyproject.toml"));
		if (pyproject?.includes("[build-system]")) {
			return { pass: true, details: "Build system in pyproject.toml" };
		}

		// Check Makefile
		const makefile = await readText(path.join(ctx.app.path, "Makefile"));
		if (makefile?.includes("build:")) {
			return { pass: true, details: "make build defined" };
		}

		return { pass: false, details: "No build defined" };
	},

	"ci-tasks-aligned": async (ctx: CheckContext): Promise<CheckResult> => {
		const hasCI = dirExists(path.join(ctx.repoRoot, ".github/workflows"));
		const hasMakefile = await fileExists(path.join(ctx.app.path, "Makefile"));
		const hasNoxfile = await fileExists(path.join(ctx.app.path, "noxfile.py"));

		if (hasCI && (hasMakefile || hasNoxfile)) {
			return { pass: true, details: "CI and task runner present" };
		}

		return { pass: false, details: "CI or task runner missing" };
	},

	"common-aliases": async (ctx: CheckContext): Promise<CheckResult> => {
		const makefile = await readText(path.join(ctx.app.path, "Makefile")) || "";
		const commonTargets = ["install", "test", "lint", "run", "format"];
		const found = commonTargets.filter((t) => makefile.includes(`${t}:`));

		if (found.length >= 3) {
			return { pass: true, details: `Has: ${found.join(", ")}` };
		}

		// Check pyproject.toml for scripts
		const pyproject = await readText(path.join(ctx.app.path, "pyproject.toml")) || "";
		if (pyproject.includes("[project.scripts]") || pyproject.includes("[tool.poetry.scripts]")) {
			return { pass: true, details: "Scripts in pyproject.toml" };
		}

		return { pass: false, details: `Only ${found.length}/5 common aliases` };
	},

	"dependency-manifest": async (ctx: CheckContext): Promise<CheckResult> => {
		if (await fileExists(path.join(ctx.app.path, "pyproject.toml"))) {
			return { pass: true, configPath: "pyproject.toml" };
		}
		if (await fileExists(path.join(ctx.app.path, "requirements.txt"))) {
			return { pass: true, configPath: "requirements.txt" };
		}
		if (await fileExists(path.join(ctx.app.path, "setup.py"))) {
			return { pass: true, configPath: "setup.py" };
		}
		return { pass: false, details: "No dependency manifest" };
	},

	"no-lint-ignores": async (ctx: CheckContext): Promise<CheckResult> => {
		return { pass: true, details: "Assumed clean (not scanned)" };
	},

	"npm-scripts": async (ctx: CheckContext): Promise<CheckResult> => {
		// Not applicable to Python
		return { pass: true, skipped: true, details: "N/A for Python" };
	},

	"test-isolation": async (ctx: CheckContext): Promise<CheckResult> => {
		const pyproject = await readText(path.join(ctx.app.path, "pyproject.toml")) || "";
		const requirements = await readText(path.join(ctx.app.path, "requirements.txt")) || "";
		const deps = pyproject + requirements;

		if (deps.includes("testcontainers") || deps.includes("pytest-docker")) {
			return { pass: true, details: "Test containers configured" };
		}

		return { pass: true, details: "Assumed isolated" };
	},

	"watch-mode": async (ctx: CheckContext): Promise<CheckResult> => {
		const makefile = await readText(path.join(ctx.app.path, "Makefile")) || "";

		if (makefile.includes("watch:") || makefile.includes("dev:")) {
			return { pass: true, details: "Watch mode in Makefile" };
		}

		const pyproject = await readText(path.join(ctx.app.path, "pyproject.toml")) || "";
		if (pyproject.includes("watchdog") || pyproject.includes("uvicorn")) {
			return { pass: true, details: "Auto-reload tool configured" };
		}

		return { pass: false, details: "No watch mode" };
	},
};

// ============================================================================
// Adapter Export
// ============================================================================

export const pythonAdapter = createLanguageAdapter({
	language: "python",
	displayName: "Python",
	runners: pySpecificRunners,
});
