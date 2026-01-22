/**
 * @fileoverview Java language adapter
 * @module kb-tools/lib/adapters/java
 *
 * @description
 * Implements readiness checks for Java codebases.
 * Supports Maven (pom.xml) and Gradle (build.gradle) build systems.
 * Detects common tools: Checkstyle, SpotBugs, JUnit, Mockito.
 *
 * Uses shared checks for common patterns (README, CI, security, etc.)
 * and only implements Java-specific checks here.
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
// Helper Functions
// ============================================================================

/**
 * Detect the build system (Maven or Gradle)
 */
async function detectBuildSystem(
	appPath: string
): Promise<{ type: "maven" | "gradle" | null; configPath: string | null }> {
	if (await fileExists(path.join(appPath, "pom.xml"))) {
		return { type: "maven", configPath: "pom.xml" };
	}
	if (await fileExists(path.join(appPath, "build.gradle"))) {
		return { type: "gradle", configPath: "build.gradle" };
	}
	if (await fileExists(path.join(appPath, "build.gradle.kts"))) {
		return { type: "gradle", configPath: "build.gradle.kts" };
	}
	return { type: null, configPath: null };
}

// ============================================================================
// Java-Specific Check Runners
// ============================================================================

const javaSpecificRunners: Record<string, CheckRunner> = {
	// =========================================================================
	// STYLE & VALIDATION (Java-specific)
	// =========================================================================

	"linter-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const buildSystem = await detectBuildSystem(appPath);

		// Check for Checkstyle
		if (await fileExists(path.join(appPath, "checkstyle.xml")) ||
			await fileExists(path.join(appPath, "config/checkstyle/checkstyle.xml"))) {
			return { pass: true, tool: "Checkstyle", configPath: "checkstyle.xml" };
		}

		// Check for PMD
		if (await fileExists(path.join(appPath, "pmd.xml")) ||
			await fileExists(path.join(appPath, "ruleset.xml"))) {
			return { pass: true, tool: "PMD", configPath: "pmd.xml" };
		}

		// Check for SpotBugs
		if (await fileExists(path.join(appPath, "spotbugs-exclude.xml"))) {
			return { pass: true, tool: "SpotBugs", configPath: "spotbugs-exclude.xml" };
		}

		// Check build config for linting plugins
		if (buildSystem.type === "maven") {
			const pom = await readText(path.join(appPath, "pom.xml"));
			if (pom?.includes("checkstyle") || pom?.includes("spotbugs") || pom?.includes("pmd")) {
				return { pass: true, details: "Linting plugin in pom.xml" };
			}
		}

		if (buildSystem.type === "gradle") {
			const buildFile = await readText(path.join(appPath, buildSystem.configPath!));
			if (buildFile?.includes("checkstyle") || buildFile?.includes("spotbugs") || buildFile?.includes("pmd")) {
				return { pass: true, details: "Linting plugin in build.gradle" };
			}
		}

		return { pass: false, details: "No linter configured (Checkstyle/SpotBugs recommended)" };
	},

	"type-checker-strict": async (ctx: CheckContext): Promise<CheckResult> => {
		const buildSystem = await detectBuildSystem(ctx.app.path);

		if (buildSystem.type) {
			return { pass: true, tool: "Java compiler", details: "Java is statically typed" };
		}

		return { pass: false, details: "No build configuration found" };
	},

	"formatter-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const buildSystem = await detectBuildSystem(appPath);

		// Check for Google Java Format config
		if (await fileExists(path.join(appPath, ".google-java-format"))) {
			return { pass: true, tool: "google-java-format" };
		}

		// Check for Spotless
		if (buildSystem.type === "gradle") {
			const buildFile = await readText(path.join(appPath, buildSystem.configPath!));
			if (buildFile?.includes("spotless")) {
				return { pass: true, tool: "Spotless" };
			}
		}

		if (buildSystem.type === "maven") {
			const pom = await readText(path.join(appPath, "pom.xml"));
			if (pom?.includes("spotless") || pom?.includes("formatter-maven-plugin")) {
				return { pass: true, tool: "Spotless/Formatter Maven Plugin" };
			}
		}

		// Check for EditorConfig (general but useful)
		if (await fileExists(path.join(appPath, ".editorconfig"))) {
			return { pass: true, tool: "EditorConfig", details: "Partial formatting" };
		}

		return { pass: false, details: "No formatter configured (Spotless recommended)" };
	},

	"no-lint-ignores": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			// Check for @SuppressWarnings annotations
			const result = await $`grep -r "@SuppressWarnings" --include="*.java" ${ctx.app.path} 2>/dev/null | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			return {
				pass: count < 20,
				details: `${count} @SuppressWarnings annotations`,
			};
		} catch {
			return { pass: true, details: "No Java files found" };
		}
	},

	"strict-mode": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const buildSystem = await detectBuildSystem(appPath);

		if (buildSystem.type === "maven") {
			const pom = await readText(path.join(appPath, "pom.xml"));
			if (pom?.includes("-Werror") || pom?.includes("failOnWarning")) {
				return { pass: true, details: "Warnings as errors enabled" };
			}
		}

		if (buildSystem.type === "gradle") {
			const buildFile = await readText(path.join(appPath, buildSystem.configPath!));
			if (buildFile?.includes("-Werror") || buildFile?.includes("failOnWarning")) {
				return { pass: true, details: "Warnings as errors enabled" };
			}
		}

		return { pass: false, details: "No strict mode (consider -Werror)" };
	},

	"zero-lint-errors": async (ctx: CheckContext): Promise<CheckResult> => {
		const buildSystem = await detectBuildSystem(ctx.app.path);

		if (!buildSystem.type) {
			return { pass: false, details: "No build system found" };
		}

		try {
			if (buildSystem.type === "maven") {
				await runWithTimeout(
					$`cd ${ctx.app.path} && mvn compile -q 2>&1`.quiet(),
					180000,
				);
			} else {
				await runWithTimeout(
					$`cd ${ctx.app.path} && ./gradlew compileJava -q 2>&1`.quiet(),
					180000,
				);
			}
			return { pass: true, details: "Compilation clean" };
		} catch {
			return { pass: false, details: "Compilation has warnings/errors" };
		}
	},

	// =========================================================================
	// BUILD SYSTEM (Java-specific)
	// =========================================================================

	"dependency-manifest": async (ctx: CheckContext): Promise<CheckResult> => {
		const buildSystem = await detectBuildSystem(ctx.app.path);

		if (buildSystem.type) {
			return {
				pass: true,
				tool: buildSystem.type === "maven" ? "Maven" : "Gradle",
				configPath: buildSystem.configPath!,
			};
		}

		return { pass: false, details: "No pom.xml or build.gradle found" };
	},

	"package-json-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		const buildSystem = await detectBuildSystem(ctx.app.path);
		return {
			pass: Boolean(buildSystem.type),
			details: buildSystem.type ? `${buildSystem.configPath} found` : "No build config",
		};
	},

	"lockfile-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		// Gradle lock file
		if (await fileExists(path.join(appPath, "gradle.lockfile"))) {
			return { pass: true, tool: "Gradle", configPath: "gradle.lockfile" };
		}

		// Maven doesn't have a lockfile by default, but check for enforcer
		const pom = await readText(path.join(appPath, "pom.xml"));
		if (pom?.includes("maven-enforcer-plugin") || pom?.includes("dependencyConvergence")) {
			return { pass: true, tool: "Maven Enforcer", details: "Dependency convergence enforced" };
		}

		// Check for dependency lock config in gradle
		const buildFile = await readText(path.join(appPath, "build.gradle")) ||
			await readText(path.join(appPath, "build.gradle.kts"));
		if (buildFile?.includes("dependencyLocking")) {
			return { pass: true, tool: "Gradle", details: "Locking enabled but file missing" };
		}

		return { pass: false, details: "No lockfile (Maven doesn't require one)" };
	},

	"build-defined": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const buildSystem = await detectBuildSystem(appPath);

		if (buildSystem.type === "maven") {
			return { pass: true, details: "mvn package" };
		}

		if (buildSystem.type === "gradle") {
			return { pass: true, details: "./gradlew build" };
		}

		const readme = await readText(path.join(appPath, "README.md"));
		if (readme?.includes("mvn") || readme?.includes("gradle")) {
			return { pass: true, details: "Build command documented" };
		}

		return { pass: false, details: "No build command" };
	},

	"deps-installed": async (ctx: CheckContext): Promise<CheckResult> => {
		const buildSystem = await detectBuildSystem(ctx.app.path);

		if (!buildSystem.type) {
			return { pass: false, details: "No build system" };
		}

		try {
			if (buildSystem.type === "maven") {
				await $`cd ${ctx.app.path} && mvn dependency:resolve -q 2>&1`.quiet();
			} else {
				await $`cd ${ctx.app.path} && ./gradlew dependencies --quiet 2>&1`.quiet();
			}
			return { pass: true, details: "Dependencies resolved" };
		} catch {
			return { pass: false, details: "Dependency resolution failed" };
		}
	},

	"build-succeeds": async (ctx: CheckContext): Promise<CheckResult> => {
		if (ctx.options.skipBuild) {
			return { pass: true, skipped: true, details: "Skipped via --skip-build" };
		}

		const buildSystem = await detectBuildSystem(ctx.app.path);

		if (!buildSystem.type) {
			return { pass: false, details: "No build system" };
		}

		try {
			if (buildSystem.type === "maven") {
				await runWithTimeout(
					$`cd ${ctx.app.path} && mvn package -DskipTests -q 2>&1`.quiet(),
					300000,
				);
			} else {
				await runWithTimeout(
					$`cd ${ctx.app.path} && ./gradlew build -x test -q 2>&1`.quiet(),
					300000,
				);
			}
			return { pass: true, details: "Build succeeded" };
		} catch {
			return { pass: false, details: "Build failed" };
		}
	},

	"reproducible-builds": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const buildSystem = await detectBuildSystem(appPath);

		if (!buildSystem.type) {
			return { pass: false, details: "No build system" };
		}

		const hasDocker = await fileExists(path.join(appPath, "Dockerfile"));
		const hasNix = await fileExists(path.join(appPath, "flake.nix"));
		const hasGradleLock = await fileExists(path.join(appPath, "gradle.lockfile"));
		const hasGradleWrapper = await fileExists(path.join(appPath, "gradle/wrapper/gradle-wrapper.properties"));
		const hasMavenWrapper = await fileExists(path.join(appPath, ".mvn/wrapper/maven-wrapper.properties"));

		if (hasNix) {
			return { pass: true, details: "Nix flake" };
		}

		if (hasDocker && (hasGradleWrapper || hasMavenWrapper)) {
			return { pass: true, details: "Docker + wrapper" };
		}

		if (hasGradleLock && hasGradleWrapper) {
			return { pass: true, details: "Gradle lockfile + wrapper" };
		}

		if (hasMavenWrapper) {
			return { pass: true, details: "Maven wrapper", confidence: 70 };
		}

		if (hasGradleWrapper) {
			return { pass: true, details: "Gradle wrapper", confidence: 70 };
		}

		return { pass: false, details: "No reproducibility guarantees" };
	},

	// =========================================================================
	// TESTING (Java-specific)
	// =========================================================================

	"tests-exist": async (ctx: CheckContext): Promise<CheckResult> => {
		const testDirs = [
			"src/test/java",
			"src/test/kotlin",
			"test",
		];

		for (const dir of testDirs) {
			if (dirExists(path.join(ctx.app.path, dir))) {
				return { pass: true, details: `${dir}/ found` };
			}
		}

		try {
			const result = await $`find ${ctx.app.path} -name "*Test.java" -o -name "*Tests.java" -o -name "*IT.java" 2>/dev/null | head -1`.quiet();
			if (result.text().trim().length > 0) {
				return { pass: true, details: "Test files found" };
			}
		} catch {
			// Ignore
		}

		return { pass: false, details: "No test files found" };
	},

	"tests-pass": async (ctx: CheckContext): Promise<CheckResult> => {
		if (ctx.options.skipTests) {
			return { pass: true, skipped: true, details: "Skipped via --skip-tests" };
		}

		const buildSystem = await detectBuildSystem(ctx.app.path);

		if (!buildSystem.type) {
			return { pass: false, details: "No build system" };
		}

		try {
			if (buildSystem.type === "maven") {
				await runWithTimeout(
					$`cd ${ctx.app.path} && mvn test -q 2>&1`.quiet(),
					300000,
				);
			} else {
				await runWithTimeout(
					$`cd ${ctx.app.path} && ./gradlew test -q 2>&1`.quiet(),
					300000,
				);
			}
			return { pass: true, details: "All tests pass" };
		} catch {
			return { pass: false, details: "Tests failed" };
		}
	},

	"integration-tests": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		// Check for integration test directories
		if (dirExists(path.join(appPath, "src/integrationTest")) ||
			dirExists(path.join(appPath, "src/it"))) {
			return { pass: true, details: "Integration test directory found" };
		}

		// Check for IT suffix files
		try {
			const result = await $`find ${appPath} -name "*IT.java" 2>/dev/null | head -1`.quiet();
			if (result.text().trim().length > 0) {
				return { pass: true, details: "*IT.java files found" };
			}
		} catch {
			// Ignore
		}

		// Check build config for integration test task
		const buildSystem = await detectBuildSystem(appPath);
		if (buildSystem.type === "gradle") {
			const buildFile = await readText(path.join(appPath, buildSystem.configPath!));
			if (buildFile?.includes("integrationTest")) {
				return { pass: true, details: "integrationTest task configured" };
			}
		}

		if (buildSystem.type === "maven") {
			const pom = await readText(path.join(appPath, "pom.xml"));
			if (pom?.includes("failsafe-maven-plugin")) {
				return { pass: true, details: "Failsafe plugin configured" };
			}
		}

		return { pass: false, details: "No integration tests" };
	},

	"test-coverage": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;
		const buildSystem = await detectBuildSystem(appPath);

		if (buildSystem.type === "maven") {
			const pom = await readText(path.join(appPath, "pom.xml"));
			if (pom?.includes("jacoco")) {
				return { pass: true, tool: "JaCoCo" };
			}
		}

		if (buildSystem.type === "gradle") {
			const buildFile = await readText(path.join(appPath, buildSystem.configPath!));
			if (buildFile?.includes("jacoco")) {
				return { pass: true, tool: "JaCoCo" };
			}
		}

		// Check CI for coverage
		const workflowsDir = path.join(ctx.repoRoot, ".github/workflows");
		if (dirExists(workflowsDir)) {
			try {
				const files = fs.readdirSync(workflowsDir);
				for (const file of files) {
					const content = await readText(path.join(workflowsDir, file));
					if (content?.includes("jacoco") || content?.includes("codecov")) {
						return { pass: true, details: "Coverage in CI" };
					}
				}
			} catch {
				// Ignore
			}
		}

		return { pass: false, details: "No coverage configured (JaCoCo recommended)" };
	},

	"tests-fast": async (ctx: CheckContext): Promise<CheckResult> => {
		if (ctx.options.skipTests) {
			return { pass: true, skipped: true, details: "Skipped via --skip-tests" };
		}

		const buildSystem = await detectBuildSystem(ctx.app.path);

		if (!buildSystem.type) {
			return { pass: false, details: "No build system" };
		}

		const start = Date.now();
		try {
			if (buildSystem.type === "maven") {
				await runWithTimeout(
					$`cd ${ctx.app.path} && mvn test -q 2>&1`.quiet(),
					300000,
				);
			} else {
				await runWithTimeout(
					$`cd ${ctx.app.path} && ./gradlew test -q 2>&1`.quiet(),
					300000,
				);
			}
			const elapsed = Date.now() - start;
			return {
				pass: elapsed < 300000,
				details: `${Math.floor(elapsed / 1000)}s`,
			};
		} catch {
			return { pass: false, details: "Tests failed" };
		}
	},

	// =========================================================================
	// OBSERVABILITY (Java-specific console output)
	// =========================================================================

	"console-logs-minimal": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			const result = await $`grep -r "System.out.print\\|System.err.print" --include="*.java" ${ctx.app.path} 2>/dev/null | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			return {
				pass: count < 20,
				details: `${count} System.out/err.print calls`,
			};
		} catch {
			return { pass: true, details: "No Java files found" };
		}
	},

	// =========================================================================
	// CI (Java-specific test commands)
	// =========================================================================

	"ci-runs-tests": async (ctx: CheckContext): Promise<CheckResult> => {
		const appWorkflows = path.join(ctx.app.path, ".github/workflows");
		const repoWorkflows = path.join(ctx.repoRoot, ".github/workflows");
		const workflowsDir = dirExists(appWorkflows) ? appWorkflows : repoWorkflows;

		if (!dirExists(workflowsDir)) {
			return { pass: false, details: "No CI workflows" };
		}

		try {
			const result = await $`grep -r "mvn test\\|gradle.*test\\|./gradlew test" ${workflowsDir} 2>/dev/null | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			return { pass: count > 0, details: count > 0 ? "Tests in CI" : "No tests in CI" };
		} catch {
			return { pass: false, details: "Error scanning workflows" };
		}
	},

	// =========================================================================
	// TASK DISCOVERY (Java-specific)
	// =========================================================================

	"npm-scripts": async (ctx: CheckContext): Promise<CheckResult> => {
		const buildSystem = await detectBuildSystem(ctx.app.path);

		if (buildSystem.type === "maven") {
			return { pass: true, details: "Maven lifecycle phases" };
		}

		if (buildSystem.type === "gradle") {
			try {
				const result = await $`cd ${ctx.app.path} && ./gradlew tasks --quiet 2>&1 | head -20`.quiet();
				const tasks = result.text().split("\n").filter((l) => l.trim()).length;
				return { pass: true, details: `${tasks}+ Gradle tasks` };
			} catch {
				return { pass: true, tool: "Gradle", details: "Tasks available" };
			}
		}

		// Check for Makefile as fallback
		const makefile = await readText(path.join(ctx.app.path, "Makefile"));
		if (makefile) {
			const targets = makefile.match(/^[a-zA-Z_-]+:/gm);
			if (targets && targets.length > 0) {
				return { pass: true, details: `${targets.length} Makefile targets` };
			}
		}

		return { pass: false, details: "No task runner configured" };
	},

	"watch-mode": async (ctx: CheckContext): Promise<CheckResult> => {
		const buildSystem = await detectBuildSystem(ctx.app.path);

		if (buildSystem.type === "gradle") {
			const buildFile = await readText(path.join(ctx.app.path, buildSystem.configPath!));
			if (buildFile?.includes("continuous") || buildFile?.includes("--continuous")) {
				return { pass: true, tool: "Gradle continuous", details: "--continuous flag" };
			}
		}

		// Check for Spring Boot DevTools
		const pom = await readText(path.join(ctx.app.path, "pom.xml"));
		const gradle = await readText(path.join(ctx.app.path, "build.gradle"));

		if (pom?.includes("spring-boot-devtools") || gradle?.includes("spring-boot-devtools")) {
			return { pass: true, tool: "Spring DevTools" };
		}

		// Check README for watch instructions
		const readme = await readText(path.join(ctx.app.path, "README.md"));
		if (readme?.includes("--continuous") || readme?.includes("watch")) {
			return { pass: true, details: "Watch mode documented" };
		}

		return { pass: false, details: "No watch mode (consider Gradle --continuous)" };
	},

	// =========================================================================
	// DOCUMENTATION (Java-specific)
	// =========================================================================

	"inline-docs": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			// Check for Javadoc comments
			const result = await $`grep -r "/\\*\\*" --include="*.java" ${ctx.app.path} 2>/dev/null | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			return {
				pass: count > 10,
				details: `${count} Javadoc comments`,
			};
		} catch {
			return { pass: false, details: "No Javadoc found" };
		}
	},
};

// ============================================================================
// Adapter Export
// ============================================================================

/**
 * Java language adapter
 * Uses shared checks for common patterns (README, CI, security)
 * and Java-specific checks for language-specific patterns
 */
export const javaAdapter = createLanguageAdapter({
	language: "java",
	displayName: "Java",
	runners: javaSpecificRunners,
});
