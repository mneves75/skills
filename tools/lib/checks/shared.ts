/**
 * @fileoverview Shared check implementations
 * @module kb-tools/lib/checks/shared
 *
 * @description
 * Contains language-agnostic check implementations that are shared across
 * all language adapters. Eliminates duplication by extracting common patterns
 * for file existence, documentation, CI, and security checks.
 *
 * Uses the dependency parsing module for library detection across languages.
 */

import { $ } from "bun";
import path from "node:path";
import {
	type CheckRunner,
	type CheckContext,
	type CheckResult,
	fileExists,
	readText,
	dirExists,
} from "../check-registry.js";
import {
	parseDependencies,
	hasLibraryCategory,
	type DependencyManifest,
} from "../readiness/deps/index.js";

// ============================================================================
// Check Factory Utilities
// ============================================================================

/**
 * Options for createPathCheck factory
 */
interface PathCheckOptions {
	/** Check both app path and repo root (default: false) */
	checkBothPaths?: boolean;
	/** Key to use for the config path in result (default: "configPath") */
	resultKey?: "configPath" | "tool";
	/** Value to use for result key */
	resultValue?: string;
	/** Custom details message on success */
	successDetails?: string;
	/** Custom details message on failure */
	failureDetails?: string;
}

/**
 * Creates a check that looks for files in specified paths
 * Uses the file cache from context to reduce redundant I/O
 */
export function createPathCheck(
	files: string[],
	options: PathCheckOptions = {}
): CheckRunner {
	const {
		checkBothPaths = false,
		resultKey = "configPath",
		successDetails = "Found",
		failureDetails = "Missing",
	} = options;

	return async (ctx: CheckContext): Promise<CheckResult> => {
		const pathsToCheck = checkBothPaths
			? [ctx.app.path, ctx.repoRoot]
			: [ctx.app.path];

		// Use cache if available, otherwise fall back to direct check
		const checkExists = ctx.cache
			? (p: string) => ctx.cache.exists(p)
			: fileExists;

		for (const basePath of pathsToCheck) {
			for (const file of files) {
				if (await checkExists(path.join(basePath, file))) {
					const result: CheckResult = { pass: true, details: successDetails };
					if (resultKey === "configPath") {
						result.configPath = file;
					} else if (resultKey === "tool" && options.resultValue) {
						result.tool = options.resultValue;
					}
					return result;
				}
			}
		}

		return { pass: false, details: failureDetails };
	};
}

/**
 * Creates a check that looks for directories in specified paths
 */
export function createDirCheck(
	dirs: string[],
	options: PathCheckOptions = {}
): CheckRunner {
	const {
		checkBothPaths = false,
		resultKey = "configPath",
		successDetails = "Found",
		failureDetails = "Missing",
	} = options;

	return async (ctx: CheckContext): Promise<CheckResult> => {
		const pathsToCheck = checkBothPaths
			? [ctx.app.path, ctx.repoRoot]
			: [ctx.app.path];

		for (const basePath of pathsToCheck) {
			for (const dir of dirs) {
				if (dirExists(path.join(basePath, dir))) {
					const result: CheckResult = { pass: true, details: successDetails };
					if (resultKey === "configPath") {
						result.configPath = dir;
					}
					return result;
				}
			}
		}

		return { pass: false, details: failureDetails };
	};
}

// ============================================================================
// Shared Check Implementations
// ============================================================================

