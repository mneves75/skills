/**
 * @fileoverview Standard check definitions for Agent Readiness
 * @module kb-tools/lib/checks
 *
 * @description
 * Registers all standard check definitions with the check registry.
 * These are language-agnostic definitions - the actual implementation
 * comes from language-specific adapters.
 *
 * Also re-exports shared check implementations for use by adapters.
 */

import { type Level, type Pillar, checkRegistry, defineCheck } from "../check-registry.js";

// Re-export shared checks for adapter use
export {
	sharedChecks,
	getSharedCheck,
	listSharedChecks,
	createPathCheck,
	createDirCheck,
} from "./shared.js";

// ============================================================================
// Check Definitions
// ============================================================================

/**
 * Register all standard checks
 */
export function registerStandardChecks(): void {
	// Clear any existing checks (for re-registration)
	// Note: Registry doesn't have clear for checks, only for all

	const checks = [
		// =========================================================================
		// PILLAR 1: STYLE & VALIDATION
		// =========================================================================
		defineCheck("linter-exists", "style", 1, "Linter configured", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("type-checker-strict", "style", 1, "Type checker configured", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("formatter-exists", "style", 2, "Formatter configured", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("pre-commit-hooks", "style", 3, "Pre-commit hooks installed", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("no-lint-ignores", "style", 2, "No linter ignore comments", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("no-unsafe-types", "style", 2, "No unsafe type casts", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("strict-mode", "style", 3, "Strict mode enabled", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("zero-lint-errors", "style", 4, "Zero lint errors", async () => ({
			pass: false,
			details: "Override required",
		})),

		// =========================================================================
		// PILLAR 2: BUILD SYSTEM
		// =========================================================================
		defineCheck("dependency-manifest", "build", 1, "Dependency manifest exists", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("lockfile-exists", "build", 1, "Lock file committed", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("package-json-exists", "build", 1, "Package manifest exists", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("build-defined", "build", 1, "Build command documented", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("ci-pipeline", "build", 2, "CI pipeline configured", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("reproducible-builds", "build", 4, "Build is deterministic", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("no-deprecated-deps", "build", 3, "No deprecated dependencies", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("build-succeeds", "build", 3, "Build succeeds", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("deps-installed", "build", 2, "Dependencies installed", async () => ({
			pass: false,
			details: "Override required",
		})),

		// =========================================================================
		// PILLAR 3: TESTING
		// =========================================================================
		defineCheck("test-framework", "testing", 1, "Test framework configured", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("test-coverage", "testing", 5, "Coverage threshold defined", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("tests-pass", "testing", 2, "Tests pass", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("integration-tests", "testing", 3, "Integration tests exist", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("e2e-tests", "testing", 4, "E2E tests exist", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("test-isolation", "testing", 3, "Tests are isolated", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("tests-fast", "testing", 4, "Tests complete in <5 minutes", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("tests-exist", "testing", 1, "At least one test exists", async () => ({
			pass: false,
			details: "Override required",
		})),

		// =========================================================================
		// PILLAR 4: DOCUMENTATION
		// =========================================================================
		defineCheck("readme-exists", "documentation", 1, "README exists", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("architecture-docs", "documentation", 3, "Architecture documented", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("api-documentation", "documentation", 3, "API documentation exists", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("changelog-exists", "documentation", 2, "CHANGELOG exists", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("inline-docs", "documentation", 2, "Inline documentation", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("examples-exist", "documentation", 3, "Examples exist", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("claude-md-exists", "documentation", 2, "CLAUDE.md or AGENTS.md exists", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("claude-md-has-commands", "documentation", 3, "CLAUDE.md includes build/test commands", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("claude-md-concise", "documentation", 4, "CLAUDE.md is concise (<300 lines)", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("claude-md-recent", "documentation", 5, "CLAUDE.md updated within 30 days", async () => ({
			pass: false,
			details: "Override required",
		})),

		// =========================================================================
		// PILLAR 5: DEVELOPMENT ENVIRONMENT
		// =========================================================================
		defineCheck("env-setup-script", "devenv", 2, "Setup script exists", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("devcontainer", "devenv", 3, "Devcontainer configured", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("editor-config", "devenv", 2, ".editorconfig exists", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("debug-configs", "devenv", 3, "Debug configurations", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("local-env-docs", "devenv", 3, "Local environment documented", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("watch-mode", "devenv", 2, "Watch mode available", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("gitignore-exists", "devenv", 1, ".gitignore exists", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("env-example", "devenv", 3, "Environment template exists", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("docker-compose", "devenv", 4, "Docker Compose for local services", async () => ({
			pass: false,
			details: "Override required",
		})),

		// =========================================================================
		// PILLAR 6: DEBUGGING & OBSERVABILITY
		// =========================================================================
		defineCheck("structured-logging", "observability", 2, "Structured logging configured", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("error-tracking", "observability", 3, "Error tracking configured", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("tracing", "observability", 4, "Distributed tracing configured", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("metrics", "observability", 5, "Metrics collection configured", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("health-endpoints", "observability", 3, "Health check endpoints", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("log-levels", "observability", 2, "Log levels configured", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("console-logs-minimal", "observability", 1, "Minimal console.log usage", async () => ({
			pass: false,
			details: "Override required",
		})),

		// =========================================================================
		// PILLAR 7: SECURITY
		// =========================================================================
		defineCheck("security-scanning", "security", 3, "Security scanning configured", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("secrets-management", "security", 2, "No secrets in repository", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("auth-implementation", "security", 3, "Authentication implemented", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("input-validation", "security", 2, "Input validation", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("audit-logging", "security", 4, "Audit logging configured", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("vulnerability-policy", "security", 5, "Vulnerability policy defined", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("git-initialized", "security", 1, "Git repository initialized", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("codeowners-exists", "security", 3, "CODEOWNERS file exists", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("branch-protection-documented", "security", 4, "Branch protection documented", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("dependency-scanning", "security", 5, "Dependency scanning configured", async () => ({
			pass: false,
			details: "Override required",
		})),

		// =========================================================================
		// PILLAR 8: TASK DISCOVERY
		// =========================================================================
		defineCheck("task-definitions", "taskdiscovery", 1, "Task definitions exist", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("npm-scripts", "taskdiscovery", 1, "NPM scripts defined", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("makefile", "taskdiscovery", 2, "Makefile exists", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("common-aliases", "taskdiscovery", 3, "Common task aliases", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("task-documentation", "taskdiscovery", 2, "Tasks documented", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("ci-tasks-aligned", "taskdiscovery", 4, "CI tasks aligned with local", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("pr-template", "taskdiscovery", 1, "PR template exists", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("issue-templates", "taskdiscovery", 2, "Issue templates exist", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("contributing-guide", "taskdiscovery", 2, "CONTRIBUTING.md exists", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("branch-naming", "taskdiscovery", 3, "Branch naming convention documented", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("commit-convention", "taskdiscovery", 3, "Commit convention documented", async () => ({
			pass: false,
			details: "Override required",
		})),

		// =========================================================================
		// PILLAR 9: PRODUCT & EXPERIMENTATION
		// =========================================================================
		defineCheck("feature-flags", "product", 3, "Feature flags configured", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("analytics", "product", 4, "Analytics instrumented", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("ab-testing", "product", 5, "A/B testing framework", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("monitoring-dashboards", "product", 4, "Monitoring dashboards", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("error-budgets", "product", 5, "Error budgets defined", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("release-process", "product", 3, "Release process documented", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("ci-configured", "product", 1, "CI pipeline configured", async () => ({
			pass: false,
			details: "Override required",
		})),

		defineCheck("ci-runs-tests", "product", 2, "CI runs tests on every PR", async () => ({
			pass: false,
			details: "Override required",
		})),
	];

	// Register all checks
	checkRegistry.registerChecks(checks);
}

// Auto-register on module load
registerStandardChecks();

export { registerStandardChecks as default };
