/**
 * @fileoverview Dependency parsing module
 * @module kb-tools/lib/readiness/deps
 *
 * @description
 * Unified interface for parsing dependency manifests across multiple
 * package managers and build systems. Provides library detection
 * for common categories (logging, testing, error tracking, etc.).
 */

import path from "node:path";
import type { Language } from "../../language-detection.js";
import type {
	Dependency,
	DependencyManifest,
	LibraryCategory,
	LibraryMatch,
	LibraryMappings,
	ParseOptions,
} from "./types.js";

// Re-export types
export * from "./types.js";

// Import parsers
import { parsePackageJson, hasScript, getScriptNames } from "./package-json.js";
import { parseGoMod, moduleMatches } from "./go-mod.js";
import { parsePyProject, parseRequirementsTxt } from "./pyproject.js";
import { parseCargoToml } from "./cargo-toml.js";

// Re-export helpers
export { hasScript, getScriptNames, moduleMatches };

// ============================================================================
// Library Mappings
// ============================================================================

/**
 * Known libraries by category and language
 * Used for detecting if a codebase has certain capabilities
 */
export const LIBRARY_MAPPINGS: LibraryMappings = {
	logging: {
		typescript: ["pino", "winston", "bunyan", "consola", "tslog", "log4js", "roarr"],
		javascript: ["pino", "winston", "bunyan", "consola", "log4js", "debug"],
		go: [
			"go.uber.org/zap",
			"github.com/rs/zerolog",
			"log/slog",
			"github.com/sirupsen/logrus",
			"github.com/apex/log",
		],
		python: ["structlog", "loguru", "python-json-logger", "logging", "logbook"],
		rust: ["tracing", "log", "slog", "env_logger", "fern", "flexi_logger"],
		java: ["org.slf4j", "log4j", "ch.qos.logback", "org.apache.logging.log4j"],
	},
	errorTracking: {
		typescript: [
			"@sentry/node",
			"@sentry/bun",
			"bugsnag",
			"rollbar",
			"@honeybadger-io/js",
			"@airbrake/node",
		],
		javascript: ["@sentry/node", "bugsnag", "rollbar", "@honeybadger-io/js"],
		go: [
			"github.com/getsentry/sentry-go",
			"github.com/bugsnag/bugsnag-go",
			"github.com/rollbar/rollbar-go",
		],
		python: ["sentry-sdk", "bugsnag", "rollbar", "raygun4py", "airbrake"],
		rust: ["sentry", "sentry-core", "honeybadger"],
		java: ["io.sentry", "com.bugsnag", "com.rollbar"],
	},
	testing: {
		typescript: ["vitest", "jest", "@jest/core", "mocha", "ava", "tap"],
		javascript: ["vitest", "jest", "mocha", "ava", "tap", "jasmine"],
		go: [
			"testing",
			"github.com/stretchr/testify",
			"github.com/onsi/ginkgo",
			"github.com/onsi/gomega",
		],
		python: ["pytest", "unittest", "nose2", "hypothesis", "ward"],
		rust: ["test", "proptest", "quickcheck", "rstest"],
		java: ["junit", "org.junit", "org.testng", "org.mockito", "org.assertj"],
	},
	featureFlags: {
		typescript: [
			"@growthbook/growthbook",
			"launchdarkly-node-server-sdk",
			"@unleash/client",
			"flagsmith",
			"@vercel/flags",
		],
		javascript: [
			"@growthbook/growthbook",
			"launchdarkly-node-server-sdk",
			"@unleash/client",
		],
		go: [
			"github.com/launchdarkly/go-server-sdk",
			"github.com/Unleash/unleash-client-go",
			"github.com/growthbook/growthbook-golang",
		],
		python: ["launchdarkly-server-sdk", "growthbook", "flagsmith", "unleash-client"],
		rust: ["launchdarkly-server-sdk", "unleash-client"],
		java: ["com.launchdarkly", "io.getunleash", "com.growthbook"],
	},
	analytics: {
		typescript: [
			"@segment/analytics-node",
			"posthog-node",
			"mixpanel",
			"@amplitude/node",
			"plausible-tracker",
		],
		javascript: ["@segment/analytics-node", "posthog-js", "mixpanel", "amplitude-js"],
		go: [
			"gopkg.in/segmentio/analytics-go.v3",
			"github.com/posthog/posthog-go",
			"github.com/amplitude/analytics-go",
		],
		python: ["segment-analytics-python", "posthog", "mixpanel", "amplitude-analytics"],
		rust: ["segment", "posthog-rs", "amplitude"],
		java: ["com.segment.analytics", "com.posthog.java", "com.mixpanel"],
	},
	tracing: {
		typescript: [
			"@opentelemetry/sdk-trace-node",
			"@opentelemetry/auto-instrumentations-node",
			"dd-trace",
			"@opentelemetry/api",
		],
		javascript: ["@opentelemetry/sdk-trace-node", "@opentelemetry/api", "dd-trace"],
		go: [
			"go.opentelemetry.io/otel",
			"gopkg.in/DataDog/dd-trace-go.v1",
			"github.com/opentracing/opentracing-go",
		],
		python: ["opentelemetry-sdk", "ddtrace", "jaeger-client", "opentelemetry-api"],
		rust: ["opentelemetry", "tracing-opentelemetry", "datadog-tracing"],
		java: ["io.opentelemetry", "io.jaegertracing", "com.datadoghq"],
	},
	metrics: {
		typescript: [
			"prom-client",
			"@opentelemetry/sdk-metrics",
			"hot-shots",
			"statsd-client",
		],
		javascript: ["prom-client", "@opentelemetry/sdk-metrics", "hot-shots"],
		go: [
			"github.com/prometheus/client_golang",
			"go.opentelemetry.io/otel/metric",
			"github.com/DataDog/datadog-go",
		],
		python: ["prometheus-client", "opentelemetry-sdk", "datadog", "statsd"],
		rust: ["metrics", "prometheus", "opentelemetry-prometheus"],
		java: ["io.micrometer", "io.prometheus", "io.opentelemetry.sdk.metrics"],
	},
	validation: {
		typescript: ["zod", "yup", "joi", "superstruct", "valibot", "@sinclair/typebox"],
		javascript: ["joi", "yup", "ajv", "validator"],
		go: [
			"github.com/go-playground/validator",
			"github.com/go-ozzo/ozzo-validation",
		],
		python: ["pydantic", "marshmallow", "cerberus", "attrs"],
		rust: ["validator", "garde", "serde_valid"],
		java: ["javax.validation", "org.hibernate.validator"],
	},
	orm: {
		typescript: [
			"drizzle-orm",
			"prisma",
			"@prisma/client",
			"typeorm",
			"sequelize",
			"kysely",
		],
		javascript: ["sequelize", "knex", "mongoose", "typeorm"],
		go: [
			"gorm.io/gorm",
			"github.com/go-pg/pg",
			"entgo.io/ent",
			"github.com/uptrace/bun",
		],
		python: ["sqlalchemy", "django", "tortoise-orm", "peewee", "pony"],
		rust: ["diesel", "sea-orm", "sqlx", "tokio-postgres"],
		java: ["org.hibernate", "org.springframework.data.jpa", "org.mybatis"],
	},
	webFramework: {
		typescript: ["express", "fastify", "hono", "elysia", "@nestjs/core", "koa"],
		javascript: ["express", "fastify", "koa", "hapi"],
		go: [
			"github.com/gin-gonic/gin",
			"github.com/labstack/echo",
			"github.com/gofiber/fiber",
			"net/http",
		],
		python: ["fastapi", "flask", "django", "starlette", "litestar"],
		rust: ["actix-web", "axum", "rocket", "warp", "tide"],
		java: [
			"org.springframework.boot",
			"io.quarkus",
			"io.micronaut",
			"jakarta.servlet",
		],
	},
};

