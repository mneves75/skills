/**
 * @fileoverview Multi-language detection with confidence scoring
 * @module kb-tools/lib/language-detection
 *
 * @description
 * Detects primary and secondary languages in a repository using
 * multiple signals: config files, source file counts, and dependencies.
 * Designed to match Factory.ai's language detection methodology.
 */

import fs from "node:fs";
import path from "node:path";

// ============================================================================
// Types
// ============================================================================

/**
 * Supported programming languages for detection
 */
export type Language =
	| "typescript"
	| "javascript"
	| "go"
	| "python"
	| "rust"
	| "java"
	| "kotlin"
	| "swift"
	| "csharp"
	| "ruby"
	| "php"
	| "unknown";

/**
 * Source of a language detection signal
 */
export type SignalSource = "config" | "source" | "dependency" | "ci";

/**
 * A single signal that contributed to language detection
 */
export interface LanguageSignal {
	/** Detected language */
	language: Language;
	/** How the signal was detected */
	source: SignalSource;
	/** File path that triggered detection */
	path: string;
	/** Signal weight (1-10, higher = more confident) */
	weight: number;
}

/**
 * Complete language detection result
 */
export interface LanguageDetection {
	/** Primary detected language */
	primary: Language;
	/** Secondary languages detected */
	secondary: Language[];
	/** Overall confidence (0-100) */
	confidence: number;
	/** All signals that contributed to detection */
	signals: LanguageSignal[];
	/** Source file counts per language */
	sourceFileCount: Partial<Record<Language, number>>;
}

// ============================================================================
// Configuration
// ============================================================================

/**
 * Config files that strongly indicate a language (weight: 10)
 */
const CONFIG_SIGNALS: Record<string, Language> = {
	// Go
	"go.mod": "go",
	"go.sum": "go",
	"go.work": "go",
	// Python
	"pyproject.toml": "python",
	"setup.py": "python",
	"setup.cfg": "python",
	"requirements.txt": "python",
	"Pipfile": "python",
	"poetry.lock": "python",
	"uv.lock": "python",
	// Rust
	"Cargo.toml": "rust",
	"Cargo.lock": "rust",
	// TypeScript
	"tsconfig.json": "typescript",
	"tsconfig.base.json": "typescript",
	// JavaScript
	"jsconfig.json": "javascript",
	// Java
	"pom.xml": "java",
	"build.gradle": "java",
	"settings.gradle": "java",
	// Kotlin
	"build.gradle.kts": "kotlin",
	"settings.gradle.kts": "kotlin",
	// Swift
	"Package.swift": "swift",
	// C#
	"*.csproj": "csharp",
	"*.sln": "csharp",
	// Ruby
	Gemfile: "ruby",
	"Gemfile.lock": "ruby",
	// PHP
	"composer.json": "php",
	"composer.lock": "php",
};

/**
 * Source file extensions mapped to languages
 */
const SOURCE_EXTENSIONS: Record<string, Language> = {
	".go": "go",
	".py": "python",
	".pyw": "python",
	".rs": "rust",
	".ts": "typescript",
	".tsx": "typescript",
	".mts": "typescript",
	".cts": "typescript",
	".js": "javascript",
	".jsx": "javascript",
	".mjs": "javascript",
	".cjs": "javascript",
	".java": "java",
	".kt": "kotlin",
	".kts": "kotlin",
	".swift": "swift",
	".cs": "csharp",
	".rb": "ruby",
	".php": "php",
};

/**
 * Directories to exclude from source scanning
 */
const EXCLUDE_DIRS = new Set([
	"node_modules",
	".git",
	".svn",
	"vendor",
	"target",
	"build",
	"dist",
	"out",
	".next",
	".nuxt",
	"__pycache__",
	".pytest_cache",
	".mypy_cache",
	"venv",
	".venv",
	"env",
	".tox",
	"coverage",
	".coverage",
	"htmlcov",
	".gradle",
	".idea",
	".vscode",
	"Pods",
	"DerivedData",
]);

// ============================================================================
// Detection Functions
// ============================================================================

