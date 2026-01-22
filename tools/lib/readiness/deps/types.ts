/**
 * @fileoverview Dependency parsing types
 * @module kb-tools/lib/readiness/deps/types
 *
 * @description
 * Shared types for dependency parsing across multiple package managers
 * and build systems (npm, Go, Python, Rust, Java).
 */

import type { Language } from "../../language-detection.js";

// ============================================================================
// Core Types
// ============================================================================

/**
 * A parsed dependency from a manifest file
 */
export interface Dependency {
	/** Package name (e.g., "lodash", "go.uber.org/zap") */
	name: string;
	/** Version constraint (e.g., "^4.17.21", "v1.27.0") */
	version: string;
	/** Dependency type */
	type: DependencyType;
	/** Resolved version from lockfile (if available) */
	resolved?: string;
	/** Whether this is optional */
	optional?: boolean;
}

/**
 * Dependency classification
 */
export type DependencyType =
	| "production"
	| "development"
	| "optional"
	| "peer"
	| "build";

/**
 * Parsed dependency manifest
 */
export interface DependencyManifest {
	/** Absolute path to the manifest file */
	path: string;
	/** Manifest type */
	type: ManifestType;
	/** Production dependencies */
	dependencies: Dependency[];
	/** Development dependencies */
	devDependencies: Dependency[];
	/** Package scripts (for npm-like manifests) */
	scripts?: Record<string, string>;
	/** Package name (if defined in manifest) */
	name?: string;
	/** Package version (if defined in manifest) */
	version?: string;
	/** Additional metadata */
	metadata?: Record<string, unknown>;
}

/**
 * Supported manifest types
 */
export type ManifestType =
	| "npm"
	| "bun"
	| "pnpm"
	| "yarn"
	| "go"
	| "python-pyproject"
	| "python-requirements"
	| "python-poetry"
	| "rust"
	| "maven"
	| "gradle";

// ============================================================================
// Library Detection
// ============================================================================

/**
 * Result of library detection
 */
export interface LibraryMatch {
	/** Whether a matching library was found */
	found: boolean;
	/** The matched library name */
	library?: string;
	/** The version constraint */
	version?: string;
	/** Whether it's a dev dependency */
	isDev?: boolean;
}

/**
 * Library category
 */
export type LibraryCategory =
	| "logging"
	| "errorTracking"
	| "testing"
	| "featureFlags"
	| "analytics"
	| "tracing"
	| "metrics"
	| "validation"
	| "orm"
	| "webFramework";

/**
 * Library mappings by category and language
 */
export type LibraryMappings = {
	[K in LibraryCategory]: {
		[L in Language]?: readonly string[];
	};
};

// ============================================================================
// Parser Interface
// ============================================================================

/**
 * Options for parsing
 */
export interface ParseOptions {
	/** Include dev dependencies (default: true) */
	includeDev?: boolean;
	/** Parse lockfile for resolved versions (default: false) */
	parseLockfile?: boolean;
}

/**
 * Parser function signature
 */
export type ManifestParser = (
	filepath: string,
	options?: ParseOptions
) => Promise<DependencyManifest | null>;