// ============================================================================
// Main API
// ============================================================================

/**
 * Parse dependencies from a project directory
 * Automatically detects the manifest file based on language
 */
export async function parseDependencies(
	appPath: string,
	language: Language,
	options: ParseOptions = {}
): Promise<DependencyManifest | null> {
	switch (language) {
		case "typescript":
		case "javascript":
			return parsePackageJson(path.join(appPath, "package.json"), options);

		case "go":
			return parseGoMod(path.join(appPath, "go.mod"), options);

		case "python": {
			// Try pyproject.toml first
			const pyproject = await parsePyProject(
				path.join(appPath, "pyproject.toml"),
				options
			);
			if (pyproject) return pyproject;

			// Fall back to requirements.txt
			return parseRequirementsTxt(
				path.join(appPath, "requirements.txt"),
				options
			);
		}

		case "rust":
			return parseCargoToml(path.join(appPath, "Cargo.toml"), options);

		case "java": {
			// Check for pom.xml or build.gradle
			// For now, return null - Java parsing is more complex
			// and will be added in the Java adapter
			return null;
		}

		default:
			return null;
	}
}

/**
 * Check if a manifest contains any of the specified libraries
 */
export function hasLibrary(
	manifest: DependencyManifest | null,
	libraries: readonly string[]
): LibraryMatch {
	if (!manifest) {
		return { found: false };
	}

	// Check all dependencies
	const allDeps = [...manifest.dependencies, ...manifest.devDependencies];

	for (const lib of libraries) {
		for (const dep of allDeps) {
			// Exact match or prefix match (for Go modules)
			if (
				dep.name === lib ||
				dep.name.startsWith(lib + "/") ||
				lib.startsWith(dep.name + "/")
			) {
				return {
					found: true,
					library: dep.name,
					version: dep.version,
					isDev: dep.type === "development",
				};
			}
		}
	}

	return { found: false };
}

