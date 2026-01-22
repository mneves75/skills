/**
 * @fileoverview Rust language adapter
 * @module kb-tools/lib/adapters/rust
 *
 * @description
 * Implements readiness checks for Rust codebases.
 * Supports Clippy, rustfmt, cargo test, and Cargo.toml.
 *
 * Uses shared checks for common patterns (README, CI, security, etc.)
 * and only implements Rust-specific checks here.
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
// Rust-Specific Check Runners
// ============================================================================

const rustSpecificRunners: Record<string, CheckRunner> = {
	// =========================================================================
	// STYLE & VALIDATION (Rust-specific)
	// =========================================================================

	"linter-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		// Check for clippy configuration
		if (await fileExists(path.join(appPath, ".clippy.toml")) ||
			await fileExists(path.join(appPath, "clippy.toml"))) {
			return { pass: true, tool: "Clippy", configPath: "clippy.toml" };
		}

		// Check Cargo.toml for clippy lints
		const cargoToml = await readText(path.join(appPath, "Cargo.toml"));
		if (cargoToml?.includes("[lints.clippy]") || cargoToml?.includes("clippy::")) {
			return { pass: true, tool: "Clippy", details: "Via Cargo.toml" };
		}

		// Check for CI with clippy
		const workflowsDir = path.join(ctx.repoRoot, ".github/workflows");
		if (dirExists(workflowsDir)) {
			try {
				const files = fs.readdirSync(workflowsDir);
				for (const file of files) {
					const content = await readText(path.join(workflowsDir, file));
					if (content?.includes("cargo clippy")) {
						return { pass: true, tool: "Clippy", details: "Via CI" };
					}
				}
			} catch {
				// Ignore
			}
		}

		// Check Makefile
		const makefile = await readText(path.join(appPath, "Makefile"));
		if (makefile?.includes("clippy")) {
			return { pass: true, tool: "Clippy", details: "Via Makefile" };
		}

		return { pass: false, details: "No Clippy configured (recommended)" };
	},

	"type-checker-strict": async (ctx: CheckContext): Promise<CheckResult> => {
		if (await fileExists(path.join(ctx.app.path, "Cargo.toml"))) {
			return { pass: true, tool: "Rust compiler", details: "Rust is statically typed" };
		}
		return { pass: false, details: "No Cargo.toml found" };
	},

	"formatter-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		// Check for rustfmt.toml
		if (await fileExists(path.join(appPath, "rustfmt.toml")) ||
			await fileExists(path.join(appPath, ".rustfmt.toml"))) {
			return { pass: true, tool: "rustfmt", configPath: "rustfmt.toml" };
		}

		// Check CI for cargo fmt
		const workflowsDir = path.join(ctx.repoRoot, ".github/workflows");
		if (dirExists(workflowsDir)) {
			try {
				const files = fs.readdirSync(workflowsDir);
				for (const file of files) {
					const content = await readText(path.join(workflowsDir, file));
					if (content?.includes("cargo fmt")) {
						return { pass: true, tool: "rustfmt", details: "Via CI" };
					}
				}
			} catch {
				// Ignore
			}
		}

		// Check Makefile
		const makefile = await readText(path.join(appPath, "Makefile"));
		if (makefile?.includes("cargo fmt")) {
			return { pass: true, tool: "rustfmt", details: "Via Makefile" };
		}

		// rustfmt is always available with cargo
		return { pass: true, tool: "rustfmt", details: "Built-in (recommend explicit config)" };
	},

	"no-lint-ignores": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			const result = await $`grep -r "#\\[allow(" --include="*.rs" ${ctx.app.path} 2>/dev/null | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			return {
				pass: count < 10,
				details: `${count} #[allow(...)] attributes`,
			};
		} catch {
			return { pass: true, details: "No Rust files found" };
		}
	},

	"no-unsafe-types": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			const result = await $`grep -r "unsafe " --include="*.rs" ${ctx.app.path} 2>/dev/null | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			return {
				pass: count < 5,
				details: `${count} unsafe blocks`,
			};
		} catch {
			return { pass: true, details: "No Rust files found" };
		}
	},

	"strict-mode": async (ctx: CheckContext): Promise<CheckResult> => {
		const cargoToml = await readText(path.join(ctx.app.path, "Cargo.toml"));

		if (cargoToml) {
			// Check for strict clippy lints
			const hasStrictLints =
				cargoToml.includes("deny(warnings)") ||
				cargoToml.includes("deny(clippy::all)") ||
				cargoToml.includes("clippy::pedantic") ||
				cargoToml.includes("[lints.clippy]");

			if (hasStrictLints) {
				return { pass: true, details: "Strict lints configured" };
			}
		}

		// Check for #![deny()] in lib.rs or main.rs
		const libRs = await readText(path.join(ctx.app.path, "src/lib.rs"));
		const mainRs = await readText(path.join(ctx.app.path, "src/main.rs"));
		const srcContent = libRs || mainRs || "";

		if (srcContent.includes("#![deny(") || srcContent.includes("#![warn(")) {
			return { pass: true, details: "Strict lints in source" };
		}

		return { pass: false, details: "No strict mode configured" };
	},

	"zero-lint-errors": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			await runWithTimeout(
				$`cd ${ctx.app.path} && cargo clippy -- -D warnings 2>&1`.quiet(),
				180000,
			);
			return { pass: true, details: "cargo clippy clean" };
		} catch {
			try {
				await $`which cargo`.quiet();
				return { pass: false, details: "Clippy warnings present" };
			} catch {
				return { pass: false, details: "Cargo not installed" };
			}
		}
	},

	// =========================================================================
	// BUILD SYSTEM (Rust-specific)
	// =========================================================================

	"dependency-manifest": async (ctx: CheckContext): Promise<CheckResult> => {
		const exists = await fileExists(path.join(ctx.app.path, "Cargo.toml"));
		return {
			pass: exists,
			details: exists ? "Cargo.toml found" : "Missing Cargo.toml",
		};
	},

	"package-json-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		const exists = await fileExists(path.join(ctx.app.path, "Cargo.toml"));
		return { pass: exists, details: exists ? "Cargo.toml found" : "Missing Cargo.toml" };
	},

	"lockfile-exists": async (ctx: CheckContext): Promise<CheckResult> => {
		if (await fileExists(path.join(ctx.app.path, "Cargo.lock"))) {
			return { pass: true, tool: "Cargo", configPath: "Cargo.lock" };
		}

		// For libraries, Cargo.lock might not be committed (check .gitignore)
		const cargoToml = await readText(path.join(ctx.app.path, "Cargo.toml"));
		if (cargoToml?.includes("[lib]") && !cargoToml.includes("[[bin]]")) {
			return { pass: true, details: "Library (Cargo.lock optional)" };
		}

		return { pass: false, details: "No Cargo.lock found" };
	},

	"build-defined": async (ctx: CheckContext): Promise<CheckResult> => {
		const makefile = await readText(path.join(ctx.app.path, "Makefile"));

		if (makefile?.includes("build:") || makefile?.includes("build :")) {
			return { pass: true, details: "Makefile build target" };
		}

		const readme = await readText(path.join(ctx.app.path, "README.md"));
		if (readme?.includes("cargo build")) {
			return { pass: true, details: "cargo build documented" };
		}

		if (await fileExists(path.join(ctx.app.path, "Cargo.toml"))) {
			return { pass: true, details: "cargo build" };
		}

		return { pass: false, details: "No build command documented" };
	},

	"deps-installed": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			await $`cd ${ctx.app.path} && cargo check 2>&1`.quiet();
			return { pass: true, details: "cargo check succeeded" };
		} catch {
			return { pass: false, details: "cargo check failed" };
		}
	},

	"build-succeeds": async (ctx: CheckContext): Promise<CheckResult> => {
		if (ctx.options.skipBuild) {
			return { pass: true, skipped: true, details: "Skipped via --skip-build" };
		}

		try {
			await runWithTimeout(
				$`cd ${ctx.app.path} && cargo build 2>&1`.quiet(),
				300000,
			);
			return { pass: true, details: "cargo build succeeded" };
		} catch {
			return { pass: false, details: "cargo build failed" };
		}
	},

	"reproducible-builds": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		const hasCargoLock = await fileExists(path.join(appPath, "Cargo.lock"));
		const hasDocker = await fileExists(path.join(appPath, "Dockerfile"));
		const hasNix = await fileExists(path.join(appPath, "flake.nix"));
		const hasRustToolchain = await fileExists(path.join(appPath, "rust-toolchain.toml")) ||
			await fileExists(path.join(appPath, "rust-toolchain"));

		if (hasNix && hasCargoLock) {
			return { pass: true, details: "Nix + Cargo.lock" };
		}

		if (hasDocker && hasCargoLock && hasRustToolchain) {
			return { pass: true, details: "Docker + Cargo.lock + rust-toolchain" };
		}

		if (hasCargoLock && hasRustToolchain) {
			return { pass: true, details: "Cargo.lock + rust-toolchain" };
		}

		if (hasCargoLock) {
			return { pass: true, details: "Cargo.lock only", confidence: 70 };
		}

		return { pass: false, details: "No determinism guarantees" };
	},

	// =========================================================================
	// TESTING (Rust-specific)
	// =========================================================================

	"tests-exist": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			// Check for #[test] or #[cfg(test)] in Rust files
			const result = await $`grep -r "#\\[test\\]\\|#\\[cfg(test)\\]" --include="*.rs" ${ctx.app.path} 2>/dev/null | head -1`.quiet();
			const found = result.text().trim().length > 0;

			if (found) {
				return { pass: true, details: "Test functions found" };
			}

			// Check for tests directory
			if (dirExists(path.join(ctx.app.path, "tests"))) {
				return { pass: true, details: "tests/ directory found" };
			}

			return { pass: false, details: "No tests found" };
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
				$`cd ${ctx.app.path} && cargo test 2>&1`.quiet(),
				180000,
			);
			return { pass: true, details: "All tests pass" };
		} catch {
			return { pass: false, details: "Tests failed" };
		}
	},

	"integration-tests": async (ctx: CheckContext): Promise<CheckResult> => {
		const appPath = ctx.app.path;

		// Check for tests/ directory (Rust convention for integration tests)
		if (dirExists(path.join(appPath, "tests"))) {
			try {
				const files = fs.readdirSync(path.join(appPath, "tests"));
				const rsFiles = files.filter((f) => f.endsWith(".rs"));
				if (rsFiles.length > 0) {
					return { pass: true, details: `${rsFiles.length} integration test files` };
				}
			} catch {
				// Ignore
			}
		}

		return { pass: false, details: "No integration tests (tests/ directory)" };
	},

	"test-coverage": async (ctx: CheckContext): Promise<CheckResult> => {
		const cargoToml = await readText(path.join(ctx.app.path, "Cargo.toml"));

		// Check for coverage tools in dev-dependencies
		if (cargoToml?.includes("cargo-tarpaulin") || cargoToml?.includes("grcov")) {
			return { pass: true, details: "Coverage tool configured" };
		}

		// Check CI for coverage
		const workflowsDir = path.join(ctx.repoRoot, ".github/workflows");
		if (dirExists(workflowsDir)) {
			try {
				const files = fs.readdirSync(workflowsDir);
				for (const file of files) {
					const content = await readText(path.join(workflowsDir, file));
					if (content?.includes("tarpaulin") || content?.includes("grcov") || content?.includes("llvm-cov")) {
						return { pass: true, details: "Coverage in CI" };
					}
				}
			} catch {
				// Ignore
			}
		}

		return { pass: false, details: "No coverage threshold" };
	},

	"tests-fast": async (ctx: CheckContext): Promise<CheckResult> => {
		if (ctx.options.skipTests) {
			return { pass: true, skipped: true, details: "Skipped via --skip-tests" };
		}

		const start = Date.now();
		try {
			await runWithTimeout(
				$`cd ${ctx.app.path} && cargo test 2>&1`.quiet(),
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

	// =========================================================================
	// DOCUMENTATION (Rust-specific commands check)
	// =========================================================================

	"inline-docs": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			// Check for doc comments (//! or ///)
			const result = await $`grep -r "///\\|//!" --include="*.rs" ${ctx.app.path} 2>/dev/null | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			return {
				pass: count > 10,
				details: `${count} doc comments`,
			};
		} catch {
			return { pass: false, details: "No doc comments found" };
		}
	},

	// =========================================================================
	// OBSERVABILITY (Rust-specific console output)
	// =========================================================================

	"console-logs-minimal": async (ctx: CheckContext): Promise<CheckResult> => {
		try {
			const result = await $`grep -r "println!\\|print!\\|dbg!" --include="*.rs" ${ctx.app.path} 2>/dev/null | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			return {
				pass: count < 20,
				details: `${count} print!/println!/dbg! calls`,
			};
		} catch {
			return { pass: true, details: "No Rust files found" };
		}
	},

	// =========================================================================
	// CI (Rust-specific test commands)
	// =========================================================================

	"ci-runs-tests": async (ctx: CheckContext): Promise<CheckResult> => {
		const appWorkflows = path.join(ctx.app.path, ".github/workflows");
		const repoWorkflows = path.join(ctx.repoRoot, ".github/workflows");
		const workflowsDir = dirExists(appWorkflows) ? appWorkflows : repoWorkflows;

		if (!dirExists(workflowsDir)) {
			return { pass: false, details: "No CI workflows" };
		}

		try {
			const result = await $`grep -r "cargo test" ${workflowsDir} 2>/dev/null | wc -l`.quiet();
			const count = Number.parseInt(result.text().trim(), 10) || 0;
			return { pass: count > 0, details: count > 0 ? "Tests in CI" : "No tests in CI" };
		} catch {
			return { pass: false, details: "Error scanning workflows" };
		}
	},

	// =========================================================================
	// TASK DISCOVERY (Rust-specific)
	// =========================================================================

	"npm-scripts": async (ctx: CheckContext): Promise<CheckResult> => {
		// Not applicable for Rust - check for Makefile targets or Cargo aliases
		const makefile = await readText(path.join(ctx.app.path, "Makefile"));
		if (makefile) {
			const targets = makefile.match(/^[a-zA-Z_-]+:/gm);
			if (targets && targets.length > 0) {
				return { pass: true, details: `${targets.length} Makefile targets` };
			}
		}

		// Check for cargo-make
		if (await fileExists(path.join(ctx.app.path, "Makefile.toml"))) {
			return { pass: true, tool: "cargo-make", configPath: "Makefile.toml" };
		}

		// Check for just
		if (await fileExists(path.join(ctx.app.path, "Justfile"))) {
			return { pass: true, tool: "Just", configPath: "Justfile" };
		}

		return { pass: false, details: "No task runner configured" };
	},

	"watch-mode": async (ctx: CheckContext): Promise<CheckResult> => {
		const cargoToml = await readText(path.join(ctx.app.path, "Cargo.toml"));

		// Check for cargo-watch in dev-dependencies or as installed tool
		if (cargoToml?.includes("cargo-watch")) {
			return { pass: true, tool: "cargo-watch" };
		}

		const makefile = await readText(path.join(ctx.app.path, "Makefile"));
		if (makefile?.includes("cargo watch") || makefile?.includes("cargo-watch")) {
			return { pass: true, tool: "cargo-watch", details: "Via Makefile" };
		}

		// Check README for watch instructions
		const readme = await readText(path.join(ctx.app.path, "README.md"));
		if (readme?.includes("cargo watch")) {
			return { pass: true, tool: "cargo-watch", details: "Documented" };
		}

		return { pass: false, details: "No watch mode (cargo-watch recommended)" };
	},
};

// ============================================================================
// Adapter Export
// ============================================================================

/**
 * Rust language adapter
 * Uses shared checks for common patterns (README, CI, security)
 * and Rust-specific checks for language-specific patterns
 */
export const rustAdapter = createLanguageAdapter({
	language: "rust",
	displayName: "Rust",
	runners: rustSpecificRunners,
});