/**
 * Check if a file exists
 */
async function fileExists(filepath: string): Promise<boolean> {
	try {
		return await Bun.file(filepath).exists();
	} catch {
		return false;
	}
}

/**
 * Detect language from config files (fast, high confidence)
 */
async function detectFromConfigs(
	repoPath: string,
): Promise<LanguageSignal[]> {
	const signals: LanguageSignal[] = [];

	for (const [filename, language] of Object.entries(CONFIG_SIGNALS)) {
		// Handle glob patterns for C#
		if (filename.startsWith("*")) {
			const ext = filename.slice(1);
			try {
				const files = fs.readdirSync(repoPath);
				for (const file of files) {
					if (file.endsWith(ext)) {
						signals.push({
							language,
							source: "config",
							path: file,
							weight: 10,
						});
					}
				}
			} catch {
				// Directory read failed, skip
			}
		} else {
			const fullPath = path.join(repoPath, filename);
			if (await fileExists(fullPath)) {
				signals.push({
					language,
					source: "config",
					path: filename,
					weight: 10,
				});
			}
		}
	}

	return signals;
}

/**
 * Count source files by language (thorough, lower weight per file)
 */
async function countSourceFiles(
	repoPath: string,
	maxDepth = 5,
): Promise<{
	counts: Partial<Record<Language, number>>;
	signals: LanguageSignal[];
}> {
	const counts: Partial<Record<Language, number>> = {};
	const signals: LanguageSignal[] = [];

	function scanDir(dir: string, depth: number): void {
		if (depth > maxDepth) return;

		let entries: fs.Dirent[];
		try {
			entries = fs.readdirSync(dir, { withFileTypes: true });
		} catch {
			return;
		}

		for (const entry of entries) {
			if (entry.isDirectory()) {
				if (!EXCLUDE_DIRS.has(entry.name)) {
					scanDir(path.join(dir, entry.name), depth + 1);
				}
			} else if (entry.isFile()) {
				const ext = path.extname(entry.name).toLowerCase();
				const language = SOURCE_EXTENSIONS[ext];
				if (language) {
					counts[language] = (counts[language] || 0) + 1;
				}
			}
		}
	}

	scanDir(repoPath, 0);

	// Add signals based on file counts (weight based on count)
	for (const [lang, count] of Object.entries(counts)) {
		if (count > 0) {
			// Weight: 1 per 20 files, max 5
			const weight = Math.min(5, Math.ceil(count / 20));
			signals.push({
				language: lang as Language,
				source: "source",
				path: `${count} source files`,
				weight,
			});
		}
	}

	return { counts, signals };
}

/**
 * Detect language from CI configuration
 */
async function detectFromCI(repoPath: string): Promise<LanguageSignal[]> {
	const signals: LanguageSignal[] = [];

	// Check GitHub Actions
	const workflowsDir = path.join(repoPath, ".github", "workflows");
	try {
		const files = fs.readdirSync(workflowsDir);
		for (const file of files) {
			if (file.endsWith(".yml") || file.endsWith(".yaml")) {
				const content = await Bun.file(
					path.join(workflowsDir, file),
				).text();
				const contentLower = content.toLowerCase();

				// Check for language-specific actions/commands
				if (
					contentLower.includes("setup-go") ||
					contentLower.includes("go build") ||
					contentLower.includes("go test")
				) {
					signals.push({
						language: "go",
						source: "ci",
						path: `.github/workflows/${file}`,
						weight: 5,
					});
				}
				if (
					contentLower.includes("setup-python") ||
					contentLower.includes("pip install") ||
					contentLower.includes("pytest")
				) {
					signals.push({
						language: "python",
						source: "ci",
						path: `.github/workflows/${file}`,
						weight: 5,
					});
				}
				if (
					contentLower.includes("cargo build") ||
					contentLower.includes("cargo test") ||
					contentLower.includes("dtolnay/rust-toolchain")
				) {
					signals.push({
						language: "rust",
						source: "ci",
						path: `.github/workflows/${file}`,
						weight: 5,
					});
				}
				if (
					contentLower.includes("setup-node") ||
					contentLower.includes("bun ") ||
					contentLower.includes("npm ") ||
					contentLower.includes("pnpm ") ||
					contentLower.includes("yarn ")
				) {
					// Could be either TS or JS, check for tsconfig
					const hasTsConfig = await fileExists(
						path.join(repoPath, "tsconfig.json"),
					);
					signals.push({
						language: hasTsConfig ? "typescript" : "javascript",
						source: "ci",
						path: `.github/workflows/${file}`,
						weight: 3,
					});
				}
				if (
					contentLower.includes("setup-java") ||
					contentLower.includes("maven") ||
					contentLower.includes("gradle")
				) {
					signals.push({
						language: "java",
						source: "ci",
						path: `.github/workflows/${file}`,
						weight: 5,
					});
				}
			}
		}
	} catch {
		// No workflows directory
	}

	return signals;
}