export const sharedChecks: Record<string, CheckRunner> = {
	// =========================================================================
	// DOCUMENTATION
	// =========================================================================

	"readme-exists": createPathCheck(
		["README.md", "readme.md", "Readme.md"],
		{ checkBothPaths: true }
	),

	"gitignore-exists": createPathCheck(
		[".gitignore"],
		{ checkBothPaths: true }
	),

	"claude-md-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		// Check for CLAUDE.md or AGENTS.md (agent-optimized)
		const claudeMdApp = await fileExists(path.join(appPath, "CLAUDE.md"));
		const agentsMdApp = await fileExists(path.join(appPath, "AGENTS.md"));
		const claudeMdRepo = await fileExists(path.join(repoRoot, "CLAUDE.md"));
		const agentsMdRepo = await fileExists(path.join(repoRoot, "AGENTS.md"));

		if (claudeMdApp || claudeMdRepo) {
			return { pass: true, details: "CLAUDE.md" };
		}
		if (agentsMdApp || agentsMdRepo) {
			return { pass: true, details: "AGENTS.md" };
		}

		// For OSS projects: Accept good documentation as equivalent
		// A project with README + CONTRIBUTING + docs/ provides agent context
		const hasReadme = (await fileExists(path.join(appPath, "README.md"))) ||
			(await fileExists(path.join(repoRoot, "README.md")));
		const hasContributing = (await fileExists(path.join(appPath, "CONTRIBUTING.md"))) ||
			(await fileExists(path.join(repoRoot, "CONTRIBUTING.md")));
		const hasDocs = dirExists(path.join(appPath, "docs")) ||
			dirExists(path.join(repoRoot, "docs")) ||
			dirExists(path.join(appPath, "doc")) ||
			dirExists(path.join(repoRoot, "doc"));

		if (hasReadme && (hasContributing || hasDocs)) {
			return { pass: true, details: "README + docs (OSS equivalent)" };
		}

		return { pass: false, details: "Missing agent context docs" };
	},

	"claude-md-concise": async (ctx: CheckContext): Promise<CheckResult> => {
		// Check CLAUDE.md first
		let content = await readText(path.join(ctx.app.path, "CLAUDE.md"));
		if (!content) {
			content = await readText(path.join(ctx.repoRoot, "CLAUDE.md"));
		}

		if (content) {
			const lines = content.split("\n").length;
			return {
				pass: lines < 300,
				details: `${lines} lines`,
			};
		}

		// For OSS: Check README is well-structured (concise by section)
		const readme = await readText(path.join(ctx.app.path, "README.md")) ||
			await readText(path.join(ctx.repoRoot, "README.md"));

		if (readme) {
			const lines = readme.split("\n").length;
			// README can be longer, but should have structure
			const hasHeadings = (readme.match(/^#{1,3}\s/gm) || []).length >= 3;
			if (hasHeadings) {
				return { pass: true, details: `README: ${lines} lines, structured` };
			}
		}

		return { pass: false, details: "No structured docs" };
	},

	"claude-md-recent": async (ctx: CheckContext): Promise<CheckResult> => {
		// Check CLAUDE.md first
		const appClaudeMd = path.join(ctx.app.path, "CLAUDE.md");
		const repoClaudeMd = path.join(ctx.repoRoot, "CLAUDE.md");

		let docPath: string | null = null;
		if (await fileExists(appClaudeMd)) docPath = appClaudeMd;
		else if (await fileExists(repoClaudeMd)) docPath = repoClaudeMd;

		// Fallback to README for OSS projects
		if (!docPath) {
			const appReadme = path.join(ctx.app.path, "README.md");
			const repoReadme = path.join(ctx.repoRoot, "README.md");
			if (await fileExists(appReadme)) docPath = appReadme;
			else if (await fileExists(repoReadme)) docPath = repoReadme;
		}

		if (!docPath) {
			return { pass: false, details: "No docs found" };
		}

		try {
			const result = await $`cd ${ctx.repoRoot} && git log -1 --format=%ct -- ${docPath} 2>/dev/null`.quiet();
			const timestamp = Number.parseInt(result.text().trim(), 10);
			if (Number.isNaN(timestamp)) {
				return { pass: false, details: "No git history" };
			}

			const daysSince = (Date.now() / 1000 - timestamp) / 86400;
			// OSS projects: 90 days is acceptable (vs 30 for CLAUDE.md)
			const threshold = docPath.includes("CLAUDE.md") ? 30 : 90;
			return {
				pass: daysSince < threshold,
				details: `${Math.floor(daysSince)} days ago`,
			};
		} catch {
			return { pass: false, details: "No git history" };
		}
	},

	"contributing-guide": createPathCheck(
		["CONTRIBUTING.md"],
		{ checkBothPaths: true }
	),

	// =========================================================================
	// DEVELOPMENT ENVIRONMENT
	// =========================================================================

	"editorconfig-exists": createPathCheck(
		[".editorconfig"],
		{ checkBothPaths: true }
	),

	"devcontainer-exists": createPathCheck(
		[".devcontainer/devcontainer.json", ".devcontainer.json"],
		{ checkBothPaths: true, successDetails: "Found", failureDetails: "Not configured" }
	),

	"env-example": createPathCheck(
		[".env.example", ".env.template", ".env.sample"],
		{ checkBothPaths: true, successDetails: "Found", failureDetails: "No .env.example" }
	),

	"docker-compose": createPathCheck(
		["docker-compose.yml", "docker-compose.yaml", "compose.yml", "compose.yaml"],
		{ checkBothPaths: true, successDetails: "Found", failureDetails: "Not configured" }
	),

	// =========================================================================
	// SECURITY
	// =========================================================================

	"git-initialized": async (ctx: CheckContext): Promise<CheckResult> => {
		const exists = dirExists(path.join(ctx.repoRoot, ".git"));
		return { pass: exists, details: exists ? "Yes" : "No" };
	},

	"no-secrets-in-repo": async (ctx: CheckContext): Promise<CheckResult> => {
		const hasEnvFile = await fileExists(path.join(ctx.app.path, ".env"));
		const hasCredentials = await fileExists(path.join(ctx.app.path, "credentials.json"));
		const suspicious = hasEnvFile || hasCredentials;
		return {
			pass: !suspicious,
			details: suspicious ? "Potential secrets found" : "No obvious secrets",
		};
	},

	"secret-scanning": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		const scanners = [
			{ file: ".gitleaks.toml", tool: "Gitleaks" },
			{ file: ".trufflehog.yml", tool: "TruffleHog" },
			{ file: ".gitguardian.yaml", tool: "GitGuardian" },
		];

		for (const { file, tool } of scanners) {
			if ((await fileExists(path.join(appPath, file))) ||
				(await fileExists(path.join(repoRoot, file)))) {
				return { pass: true, tool, configPath: file };
			}
		}

		return { pass: false, details: "No secret scanning configured" };
	},

	"codeowners-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;
		const locations = ["CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS"];

		for (const loc of locations) {
			if ((await fileExists(path.join(appPath, loc))) ||
				(await fileExists(path.join(repoRoot, loc)))) {
				return { pass: true, configPath: loc };
			}
		}

		return { pass: false, details: "Missing CODEOWNERS" };
	},

	"branch-protection-documented": async (ctx: CheckContext): Promise<CheckResult> => {
		const claudeMdApp = await readText(path.join(ctx.app.path, "CLAUDE.md"));
		const claudeMdRepo = await readText(path.join(ctx.repoRoot, "CLAUDE.md"));
		const contributingApp = await readText(path.join(ctx.app.path, "CONTRIBUTING.md"));
		const contributingRepo = await readText(path.join(ctx.repoRoot, "CONTRIBUTING.md"));

		const claudeMd = claudeMdApp || claudeMdRepo || "";
		const contributing = contributingApp || contributingRepo || "";

		const patterns = ["branch protection", "required review", "status check"];
		const documented =
			patterns.some((p) => claudeMd.toLowerCase().includes(p)) ||
			patterns.some((p) => contributing.toLowerCase().includes(p));

		return {
			pass: documented,
			details: documented ? "Documented" : "Not documented",
		};
	},

	"dependency-scanning": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		const scanners = [
			{ file: "renovate.json", tool: "Renovate" },
			{ file: ".renovaterc.json", tool: "Renovate" },
			{ file: ".github/dependabot.yml", tool: "Dependabot" },
			{ file: ".snyk", tool: "Snyk" },
		];

		for (const { file, tool } of scanners) {
			if ((await fileExists(path.join(appPath, file))) ||
				(await fileExists(path.join(repoRoot, file)))) {
				return { pass: true, tool, configPath: file };
			}
		}

		return { pass: false, details: "No dependency scanning" };
	},

	// =========================================================================
	// PRE-COMMIT HOOKS
	// =========================================================================

	"pre-commit-hooks": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		// Check for Husky
		if (dirExists(path.join(appPath, ".husky")) ||
			dirExists(path.join(repoRoot, ".husky"))) {
			return { pass: true, tool: "Husky", configPath: ".husky" };
		}

		// Check for Lefthook
		if ((await fileExists(path.join(appPath, "lefthook.yml"))) ||
			(await fileExists(path.join(repoRoot, "lefthook.yml")))) {
			return { pass: true, tool: "Lefthook", configPath: "lefthook.yml" };
		}

		// Check for pre-commit
		if ((await fileExists(path.join(appPath, ".pre-commit-config.yaml"))) ||
			(await fileExists(path.join(repoRoot, ".pre-commit-config.yaml")))) {
			return { pass: true, tool: "pre-commit", configPath: ".pre-commit-config.yaml" };
		}

		return { pass: false, details: "No pre-commit hooks configured" };
	},

	// =========================================================================
	// TASK DISCOVERY
	// =========================================================================

	"pr-template": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		const templates = [
			".github/pull_request_template.md",
			".github/PULL_REQUEST_TEMPLATE.md",
		];

		for (const template of templates) {
			if ((await fileExists(path.join(appPath, template))) ||
				(await fileExists(path.join(repoRoot, template)))) {
				return { pass: true, configPath: template };
			}
		}

		// Check for template directory
		if (dirExists(path.join(appPath, ".github/PULL_REQUEST_TEMPLATE")) ||
			dirExists(path.join(repoRoot, ".github/PULL_REQUEST_TEMPLATE"))) {
			return { pass: true, configPath: ".github/PULL_REQUEST_TEMPLATE/" };
		}

		return { pass: false, details: "Missing PR template" };
	},

	"issue-templates": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		if (dirExists(path.join(appPath, ".github/ISSUE_TEMPLATE")) ||
			dirExists(path.join(repoRoot, ".github/ISSUE_TEMPLATE"))) {
			return { pass: true, configPath: ".github/ISSUE_TEMPLATE/" };
		}

		if ((await fileExists(path.join(appPath, ".github/ISSUE_TEMPLATE.md"))) ||
			(await fileExists(path.join(repoRoot, ".github/ISSUE_TEMPLATE.md")))) {
			return { pass: true, configPath: ".github/ISSUE_TEMPLATE.md" };
		}

		return { pass: false, details: "Missing issue templates" };
	},

	"branch-naming": async (ctx: CheckContext): Promise<CheckResult> => {
		const claudeMdApp = await readText(path.join(ctx.app.path, "CLAUDE.md"));
		const claudeMdRepo = await readText(path.join(ctx.repoRoot, "CLAUDE.md"));
		const contributingApp = await readText(path.join(ctx.app.path, "CONTRIBUTING.md"));
		const contributingRepo = await readText(path.join(ctx.repoRoot, "CONTRIBUTING.md"));

		const claudeMd = claudeMdApp || claudeMdRepo || "";
		const contributing = contributingApp || contributingRepo || "";

		const documented = Boolean(
			(claudeMd.toLowerCase().includes("branch") && claudeMd.toLowerCase().includes("naming")) ||
			(contributing.toLowerCase().includes("branch") && contributing.toLowerCase().includes("naming"))
		);

		return {
			pass: documented,
			details: documented ? "Documented" : "Not documented",
		};
	},

	"commit-convention": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		// Check for commit tools
		const configs = [
			{ file: "commitlint.config.js", tool: "Commitlint" },
			{ file: ".commitlintrc.json", tool: "Commitlint" },
			{ file: ".czrc", tool: "Commitizen" },
			{ file: ".cz.json", tool: "Commitizen" },
		];

		for (const { file, tool } of configs) {
			if ((await fileExists(path.join(appPath, file))) ||
				(await fileExists(path.join(repoRoot, file)))) {
				return { pass: true, tool, configPath: file };
			}
		}

		// Check for documentation
		const contributingApp = await readText(path.join(appPath, "CONTRIBUTING.md"));
		const contributingRepo = await readText(path.join(repoRoot, "CONTRIBUTING.md"));
		const contributing = contributingApp || contributingRepo || "";

		if (
			contributing.toLowerCase().includes("conventional commit") ||
			contributing.toLowerCase().includes("commit message")
		) {
			return { pass: true, details: "Documented in CONTRIBUTING.md" };
		}

		return { pass: false, details: "No commit convention" };
	},

	// =========================================================================
	// CI/CD
	// =========================================================================

	"ci-configured": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		// GitHub Actions
		if (dirExists(path.join(appPath, ".github/workflows")) ||
			dirExists(path.join(repoRoot, ".github/workflows"))) {
			return { pass: true, tool: "GitHub Actions" };
		}

		// GitLab CI
		if ((await fileExists(path.join(appPath, ".gitlab-ci.yml"))) ||
			(await fileExists(path.join(repoRoot, ".gitlab-ci.yml")))) {
			return { pass: true, tool: "GitLab CI" };
		}

		// CircleCI
		if ((await fileExists(path.join(appPath, ".circleci/config.yml"))) ||
			(await fileExists(path.join(repoRoot, ".circleci/config.yml")))) {
			return { pass: true, tool: "CircleCI" };
		}

		// Travis CI
		if ((await fileExists(path.join(appPath, ".travis.yml"))) ||
			(await fileExists(path.join(repoRoot, ".travis.yml")))) {
			return { pass: true, tool: "Travis CI" };
		}

		return { pass: false, details: "No CI configured" };
	},

	// =========================================================================
	// OBSERVABILITY (using dependency parsing)
	// =========================================================================

	"structured-logging": async (ctx: CheckContext): Promise<CheckResult> => {
		const manifest = await parseDependencies(ctx.app.path, ctx.app.language);
		const match = hasLibraryCategory(manifest, "logging", ctx.app.language);

		if (match.found) {
			return {
				pass: true,
				tool: match.library,
				details: `Using ${match.library}`,
			};
		}

		return { pass: false, details: "No structured logging library detected" };
	},

	"error-tracking": async (ctx: CheckContext): Promise<CheckResult> => {
		const manifest = await parseDependencies(ctx.app.path, ctx.app.language);
		const match = hasLibraryCategory(manifest, "errorTracking", ctx.app.language);

		if (match.found) {
			return {
				pass: true,
				tool: match.library,
				details: `Using ${match.library}`,
			};
		}

		return { pass: false, details: "No error tracking configured" };
	},

	"tracing": async (ctx: CheckContext): Promise<CheckResult> => {
		const manifest = await parseDependencies(ctx.app.path, ctx.app.language);
		const match = hasLibraryCategory(manifest, "tracing", ctx.app.language);

		if (match.found) {
			return {
				pass: true,
				tool: match.library,
				details: `Using ${match.library}`,
			};
		}

		return { pass: false, details: "No distributed tracing configured" };
	},

	"metrics": async (ctx: CheckContext): Promise<CheckResult> => {
		const manifest = await parseDependencies(ctx.app.path, ctx.app.language);
		const match = hasLibraryCategory(manifest, "metrics", ctx.app.language);

		if (match.found) {
			return {
				pass: true,
				tool: match.library,
				details: `Using ${match.library}`,
			};
		}

		return { pass: false, details: "No metrics collection configured" };
	},

	// =========================================================================
	// PRODUCT & EXPERIMENTATION (using dependency parsing)
	// =========================================================================

	"feature-flags": async (ctx: CheckContext): Promise<CheckResult> => {
		const manifest = await parseDependencies(ctx.app.path, ctx.app.language);
		const match = hasLibraryCategory(manifest, "featureFlags", ctx.app.language);

		if (match.found) {
			return {
				pass: true,
				tool: match.library,
				details: `Using ${match.library}`,
			};
		}

		return { pass: false, details: "No feature flag library detected" };
	},

	"analytics": async (ctx: CheckContext): Promise<CheckResult> => {
		const manifest = await parseDependencies(ctx.app.path, ctx.app.language);
		const match = hasLibraryCategory(manifest, "analytics", ctx.app.language);

		if (match.found) {
			return {
				pass: true,
				tool: match.library,
				details: `Using ${match.library}`,
			};
		}

		return { pass: false, details: "No analytics library detected" };
	},

	// =========================================================================
	// TESTING (using dependency parsing)
	// =========================================================================

	"test-framework": async (ctx: CheckContext): Promise<CheckResult> => {
		const manifest = await parseDependencies(ctx.app.path, ctx.app.language);
		const match = hasLibraryCategory(manifest, "testing", ctx.app.language);

		if (match.found) {
			return {
				pass: true,
				tool: match.library,
				details: `Using ${match.library}`,
			};
		}

		// For Python: Check pyproject.toml for pytest configuration
		// (pytest may be a dev dependency not in main deps)
		if (ctx.app.language === "python") {
			for (const basePath of [ctx.app.path, ctx.repoRoot]) {
				const pyproject = await readText(path.join(basePath, "pyproject.toml"));
				if (pyproject) {
					if (pyproject.includes("[tool.pytest") || pyproject.includes("[tool.pytest.ini_options]")) {
						return { pass: true, tool: "pytest", details: "pytest configured in pyproject.toml" };
					}
				}
				// Check pytest.ini
				if (await fileExists(path.join(basePath, "pytest.ini"))) {
					return { pass: true, tool: "pytest", details: "pytest.ini exists" };
				}
				// Check setup.cfg for pytest
				const setupCfg = await readText(path.join(basePath, "setup.cfg"));
				if (setupCfg?.includes("[tool:pytest]")) {
					return { pass: true, tool: "pytest", details: "pytest in setup.cfg" };
				}
			}
		}

		// For Go: testing package is built-in
		if (ctx.app.language === "go") {
			// Check for _test.go files
			try {
				const testFiles = await $`find ${ctx.app.path} -name "*_test.go" -type f 2>/dev/null | head -1`.quiet();
				if (testFiles.text().trim()) {
					return { pass: true, tool: "testing", details: "Go testing package (built-in)" };
				}
			} catch {
				// Ignore errors
			}
		}

		// For Rust: test module is built-in
		if (ctx.app.language === "rust") {
			// Check for #[test] or #[cfg(test)] in source files
			try {
				const testAttrs = await $`grep -r "#\\[test\\]\\|#\\[cfg(test)\\]" --include="*.rs" ${ctx.app.path} 2>/dev/null | head -1`.quiet();
				if (testAttrs.text().trim()) {
					return { pass: true, tool: "test", details: "Rust test module (built-in)" };
				}
			} catch {
				// Ignore errors
			}
		}

		// For Java: Check for JUnit annotations
		if (ctx.app.language === "java") {
			try {
				const junitTests = await $`grep -r "@Test\\|@org.junit" --include="*.java" ${ctx.app.path} 2>/dev/null | head -1`.quiet();
				if (junitTests.text().trim()) {
					return { pass: true, tool: "JUnit", details: "JUnit tests found" };
				}
			} catch {
				// Ignore errors
			}
		}

		return { pass: false, details: "No test framework detected" };
	},

	"input-validation": async (ctx: CheckContext): Promise<CheckResult> => {
		const manifest = await parseDependencies(ctx.app.path, ctx.app.language);
		const match = hasLibraryCategory(manifest, "validation", ctx.app.language);

		if (match.found) {
			return {
				pass: true,
				tool: match.library,
				details: `Using ${match.library}`,
			};
		}

		return { pass: false, details: "No validation library detected" };
	},

	// =========================================================================
	// DOCUMENTATION (additional)
	// =========================================================================

	"changelog-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		// Standard changelog files
		const changelogFiles = [
			"CHANGELOG.md",
			"HISTORY.md",
			"CHANGES.md",
			"changelog.md",
			"NEWS",
			"NEWS.md",
			"RELEASE_NOTES.md",
			"ReleaseNotes.md",
			"RELEASES.md",
		];

		for (const basePath of [appPath, repoRoot]) {
			for (const file of changelogFiles) {
				if (await fileExists(path.join(basePath, file))) {
					return { pass: true, configPath: file };
				}
			}
		}

		// Check for docs/releases/ or docs/changelog/ directory
		const releasesDirs = [
			"docs/releases",
			"docs/changelog",
			"docs/release-notes",
		];

		for (const basePath of [appPath, repoRoot]) {
			for (const dir of releasesDirs) {
				if (dirExists(path.join(basePath, dir))) {
					return { pass: true, configPath: dir };
				}
			}
		}

		// Check for GitHub releases (via .github or release workflow)
		const workflowsDir = path.join(repoRoot, ".github/workflows");
		if (dirExists(workflowsDir)) {
			try {
				const files = (await import("node:fs")).readdirSync(workflowsDir);
				for (const file of files) {
					if (file.toLowerCase().includes("release")) {
						const content = await readText(path.join(workflowsDir, file));
						if (content?.includes("release") || content?.includes("changelog")) {
							return { pass: true, details: "Release workflow configured" };
						}
					}
				}
			} catch {
				// Ignore
			}
		}

		return { pass: false, details: "Missing" };
	},

	"architecture-docs": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		const archFiles = [
			"ARCHITECTURE.md",
			"docs/architecture.md",
			"docs/ARCHITECTURE.md",
			"docs/design.md",
			"docs/DESIGN.md",
			"doc/architecture.md",
		];

		for (const file of archFiles) {
			if ((await fileExists(path.join(appPath, file))) ||
				(await fileExists(path.join(repoRoot, file)))) {
				return { pass: true, configPath: file };
			}
		}

		// Check if README has architecture section
		const readme = await readText(path.join(appPath, "README.md")) ||
			await readText(path.join(repoRoot, "README.md")) || "";

		if (readme.toLowerCase().includes("## architecture") ||
			readme.toLowerCase().includes("## design")) {
			return { pass: true, details: "Documented in README" };
		}

		return { pass: false, details: "No architecture documentation" };
	},

	"api-documentation": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		const apiDocs = [
			"openapi.yaml",
			"openapi.json",
			"swagger.yaml",
			"swagger.json",
			"docs/api.md",
			"docs/API.md",
			"api/openapi.yaml",
		];

		for (const file of apiDocs) {
			if ((await fileExists(path.join(appPath, file))) ||
				(await fileExists(path.join(repoRoot, file)))) {
				return { pass: true, configPath: file };
			}
		}

		// Check for docs directory with API content
		if (dirExists(path.join(appPath, "docs/api")) ||
			dirExists(path.join(repoRoot, "docs/api"))) {
			return { pass: true, configPath: "docs/api/" };
		}

		// Check for documentation site generators (mkdocs, sphinx, docusaurus)
		const docGenerators = [
			{ file: "mkdocs.yml", name: "MkDocs" },
			{ file: "mkdocs.yaml", name: "MkDocs" },
			{ file: "docs/mkdocs.yml", name: "MkDocs" },
			{ file: "docs/conf.py", name: "Sphinx" },
			{ file: "conf.py", name: "Sphinx" },
			{ file: "docusaurus.config.js", name: "Docusaurus" },
		];

		for (const { file, name } of docGenerators) {
			if ((await fileExists(path.join(appPath, file))) ||
				(await fileExists(path.join(repoRoot, file)))) {
				return { pass: true, tool: name, details: `${name} docs configured` };
			}
		}

		// Check for extensive docs/ directory (multi-language docs like FastAPI)
		for (const basePath of [appPath, repoRoot]) {
			const docsPath = path.join(basePath, "docs");
			if (dirExists(docsPath)) {
				try {
					const entries = fs.readdirSync(docsPath);
					// If docs has subdirectories (language dirs or topic dirs), it's comprehensive docs
					const subdirs = entries.filter(e => {
						try {
							return fs.statSync(path.join(docsPath, e)).isDirectory();
						} catch {
							return false;
						}
					});
					if (subdirs.length >= 3) {
						return { pass: true, details: `Extensive docs/ (${subdirs.length} sections)` };
					}
					// Check for mkdocs.yml in subdirectories (multi-language setup)
					for (const subdir of subdirs) {
						if (await fileExists(path.join(docsPath, subdir, "mkdocs.yml"))) {
							return { pass: true, tool: "MkDocs", details: "Multi-language MkDocs docs" };
						}
					}
				} catch {
					// Ignore errors
				}
			}
		}

		// For Python: Check if FastAPI/Starlette (auto-generates OpenAPI)
		if (ctx.app.language === "python") {
			const pyproject = await readText(path.join(appPath, "pyproject.toml")) ||
				await readText(path.join(repoRoot, "pyproject.toml")) || "";
			if (pyproject.includes("fastapi") || pyproject.includes("starlette")) {
				return { pass: true, details: "FastAPI/Starlette auto-generates OpenAPI" };
			}
		}

		return { pass: false, details: "No API documentation" };
	},

	"examples-exist": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		const exampleDirs = ["examples", "example", "samples", "demos"];

		for (const dir of exampleDirs) {
			if (dirExists(path.join(appPath, dir)) ||
				dirExists(path.join(repoRoot, dir))) {
				return { pass: true, configPath: dir };
			}
		}

		// Check README for examples section
		const readme = await readText(path.join(appPath, "README.md")) ||
			await readText(path.join(repoRoot, "README.md")) || "";

		if (readme.toLowerCase().includes("## example") ||
			readme.toLowerCase().includes("## usage")) {
			return { pass: true, details: "Examples in README" };
		}

		return { pass: false, details: "No examples found" };
	},

	"claude-md-has-commands": async (ctx: CheckContext): Promise<CheckResult> => {
		// Check CLAUDE.md first
		let content = await readText(path.join(ctx.app.path, "CLAUDE.md"));
		if (!content) {
			content = await readText(path.join(ctx.repoRoot, "CLAUDE.md"));
		}

		// Fallback to README + CONTRIBUTING for OSS
		if (!content) {
			const readme = await readText(path.join(ctx.app.path, "README.md")) ||
				await readText(path.join(ctx.repoRoot, "README.md")) || "";
			const contributing = await readText(path.join(ctx.app.path, "CONTRIBUTING.md")) ||
				await readText(path.join(ctx.repoRoot, "CONTRIBUTING.md")) || "";
			content = readme + "\n" + contributing;
		}

		if (!content || content.trim() === "") {
			return { pass: false, details: "No docs found" };
		}

		const hasBuildCommand =
			content.includes("build") ||
			content.includes("make") ||
			content.includes("cargo") ||
			content.includes("go build") ||
			content.includes("bazel") ||
			content.includes("gradle") ||
			content.includes("mvn");

		const hasTestCommand =
			content.includes("test") ||
			content.includes("pytest") ||
			content.includes("vitest") ||
			content.includes("jest") ||
			content.includes("go test") ||
			content.includes("cargo test");

		const hasRunCommand =
			content.includes("run") ||
			content.includes("start") ||
			content.includes("dev") ||
			content.includes("./dev");

		if (hasBuildCommand && hasTestCommand) {
			return { pass: true, details: "Has build and test commands" };
		}

		if (hasRunCommand || hasBuildCommand) {
			return { pass: true, details: "Has development commands" };
		}

		return { pass: false, details: "Missing build/test commands" };
	},

	// =========================================================================
	// TASK DISCOVERY (additional)
	// =========================================================================

	"task-definitions": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		// Check for package.json scripts
		const pkgPath = path.join(appPath, "package.json");
		if (await fileExists(pkgPath)) {
			try {
				const pkg = await Bun.file(pkgPath).json();
				if (pkg.scripts && Object.keys(pkg.scripts).length > 0) {
					return { pass: true, details: `${Object.keys(pkg.scripts).length} npm scripts` };
				}
			} catch { /* ignore parse errors */ }
		}

		// Check for Makefile variants
		const makefiles = ["Makefile", "makefile", "GNUmakefile"];
		for (const mf of makefiles) {
			if ((await fileExists(path.join(appPath, mf))) ||
				(await fileExists(path.join(repoRoot, mf)))) {
				return { pass: true, tool: "Make", configPath: mf };
			}
		}

		// Check for Bazel (used by CockroachDB, Google projects, etc.)
		if ((await fileExists(path.join(appPath, "BUILD.bazel"))) ||
			(await fileExists(path.join(repoRoot, "BUILD.bazel"))) ||
			(await fileExists(path.join(appPath, "WORKSPACE"))) ||
			(await fileExists(path.join(repoRoot, "WORKSPACE"))) ||
			(await fileExists(path.join(appPath, "WORKSPACE.bazel"))) ||
			(await fileExists(path.join(repoRoot, "WORKSPACE.bazel")))) {
			return { pass: true, tool: "Bazel", details: "Bazel build system" };
		}

		// Check for Justfile
		if ((await fileExists(path.join(appPath, "Justfile"))) ||
			(await fileExists(path.join(repoRoot, "Justfile")))) {
			return { pass: true, tool: "Just", configPath: "Justfile" };
		}

		// Check for Taskfile
		if ((await fileExists(path.join(appPath, "Taskfile.yml"))) ||
			(await fileExists(path.join(repoRoot, "Taskfile.yml")))) {
			return { pass: true, tool: "Task", configPath: "Taskfile.yml" };
		}

		// Check for pyproject.toml (Python)
		if ((await fileExists(path.join(appPath, "pyproject.toml"))) ||
			(await fileExists(path.join(repoRoot, "pyproject.toml")))) {
			return { pass: true, tool: "Python", configPath: "pyproject.toml" };
		}

		// Check for Cargo.toml (Rust)
		if ((await fileExists(path.join(appPath, "Cargo.toml"))) ||
			(await fileExists(path.join(repoRoot, "Cargo.toml")))) {
			return { pass: true, tool: "Cargo", configPath: "Cargo.toml" };
		}

		// Check for go.mod (Go)
		if ((await fileExists(path.join(appPath, "go.mod"))) ||
			(await fileExists(path.join(repoRoot, "go.mod")))) {
			return { pass: true, tool: "Go", configPath: "go.mod" };
		}

		return { pass: false, details: "No task definitions found" };
	},

	"makefile": createPathCheck(
		["Makefile", "makefile", "GNUmakefile"],
		{ checkBothPaths: true }
	),

	"release-process": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		// Check for release configuration files
		const releaseConfigs = [
			".releaserc.json",
			".releaserc.yaml",
			".releaserc.yml",
			"release.config.js",
			".goreleaser.yaml",
			".goreleaser.yml",
			"pyproject.toml", // Often has version info
		];

		for (const file of releaseConfigs) {
			if ((await fileExists(path.join(appPath, file))) ||
				(await fileExists(path.join(repoRoot, file)))) {
				return { pass: true, configPath: file };
			}
		}

		// Check for GitHub release workflow
		const workflowDir = path.join(repoRoot, ".github/workflows");
		if (dirExists(workflowDir)) {
			try {
				const files = await Bun.file(workflowDir);
				// Simple check: look for release in workflow names
				const result = await $`ls ${workflowDir} 2>/dev/null`.quiet();
				const workflowFiles = result.text().split("\n").filter(Boolean);
				for (const wf of workflowFiles) {
					if (wf.toLowerCase().includes("release")) {
						return { pass: true, configPath: `.github/workflows/${wf}` };
					}
				}
			} catch { /* ignore */ }
		}

		// Check documentation
		const contributing = await readText(path.join(repoRoot, "CONTRIBUTING.md")) || "";
		if (contributing.toLowerCase().includes("release")) {
			return { pass: true, details: "Documented in CONTRIBUTING.md" };
		}

		return { pass: false, details: "No release process documented" };
	},

	// =========================================================================
	// BUILD (additional)
	// =========================================================================

	"ci-pipeline": async (ctx: CheckContext): Promise<CheckResult> => {
		// Alias for ci-configured
		const ciCheck = sharedChecks["ci-configured"];
		if (ciCheck) {
			return ciCheck(ctx);
		}
		return { pass: false, details: "CI check not available" };
	},

	// =========================================================================
	// DEVELOPMENT ENVIRONMENT (additional)
	// =========================================================================

	"env-setup-script": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		const setupScripts = [
			"setup.sh",
			"scripts/setup.sh",
			"bin/setup",
			"scripts/bootstrap.sh",
			"bootstrap.sh",
			"init.sh",
			"scripts/init.sh",
		];

		for (const script of setupScripts) {
			if ((await fileExists(path.join(appPath, script))) ||
				(await fileExists(path.join(repoRoot, script)))) {
				return { pass: true, configPath: script };
			}
		}

		// Check for npm/package.json setup script
		const pkgPath = path.join(appPath, "package.json");
		if (await fileExists(pkgPath)) {
			try {
				const pkg = await Bun.file(pkgPath).json();
				if (pkg.scripts?.setup || pkg.scripts?.bootstrap || pkg.scripts?.init) {
					return { pass: true, details: "npm script" };
				}
			} catch { /* ignore */ }
		}

		return { pass: false, details: "No setup script found" };
	},

	"debug-configs": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		// VS Code debug configuration
		if ((await fileExists(path.join(appPath, ".vscode/launch.json"))) ||
			(await fileExists(path.join(repoRoot, ".vscode/launch.json")))) {
			return { pass: true, configPath: ".vscode/launch.json" };
		}

		// JetBrains run configurations
		if (dirExists(path.join(appPath, ".idea/runConfigurations")) ||
			dirExists(path.join(repoRoot, ".idea/runConfigurations"))) {
			return { pass: true, configPath: ".idea/runConfigurations/" };
		}

		return { pass: false, details: "No debug configurations" };
	},

	"local-env-docs": async (ctx: CheckContext): Promise<CheckResult> => {
		const readme = await readText(path.join(ctx.app.path, "README.md")) ||
			await readText(path.join(ctx.repoRoot, "README.md")) || "";

		const claudeMd = await readText(path.join(ctx.app.path, "CLAUDE.md")) ||
			await readText(path.join(ctx.repoRoot, "CLAUDE.md")) || "";

		const contributing = await readText(path.join(ctx.app.path, "CONTRIBUTING.md")) ||
			await readText(path.join(ctx.repoRoot, "CONTRIBUTING.md")) || "";

		const allDocs = readme + claudeMd + contributing;
		const lowerDocs = allDocs.toLowerCase();

		// Check for development setup documentation
		const hasSetupDocs =
			lowerDocs.includes("## development") ||
			lowerDocs.includes("## getting started") ||
			lowerDocs.includes("## setup") ||
			lowerDocs.includes("## installation") ||
			lowerDocs.includes("## local development");

		if (hasSetupDocs) {
			return { pass: true, details: "Development setup documented" };
		}

		return { pass: false, details: "No local environment documentation" };
	},

	// =========================================================================
	// SECURITY (additional)
	// =========================================================================

	"secrets-management": async (ctx: CheckContext): Promise<CheckResult> => {
		// This is essentially the same as no-secrets-in-repo but with a broader check
		const hasEnvFile = await fileExists(path.join(ctx.app.path, ".env"));
		const hasCredentials = await fileExists(path.join(ctx.app.path, "credentials.json"));
		const hasSecrets = await fileExists(path.join(ctx.app.path, "secrets.json"));
		const hasPrivateKey = await fileExists(path.join(ctx.app.path, "private.key"));

		// Check for .env.example as positive indicator
		const hasEnvExample = await fileExists(path.join(ctx.app.path, ".env.example")) ||
			await fileExists(path.join(ctx.repoRoot, ".env.example"));

		const suspicious = hasEnvFile || hasCredentials || hasSecrets || hasPrivateKey;

		if (suspicious && !hasEnvExample) {
			return {
				pass: false,
				details: "Potential secrets in repo, no .env.example",
			};
		}

		if (hasEnvExample) {
			return { pass: true, details: ".env.example documents secrets" };
		}

		return { pass: true, details: "No secrets found" };
	},

	"security-scanning": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		// Check for security scanning tools
		const scanners = [
			{ file: ".snyk", tool: "Snyk" },
			{ file: "snyk.json", tool: "Snyk" },
			{ file: ".trivy.yaml", tool: "Trivy" },
			{ file: ".gitleaks.toml", tool: "Gitleaks" },
			{ file: "sonar-project.properties", tool: "SonarQube" },
		];

		for (const { file, tool } of scanners) {
			if ((await fileExists(path.join(appPath, file))) ||
				(await fileExists(path.join(repoRoot, file)))) {
				return { pass: true, tool, configPath: file };
			}
		}

		// Check GitHub workflows for security scanning
		const workflowDir = path.join(repoRoot, ".github/workflows");
		if (dirExists(workflowDir)) {
			try {
				const result = await $`ls ${workflowDir} 2>/dev/null`.quiet();
				const files = result.text().split("\n").filter(Boolean);
				for (const f of files) {
					if (f.toLowerCase().includes("security") ||
						f.toLowerCase().includes("scan") ||
						f.toLowerCase().includes("codeql")) {
						return { pass: true, tool: "GitHub Actions", configPath: `.github/workflows/${f}` };
					}
				}
			} catch { /* ignore */ }
		}

		return { pass: false, details: "No security scanning configured" };
	},

	"vulnerability-policy": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		// Check for SECURITY.md
		if ((await fileExists(path.join(appPath, "SECURITY.md"))) ||
			(await fileExists(path.join(repoRoot, "SECURITY.md")))) {
			return { pass: true, configPath: "SECURITY.md" };
		}

		// Check for .github/SECURITY.md
		if (await fileExists(path.join(repoRoot, ".github/SECURITY.md"))) {
			return { pass: true, configPath: ".github/SECURITY.md" };
		}

		// Check README for security section
		const readme = await readText(path.join(repoRoot, "README.md")) || "";
		if (readme.toLowerCase().includes("## security")) {
			return { pass: true, details: "Security section in README" };
		}

		return { pass: false, details: "No security/vulnerability policy" };
	},

	// =========================================================================
	// ALIASES (for naming consistency with index.ts)
	// =========================================================================

	// editor-config → editorconfig-exists
	"editor-config": createPathCheck(
		[".editorconfig"],
		{ checkBothPaths: true }
	),

	// devcontainer → devcontainer-exists
	"devcontainer": createPathCheck(
		[".devcontainer/devcontainer.json", ".devcontainer.json"],
		{ checkBothPaths: true, successDetails: "Found", failureDetails: "Not configured" }
	),

	// =========================================================================
	// ADDITIONAL SHARED IMPLEMENTATIONS
	// =========================================================================

	"e2e-tests": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		// Check for common E2E test directories
		const e2eDirs = [
			"e2e",
			"tests/e2e",
			"test/e2e",
			"cypress",
			"playwright",
			"spec/e2e",
		];

		for (const dir of e2eDirs) {
			if (dirExists(path.join(appPath, dir)) ||
				dirExists(path.join(repoRoot, dir))) {
				return { pass: true, configPath: dir };
			}
		}

		// Check for Playwright or Cypress config files
		const e2eConfigs = [
			"playwright.config.ts",
			"playwright.config.js",
			"cypress.config.ts",
			"cypress.config.js",
			"cypress.json",
			"wdio.conf.ts",
			"wdio.conf.js",
		];

		for (const config of e2eConfigs) {
			if ((await fileExists(path.join(appPath, config))) ||
				(await fileExists(path.join(repoRoot, config)))) {
				return { pass: true, configPath: config };
			}
		}

		return { pass: false, details: "No E2E tests found" };
	},

	"health-endpoints": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		// Check for health check implementations in common locations
		const healthPatterns = [
			"health.ts",
			"health.js",
			"healthcheck.ts",
			"healthcheck.js",
			"routes/health.ts",
			"api/health.ts",
			"src/health.ts",
		];

		for (const pattern of healthPatterns) {
			if ((await fileExists(path.join(appPath, pattern))) ||
				(await fileExists(path.join(repoRoot, pattern)))) {
				return { pass: true, configPath: pattern };
			}
		}

		// Check CLAUDE.md or README for health endpoint documentation
		const docs = await readText(path.join(appPath, "CLAUDE.md")) ||
			await readText(path.join(repoRoot, "CLAUDE.md")) ||
			await readText(path.join(appPath, "README.md")) ||
			await readText(path.join(repoRoot, "README.md")) || "";

		if (docs.toLowerCase().includes("/health") ||
			docs.toLowerCase().includes("healthcheck") ||
			docs.toLowerCase().includes("/readiness") ||
			docs.toLowerCase().includes("/liveness")) {
			return { pass: true, details: "Documented" };
		}

		return { pass: false, details: "No health endpoints found" };
	},

	"inline-docs": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		// Check for API documentation directories
		const docDirs = [
			"docs",
			"doc",
			"documentation",
			"api-docs",
		];

		for (const dir of docDirs) {
			if (dirExists(path.join(appPath, dir)) ||
				dirExists(path.join(repoRoot, dir))) {
				return { pass: true, configPath: dir };
			}
		}

		// Check for generated docs config
		const docConfigs = [
			"typedoc.json",
			".typedoc.json",
			"jsdoc.json",
			".jsdoc.json",
			"mkdocs.yml",
			"docusaurus.config.js",
		];

		for (const config of docConfigs) {
			if ((await fileExists(path.join(appPath, config))) ||
				(await fileExists(path.join(repoRoot, config)))) {
				return { pass: true, configPath: config };
			}
		}

		return { pass: false, details: "No inline documentation" };
	},

	"log-levels": async (ctx: CheckContext): Promise<CheckResult> => {
		// Check for logging configuration that implies level support
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		const logConfigs = [
			"log4j.properties",
			"log4j2.xml",
			"logback.xml",
			"logging.yaml",
			"logging.json",
			".env.example", // Often contains LOG_LEVEL
		];

		for (const config of logConfigs) {
			if ((await fileExists(path.join(appPath, config))) ||
				(await fileExists(path.join(repoRoot, config)))) {
				return { pass: true, configPath: config };
			}
		}

		// Check .env.example for LOG_LEVEL
		const envExample = await readText(path.join(appPath, ".env.example")) ||
			await readText(path.join(repoRoot, ".env.example")) || "";

		if (envExample.includes("LOG_LEVEL") || envExample.includes("LOGLEVEL")) {
			return { pass: true, details: "LOG_LEVEL in .env.example" };
		}

		// Check if structured logging is configured (implies level support)
		const manifest = await parseDependencies(ctx.app.path, ctx.app.language);
		const hasLogging = hasLibraryCategory(manifest, "logging", ctx.app.language);

		if (hasLogging.found) {
			return { pass: true, details: `${hasLogging.library} supports levels` };
		}

		return { pass: false, details: "No log level configuration" };
	},

	"monitoring-dashboards": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		// Check for dashboard configs
		const dashboardConfigs = [
			"grafana/",
			"dashboards/",
			".datadog/",
			"newrelic.yml",
			"honeycomb.yaml",
		];

		for (const config of dashboardConfigs) {
			if (config.endsWith("/")) {
				if (dirExists(path.join(appPath, config.slice(0, -1))) ||
					dirExists(path.join(repoRoot, config.slice(0, -1)))) {
					return { pass: true, configPath: config };
				}
			} else {
				if ((await fileExists(path.join(appPath, config))) ||
					(await fileExists(path.join(repoRoot, config)))) {
					return { pass: true, configPath: config };
				}
			}
		}

		return { pass: false, details: "No monitoring dashboards configured" };
	},

	"error-budgets": async (ctx: CheckContext): Promise<CheckResult> => {
		// Check for SLO/error budget documentation
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		const sloFiles = [
			"slo.yaml",
			"slo.yml",
			"sli.yaml",
			"docs/slo.md",
			"docs/SLO.md",
		];

		for (const file of sloFiles) {
			if ((await fileExists(path.join(appPath, file))) ||
				(await fileExists(path.join(repoRoot, file)))) {
				return { pass: true, configPath: file };
			}
		}

		// Check README for SLO documentation
		const readme = await readText(path.join(repoRoot, "README.md")) || "";
		if (readme.toLowerCase().includes("error budget") ||
			readme.toLowerCase().includes("slo") ||
			readme.toLowerCase().includes("sli")) {
			return { pass: true, details: "Documented in README" };
		}

		return { pass: false, details: "No error budgets defined" };
	},

	"task-documentation": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const repoRoot = ctx.repoRoot;

		// Check CLAUDE.md for task documentation
		const claudeMd = await readText(path.join(appPath, "CLAUDE.md")) ||
			await readText(path.join(repoRoot, "CLAUDE.md")) || "";

		if (claudeMd.toLowerCase().includes("## development") ||
			claudeMd.toLowerCase().includes("## commands") ||
			claudeMd.toLowerCase().includes("## task") ||
			claudeMd.toLowerCase().includes("## script")) {
			return { pass: true, details: "Documented in CLAUDE.md" };
		}

		// Check README
		const readme = await readText(path.join(repoRoot, "README.md")) || "";
		if (readme.toLowerCase().includes("## development") ||
			readme.toLowerCase().includes("## commands") ||
			readme.toLowerCase().includes("## npm scripts") ||
			readme.toLowerCase().includes("## make targets")) {
			return { pass: true, details: "Documented in README" };
		}

		// Check for Makefile with help target
		const makefile = await readText(path.join(repoRoot, "Makefile")) || "";
		if (makefile.includes("help:") || makefile.includes(".PHONY: help")) {
			return { pass: true, details: "Makefile has help target" };
		}

		return { pass: false, details: "No task documentation" };
	},
};

// ============================================================================
// Exports
// ============================================================================

/**
 * Get a shared check runner by ID
 */
export function getSharedCheck(checkId: string): CheckRunner | undefined {
	return sharedChecks[checkId];
}

/**
 * List all shared check IDs
 */
export function listSharedChecks(): string[] {
	return Object.keys(sharedChecks);
}