/**
 * Check if a manifest has a library in a specific category
 */
export function hasLibraryCategory(
	manifest: DependencyManifest | null,
	category: LibraryCategory,
	language: Language
): LibraryMatch {
	const libraries = LIBRARY_MAPPINGS[category][language];
	if (!libraries) {
		return { found: false };
	}
	return hasLibrary(manifest, libraries);
}

/**
 * Get all detected capabilities from a manifest
 */
export function detectCapabilities(
	manifest: DependencyManifest | null,
	language: Language
): Record<LibraryCategory, LibraryMatch> {
	const categories = Object.keys(LIBRARY_MAPPINGS) as LibraryCategory[];
	const result: Record<LibraryCategory, LibraryMatch> = {} as Record<
		LibraryCategory,
		LibraryMatch
	>;

	for (const category of categories) {
		result[category] = hasLibraryCategory(manifest, category, language);
	}

	return result;
}

/**
 * Check if the manifest has any script matching a pattern
 */
export function hasMatchingScript(
	manifest: DependencyManifest | null,
	patterns: string[]
): { found: boolean; script?: string; command?: string } {
	if (!manifest?.scripts) {
		return { found: false };
	}

	for (const [name, command] of Object.entries(manifest.scripts)) {
		for (const pattern of patterns) {
			if (
				name.toLowerCase().includes(pattern.toLowerCase()) ||
				command.toLowerCase().includes(pattern.toLowerCase())
			) {
				return { found: true, script: name, command };
			}
		}
	}

	return { found: false };
}

// ============================================================================
// Re-exports
// ============================================================================

export { parsePackageJson } from "./package-json.js";
export { parseGoMod } from "./go-mod.js";
export { parsePyProject, parseRequirementsTxt } from "./pyproject.js";
export { parseCargoToml } from "./cargo-toml.js";