/**
 * Calculate aggregate scores per language
 */
function aggregateSignals(
	signals: LanguageSignal[],
): Map<Language, number> {
	const scores = new Map<Language, number>();

	for (const signal of signals) {
		const current = scores.get(signal.language) || 0;
		scores.set(signal.language, current + signal.weight);
	}

	return scores;
}

/**
 * Full language detection with all signals
 *
 * @param repoPath - Repository path (defaults to cwd)
 * @returns Complete language detection result
 */
export async function detectLanguage(
	repoPath?: string,
): Promise<LanguageDetection> {
	const root = repoPath || process.cwd();

	// Collect all signals
	const configSignals = await detectFromConfigs(root);
	const { counts, signals: sourceSignals } = await countSourceFiles(root);
	const ciSignals = await detectFromCI(root);

	const allSignals = [...configSignals, ...sourceSignals, ...ciSignals];

	// Aggregate scores
	const scores = aggregateSignals(allSignals);

	// Sort languages by score
	const sortedLanguages = [...scores.entries()]
		.sort((a, b) => b[1] - a[1])
		.map(([lang]) => lang);

	const primary = sortedLanguages[0] || "unknown";
	const secondary = sortedLanguages.slice(1).filter((lang) => {
		// Only include if score is at least 30% of primary
		const primaryScore = scores.get(primary) || 0;
		const langScore = scores.get(lang) || 0;
		return langScore >= primaryScore * 0.3;
	});

	// Calculate confidence
	const primaryScore = scores.get(primary) || 0;
	const totalScore = [...scores.values()].reduce((a, b) => a + b, 0);
	const confidence =
		totalScore > 0 ? Math.round((primaryScore / totalScore) * 100) : 0;

	return {
		primary,
		secondary,
		confidence,
		signals: allSignals,
		sourceFileCount: counts,
	};
}

/**
 * Quick language detection from config files only (faster)
 *
 * @param repoPath - Repository path (defaults to cwd)
 * @returns Primary detected language
 */
export async function detectLanguageQuick(
	repoPath?: string,
): Promise<Language> {
	const root = repoPath || process.cwd();
	const signals = await detectFromConfigs(root);

	if (signals.length === 0) {
		return "unknown";
	}

	// Return the language with most config file matches
	const scores = aggregateSignals(signals);
	const sorted = [...scores.entries()].sort((a, b) => b[1] - a[1]);

	return sorted[0]?.[0] || "unknown";
}

/**
 * Check if a repository is polyglot (multiple languages)
 *
 * @param detection - Language detection result
 * @returns True if repository has multiple significant languages
 */
export function isPolyglot(detection: LanguageDetection): boolean {
	return detection.secondary.length > 0;
}

/**
 * Get human-readable language name
 */
export function getLanguageName(language: Language): string {
	const names: Record<Language, string> = {
		typescript: "TypeScript",
		javascript: "JavaScript",
		go: "Go",
		python: "Python",
		rust: "Rust",
		java: "Java",
		kotlin: "Kotlin",
		swift: "Swift",
		csharp: "C#",
		ruby: "Ruby",
		php: "PHP",
		unknown: "Unknown",
	};
	return names[language];
}
