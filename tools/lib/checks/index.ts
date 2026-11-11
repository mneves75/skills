/**
 * @fileoverview Standard check definitions for Agent Readiness
 * @module kb-tools/lib/checks
 *
 * @description
 * Registers all standard check definitions with the check registry.
 * These are language-agnostic definitions - the actual implementation
 * comes from language-specific adapters.
 */

import { checkRegistry, defineCheck } from "../check-registry.js";

// ============================================================================
// Check Definitions
// ============================================================================

/**
 * Register all standard checks
 */
export function registerStandardChecks(): void {
	const checks = [
		// =========================================================================
		// PILLAR 1: STYLE & VALIDATION
		// =========================================================================
		defineCheck("linter-exists", "style", 1, "Linter configured"),

		defineCheck("type-checker-strict", "style", 1, "Type checker configured"),

		defineCheck("formatter-exists", "style", 2, "Formatter configured"),

		defineCheck("pre-commit-hooks", "style", 3, "Pre-commit hooks installed"),

		defineCheck("no-lint-ignores", "style", 2, "No linter ignore comments"),

		defineCheck("no-unsafe-types", "style", 2, "No unsafe type casts"),

		defineCheck("strict-mode", "style", 3, "Strict mode enabled"),

		defineCheck("zero-lint-errors", "style", 4, "Zero lint errors"),

		// =========================================================================
		// PILLAR 2: BUILD SYSTEM
		// =========================================================================
		defineCheck("dependency-manifest", "build", 1, "Dependency manifest exists"),

		defineCheck("lockfile-exists", "build", 1, "Lock file committed"),

		defineCheck("package-json-exists", "build", 1, "Package manifest exists"),

		defineCheck("build-defined", "build", 1, "Build command documented"),

		defineCheck("ci-pipeline", "build", 2, "CI pipeline configured"),

		defineCheck("reproducible-builds", "build", 4, "Build is deterministic"),

		defineCheck("no-deprecated-deps", "build", 3, "No deprecated dependencies"),

		defineCheck("build-succeeds", "build", 3, "Build succeeds"),

		defineCheck("deps-installed", "build", 2, "Dependencies installed"),

		// =========================================================================
		// PILLAR 3: TESTING
		// =========================================================================
		defineCheck("test-framework", "testing", 1, "Test framework configured"),

		defineCheck("test-coverage", "testing", 5, "Coverage threshold defined"),

		defineCheck("tests-pass", "testing", 2, "Tests pass"),

		defineCheck("integration-tests", "testing", 3, "Integration tests exist"),

		defineCheck("e2e-tests", "testing", 4, "E2E tests exist"),

		defineCheck("test-isolation", "testing", 3, "Tests are isolated"),

		defineCheck("tests-fast", "testing", 4, "Tests complete in <5 minutes"),

		defineCheck("tests-exist", "testing", 1, "At least one test exists"),

		// =========================================================================
		// PILLAR 4: DOCUMENTATION
		// =========================================================================
		defineCheck("readme-exists", "documentation", 1, "README exists"),

		defineCheck("architecture-docs", "documentation", 3, "Architecture documented"),

		defineCheck("api-documentation", "documentation", 3, "API documentation exists"),

		defineCheck("changelog-exists", "documentation", 2, "CHANGELOG exists"),

		defineCheck("inline-docs", "documentation", 2, "Inline documentation"),

		defineCheck("examples-exist", "documentation", 3, "Examples exist"),

		defineCheck("claude-md-exists", "documentation", 2, "CLAUDE.md or AGENTS.md exists"),

		defineCheck("claude-md-has-commands", "documentation", 3, "CLAUDE.md includes build/test commands"),

		defineCheck("claude-md-concise", "documentation", 4, "CLAUDE.md is concise (<300 lines)"),

		defineCheck("claude-md-recent", "documentation", 5, "CLAUDE.md updated within 30 days"),

		// =========================================================================
		// PILLAR 5: DEVELOPMENT ENVIRONMENT
		// =========================================================================
		defineCheck("env-setup-script", "devenv", 2, "Setup script exists"),

		defineCheck("devcontainer", "devenv", 3, "Devcontainer configured"),

		defineCheck("editor-config", "devenv", 2, ".editorconfig exists"),

		defineCheck("debug-configs", "devenv", 3, "Debug configurations"),

		defineCheck("local-env-docs", "devenv", 3, "Local environment documented"),

		defineCheck("watch-mode", "devenv", 2, "Watch mode available"),

		defineCheck("gitignore-exists", "devenv", 1, ".gitignore exists"),

		defineCheck("env-example", "devenv", 3, "Environment template exists"),

		defineCheck("docker-compose", "devenv", 4, "Docker Compose for local services"),

		// =========================================================================
		// PILLAR 6: DEBUGGING & OBSERVABILITY
		// =========================================================================
		defineCheck("structured-logging", "observability", 2, "Structured logging configured"),

		defineCheck("error-tracking", "observability", 3, "Error tracking configured"),

		defineCheck("tracing", "observability", 4, "Distributed tracing configured"),

		defineCheck("metrics", "observability", 5, "Metrics collection configured"),

		defineCheck("health-endpoints", "observability", 3, "Health check endpoints"),

		defineCheck("log-levels", "observability", 2, "Log levels configured"),

		defineCheck("console-logs-minimal", "observability", 1, "Minimal console.log usage"),

		// =========================================================================
		// PILLAR 7: SECURITY
		// =========================================================================
		defineCheck("security-scanning", "security", 3, "Security scanning configured"),

		defineCheck("secrets-management", "security", 2, "No secrets in repository"),

		defineCheck("auth-implementation", "security", 3, "Authentication implemented"),

		defineCheck("input-validation", "security", 2, "Input validation"),

		defineCheck("audit-logging", "security", 4, "Audit logging configured"),

		defineCheck("vulnerability-policy", "security", 5, "Vulnerability policy defined"),

		defineCheck("git-initialized", "security", 1, "Git repository initialized"),

		defineCheck("codeowners-exists", "security", 3, "CODEOWNERS file exists"),

		defineCheck("branch-protection-documented", "security", 4, "Branch protection documented"),

		defineCheck("dependency-scanning", "security", 5, "Dependency scanning configured"),

		// =========================================================================
		// PILLAR 8: TASK DISCOVERY
		// =========================================================================
		defineCheck("task-definitions", "taskdiscovery", 1, "Task definitions exist"),

		defineCheck("npm-scripts", "taskdiscovery", 1, "NPM scripts defined"),

		defineCheck("makefile", "taskdiscovery", 2, "Makefile exists"),

		defineCheck("common-aliases", "taskdiscovery", 3, "Common task aliases"),

		defineCheck("task-documentation", "taskdiscovery", 2, "Tasks documented"),

		defineCheck("ci-tasks-aligned", "taskdiscovery", 4, "CI tasks aligned with local"),

		defineCheck("pr-template", "taskdiscovery", 1, "PR template exists"),

		defineCheck("issue-templates", "taskdiscovery", 2, "Issue templates exist"),

		defineCheck("contributing-guide", "taskdiscovery", 2, "CONTRIBUTING.md exists"),

		defineCheck("branch-naming", "taskdiscovery", 3, "Branch naming convention documented"),

		defineCheck("commit-convention", "taskdiscovery", 3, "Commit convention documented"),

		// =========================================================================
		// PILLAR 9: PRODUCT & EXPERIMENTATION
		// =========================================================================
		defineCheck("feature-flags", "product", 3, "Feature flags configured"),

		defineCheck("analytics", "product", 4, "Analytics instrumented"),

		defineCheck("ab-testing", "product", 5, "A/B testing framework"),

		defineCheck("monitoring-dashboards", "product", 4, "Monitoring dashboards"),

		defineCheck("error-budgets", "product", 5, "Error budgets defined"),

		defineCheck("release-process", "product", 3, "Release process documented"),

		defineCheck("ci-configured", "product", 1, "CI pipeline configured"),

		defineCheck("ci-runs-tests", "product", 2, "CI runs tests on every PR"),
	];

	// Register all checks
	checkRegistry.registerChecks(checks);
}

// Auto-register on module load
registerStandardChecks();

export { registerStandardChecks as default };
