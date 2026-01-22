#!/usr/bin/env bun
/**
 * Agent Readiness Check - Factory.ai-Aligned Codebase Assessment
 *
 * SPDX-License-Identifier: Apache-2.0
 * SPDX-FileCopyrightText: 2025-2026 Marcus Neves
 *
 * @description
 * Evaluates codebases for AI agent readiness across 9 technical pillars
 * and 5 maturity levels. Supports multiple languages and monorepos.
 *
 * Features:
 * - Multi-language support (Go, Python, Rust, TypeScript, JavaScript, Java)
 * - Monorepo application discovery
 * - Pluggable check registry
 * - Multiple scoring modes (weighted, strict, average)
 *
 * @usage
 *   bun run tools/readiness-check.ts [options]
 *
 * @options
 *   --format=md|json|html  Output format (default: md)
 *   --output=<file>        Write to file instead of stdout
 *   --scoring=weighted|strict|average  Scoring mode (default: weighted)
 *   --language=<lang>      Force language detection (override)
 *   --app=<path>           Assess single application in monorepo
 *   --skip-tests           Skip test execution checks
 *   --skip-build           Skip build verification
 *   --verbose              Show all checks, not just failures
 *   --min-level=<1-5>      Exit with error if below this level (for CI)
 *   --notes                Generate session notes file
 *   --help                 Show this help
 */

import fs from "node:fs";
import path from "node:path";
import process from "node:process";

import { createFileCache, type FileCache } from "./lib/file-cache.js";

import {
	EXIT_CODES,
	generateHelp,
	getOption,
	getOptionInt,
	hasFlag,
	hasHelpFlag,
	parseArgs,
} from "./lib/index.js";

// Import v2 modules
import {
	type Language,
	detectLanguage,
	detectLanguageQuick,
} from "./lib/language-detection.js";
import { type DetectedApp, type DiscoveryResult, discoverApps } from "./lib/app-discovery.js";
import {
	type Pillar,
	type Level,
	type CheckResultWithMeta,
	type CheckContext,
	type CheckOptions,
	checkRegistry,
	PILLAR_NAMES,
	LEVEL_NAMES,
} from "./lib/check-registry.js";
import {
	type ScoringMode,
	type ScoringConfig,
	type AppScore,
	type OrgScore,
	calculateAppScore,
	aggregateOrgScore,
	formatAppSummary,
	formatOrgSummary,
	getTopRecommendations,
	DEFAULT_PILLAR_WEIGHTS,
} from "./lib/scoring.js";
import {
	getAdapter,
	getAllAdapters,
	getSupportedLanguages,
	typescriptAdapter,
	javascriptAdapter,
	goAdapter,
	pythonAdapter,
	rustAdapter,
	javaAdapter,
} from "./lib/adapters/index.js";

// Register standard check definitions - must import before main()
import "./lib/checks/index.js";

// ============================================================================
// Types
// ============================================================================

interface ReadinessReport {
	version: string;
	repoName: string;
	date: string;
	timestamp: string;
	structure: "monorepo" | "single" | "polyglot";
	language: Language;
	scoringMode: ScoringMode;
	maturityLevel: Level;
	overallScore: number;
	apps: AppScore[];
	pillars: Array<{
		pillar: Pillar;
		displayName: string;
		score: number;
		level: Level;
		passed: number;
		total: number;
		/** Individual check results for this pillar */
		checks: CheckResultWithMeta[];
	}>;
	blockingGaps: CheckResultWithMeta[];
	warnings: CheckResultWithMeta[];
	passingChecks: CheckResultWithMeta[];
	recommendations: Array<{
		pillar: Pillar;
		check: { id: string; name: string };
		impact: "high" | "medium" | "low";
		reason: string;
	}>;
}

interface SessionNote {
	timestamp: string;
	repoName: string;
	language: Language;
	structure: string;
	scoringMode: ScoringMode;
	maturityLevel: Level;
	overallScore: number;
	duration: number;
	checksRun: number;
	checksPassed: number;
	blockingGaps: string[];
	observations: string[];
	missingContext: string[];
}

// ============================================================================
// Configuration
// ============================================================================

/**
 * Reads version from VERSION file in project root.
 * Falls back to "0.0.0" if file is not found.
 */
function getVersion(): string {
	const versionPath = path.join(__dirname, "..", "VERSION");
	try {
		return fs.readFileSync(versionPath, "utf-8").trim();
	} catch {
		return "0.0.0";
	}
}

const VERSION = getVersion();

// ============================================================================
// Initialization
// ============================================================================

function initializeAdapters(): void {
	// Register all language adapters
	checkRegistry.registerAdapter(typescriptAdapter);
	checkRegistry.registerAdapter(javascriptAdapter);
	checkRegistry.registerAdapter(goAdapter);
	checkRegistry.registerAdapter(pythonAdapter);
	checkRegistry.registerAdapter(rustAdapter);
	checkRegistry.registerAdapter(javaAdapter);
}

// ============================================================================
// Utility Functions
// ============================================================================

function getRepoName(): string {
	return path.basename(process.cwd());
}

// ============================================================================
// Check Execution
// ============================================================================

async function runChecksForApp(
	app: DetectedApp,
	repoRoot: string,
	options: CheckOptions,
	cache: FileCache,
	log: (...args: unknown[]) => void,
): Promise<CheckResultWithMeta[]> {
	const ctx: CheckContext = {
		app,
		repoRoot,
		options,
		cache,
	};

	const adapter = getAdapter(app.language);
	if (!adapter) {
		log(`  Warning: No adapter for ${app.language}, using fallback checks`);
	}

	const results = await checkRegistry.runAllChecks(ctx);
	return results;
}

// ============================================================================
// Session Notes
// ============================================================================

function generateSessionNotes(
	report: ReadinessReport,
	durationMs: number,
): SessionNote {
	const observations: string[] = [];
	const missingContext: string[] = [];

	// Analyze strong pillars
	const strongPillars = report.pillars.filter((p) => p.score >= 80);
	for (const p of strongPillars) {
		observations.push(`${p.displayName} is well-configured (${p.score}%)`);
	}

	// Identify weak pillars
	const weakPillars = report.pillars.filter((p) => p.score < 50);
	for (const p of weakPillars) {
		missingContext.push(`${p.displayName}: Score below 50% (${p.score}%)`);
	}

	// Add structure observations
	if (report.structure === "monorepo") {
		observations.push(`Monorepo with ${report.apps.length} applications`);
	}

	// Add level observations
	if (report.maturityLevel === 1) {
		observations.push("Project is at base level - foundational infrastructure needed");
	} else if (report.maturityLevel >= 4) {
		observations.push("Project has mature infrastructure - focus on optimization");
	}

	return {
		timestamp: new Date().toISOString(),
		repoName: report.repoName,
		language: report.language,
		structure: report.structure,
		scoringMode: report.scoringMode,
		maturityLevel: report.maturityLevel,
		overallScore: report.overallScore,
		duration: Math.round(durationMs / 1000),
		checksRun: report.pillars.reduce((sum, p) => sum + p.total, 0),
		checksPassed: report.pillars.reduce((sum, p) => sum + p.passed, 0),
		blockingGaps: report.blockingGaps.map((g) => `${g.check.pillar}/${g.check.name}`),
		observations,
		missingContext,
	};
}

async function writeSessionNotes(note: SessionNote, outputDir: string): Promise<string> {
	const notesDir = path.join(outputDir, ".readiness-notes");
	if (!fs.existsSync(notesDir)) {
		fs.mkdirSync(notesDir, { recursive: true });
	}

	const filename = `${note.timestamp.split("T")[0]}-${note.repoName}.json`;
	const filepath = path.join(notesDir, filename);

	let existingNotes: SessionNote[] = [];
	if (fs.existsSync(filepath)) {
		try {
			existingNotes = JSON.parse(fs.readFileSync(filepath, "utf-8"));
		} catch {
			existingNotes = [];
		}
	}

	existingNotes.push(note);
	await Bun.write(filepath, JSON.stringify(existingNotes, null, 2));

	return filepath;
}

// ============================================================================
// Chart Generation
// ============================================================================

function generateRadarChart(pillars: ReadinessReport["pillars"]): string {
	const size = 300;
	const center = size / 2;
	const maxRadius = size / 2 - 40;
	const numPillars = pillars.length;
	const angleStep = (2 * Math.PI) / numPillars;

	let axes = "";
	let labels = "";
	let gridLines = "";

	// Concentric circles
	for (let ring = 1; ring <= 5; ring++) {
		const radius = (maxRadius * ring) / 5;
		gridLines += `<circle cx="${center}" cy="${center}" r="${radius}" fill="none" stroke="#404040" stroke-width="0.5" stroke-dasharray="${ring === 5 ? "0" : "2,2"}"/>`;
	}

	// Axes and points
	const points: { x: number; y: number }[] = [];
	for (let i = 0; i < numPillars; i++) {
		const pillar = pillars[i];
		if (!pillar) continue;

		const angle = i * angleStep - Math.PI / 2;
		const x2 = center + maxRadius * Math.cos(angle);
		const y2 = center + maxRadius * Math.sin(angle);

		axes += `<line x1="${center}" y1="${center}" x2="${x2}" y2="${y2}" stroke="#404040" stroke-width="0.5"/>`;

		const score = pillar.score / 100;
		const pointRadius = maxRadius * score;
		const px = center + pointRadius * Math.cos(angle);
		const py = center + pointRadius * Math.sin(angle);
		points.push({ x: px, y: py });

		const labelRadius = maxRadius + 25;
		const lx = center + labelRadius * Math.cos(angle);
		const ly = center + labelRadius * Math.sin(angle);
		const shortName = pillar.displayName.split(" ")[0] ?? pillar.displayName;
		labels += `<text x="${lx}" y="${ly}" text-anchor="middle" dominant-baseline="middle" fill="#a3a3a3" font-size="10">${shortName}</text>`;
	}

	const polygonPoints = points.map((p) => `${p.x},${p.y}`).join(" ");
	const polygon = `<polygon points="${polygonPoints}" fill="rgba(249, 115, 22, 0.3)" stroke="#f97316" stroke-width="2"/>`;

	let dots = "";
	for (const point of points) {
		dots += `<circle cx="${point.x}" cy="${point.y}" r="4" fill="#f97316"/>`;
	}

	return `
    <svg viewBox="0 0 ${size} ${size}" class="radar-chart">
      ${gridLines}
      ${axes}
      ${polygon}
      ${dots}
      ${labels}
    </svg>
  `;
}

// ============================================================================
// Output Rendering
// ============================================================================

function renderMarkdown(report: ReadinessReport): string {
	const lines: string[] = [];

	lines.push("# Agent Readiness Report v2.0");
	lines.push("");
	lines.push(`**Repository:** ${report.repoName}`);
	lines.push(`**Assessed:** ${report.date}`);
	lines.push(`**Language:** ${report.language}`);
	lines.push(`**Structure:** ${report.structure}${report.apps.length > 1 ? ` (${report.apps.length} apps)` : ""}`);
	lines.push(`**Scoring Mode:** ${report.scoringMode}`);
	lines.push(`**Maturity Level:** ${report.maturityLevel} (${LEVEL_NAMES[report.maturityLevel]})`);
	lines.push(`**Overall Score:** ${report.overallScore}%`);
	lines.push("");

	// Apps summary (if monorepo)
	if (report.apps.length > 1) {
		lines.push("## Applications");
		lines.push("");
		for (const app of report.apps) {
			lines.push(`- **${app.app.name}** (${app.app.language}): L${app.level} - ${app.score}%`);
		}
		lines.push("");
	}

	lines.push("## Pillar Scores");
	lines.push("");
	lines.push("| Pillar | Score | Level | Status |");
	lines.push("|--------|-------|-------|--------|");

	for (const pillar of report.pillars) {
		const status = pillar.level >= 3 ? "Pass" : pillar.level === 2 ? "Warning" : "Blocking";
		const emoji = pillar.level >= 3 ? "" : pillar.level === 2 ? " (warning)" : " (blocking)";
		lines.push(`| ${pillar.displayName} | ${pillar.score}% | L${pillar.level} | ${status}${emoji} |`);
	}

	if (report.recommendations.length > 0) {
		lines.push("");
		lines.push("## Top Recommendations");
		lines.push("");
		for (const rec of report.recommendations) {
			lines.push(`- **[${rec.impact.toUpperCase()}]** ${rec.check.name} (${PILLAR_NAMES[rec.pillar]})`);
		}
	}

	if (report.blockingGaps.length > 0) {
		lines.push("");
		lines.push("## Blocking Gaps (Must Fix)");
		lines.push("");
		for (const gap of report.blockingGaps) {
			const details = gap.details ? ` - ${gap.details}` : "";
			lines.push(`- **${PILLAR_NAMES[gap.check.pillar]}**: ${gap.check.name}${details}`);
		}
	}

	if (report.warnings.length > 0) {
		lines.push("");
		lines.push("## Warnings");
		lines.push("");
		for (const warning of report.warnings) {
			const details = warning.details ? ` - ${warning.details}` : "";
			lines.push(`- ${PILLAR_NAMES[warning.check.pillar]}: ${warning.check.name}${details}`);
		}
	}

	lines.push("");
	lines.push("## What's Working Well");
	lines.push("");
	const topPassing = report.passingChecks.slice(0, 8);
	for (const check of topPassing) {
		lines.push(`- ${check.check.name}`);
	}

	lines.push("");
	lines.push("---");
	lines.push(`*Generated by Agent Readiness Check v${VERSION} · https://github.com/mneves75/skills · 9 Pillars · 5 Levels*`);

	return lines.join("\n");
}

function renderJson(report: ReadinessReport): string {
	return JSON.stringify(report, null, 2);
}

function renderHtml(report: ReadinessReport): string {
	const getScoreColor = (score: number): string => {
		if (score >= 80) return "green";
		if (score >= 60) return "yellow";
		return "red";
	};

	const getLevelColor = (level: Level): string => {
		if (level === 1) return "#ef4444";
		if (level === 2) return "#f97316";
		if (level === 3) return "#eab308";
		if (level === 4) return "#22c55e";
		return "#3b82f6";
	};

	const radarChart = generateRadarChart(report.pillars);

	// Calculate level percentages for each level (Factory.ai style)
	const levelPercentages: number[] = [];
	for (let l = 1; l <= 5; l++) {
		if (l < report.maturityLevel) {
			levelPercentages.push(100);
		} else if (l === report.maturityLevel) {
			// Current level progress based on score within level thresholds
			const thresholds = [0, 35, 50, 65, 80, 100];
			const lowerBound = thresholds[l - 1] ?? 0;
			const upperBound = thresholds[l] ?? 100;
			const progress = Math.min(100, Math.max(0,
				((report.overallScore - lowerBound) / (upperBound - lowerBound)) * 100
			));
			levelPercentages.push(Math.round(progress));
		} else {
			levelPercentages.push(0);
		}
	}

	// Find strongest pillars (top 3 by score)
	const sortedPillars = [...report.pillars].sort((a, b) => b.score - a.score);
	const strongestPillar = sortedPillars[0];
	const topPillars = sortedPillars.slice(0, 3).filter(p => p.score >= 50);

	// Generate executive summary headline
	const getStrengthHeadline = (): string => {
		if (!strongestPillar || strongestPillar.score < 50) {
			return "Building Foundation";
		}
		const strengthMap: Record<string, string> = {
			"Style & Validation": "Strong Code Quality",
			"Build System": "Robust Build Pipeline",
			"Testing": "Comprehensive Test Coverage",
			"Documentation": "Well-Documented Codebase",
			"Development Environment": "Developer-Friendly Setup",
			"Debugging & Observability": "Observable & Debuggable",
			"Security": "Security-Conscious",
			"Task Discovery": "Clear Task Discovery",
			"Product & Experimentation": "Product-Ready",
		};
		return strengthMap[strongestPillar.displayName] ?? `Strong ${strongestPillar.displayName}`;
	};

	// Generate opportunities (top 3 failing areas)
	const weakPillars = [...report.pillars]
		.filter(p => p.score < 80)
		.sort((a, b) => a.score - b.score)
		.slice(0, 3);

	const opportunitiesHtml = weakPillars.length > 0 ? `
	<div class="opportunities-grid">
		${weakPillars.map((p, i) => {
			const num = String(i + 1).padStart(2, "0");
			const description = getOpportunityDescription(p.displayName, p.score);
			return `
			<div class="opportunity-item">
				<span class="opportunity-num">${num}</span>
				<div class="opportunity-content">
					<h4>${p.displayName}</h4>
					<p>${description}</p>
				</div>
			</div>`;
		}).join("")}
	</div>` : "";

	// Helper function for opportunity descriptions
	function getOpportunityDescription(pillarName: string, score: number): string {
		const level = score < 35 ? "foundational" : score < 50 ? "basic" : score < 65 ? "standardized" : "optimized";
		const descriptions: Record<string, string> = {
			"Style & Validation": `Add linter configuration and consistent code formatting to reach ${level} quality standards.`,
			"Build System": `Configure build automation and dependency management for ${level} reproducibility.`,
			"Testing": `Implement unit and integration tests to achieve ${level} test coverage.`,
			"Documentation": `Add README, architecture docs, and CLAUDE.md for ${level} agent understanding.`,
			"Development Environment": `Configure devcontainer, setup scripts, and env templates for ${level} onboarding.`,
			"Debugging & Observability": `Add structured logging, error tracking, and health checks for ${level} observability.`,
			"Security": `Implement security scanning, CODEOWNERS, and audit practices for ${level} security posture.`,
			"Task Discovery": `Add Makefile, PR templates, and task documentation for ${level} task discovery.`,
			"Product & Experimentation": `Configure feature flags and CI test execution for ${level} experimentation.`,
		};
		return descriptions[pillarName] ?? `Improve ${pillarName} to reach ${level} level.`;
	}

	// Generate pillar cards with detailed criteria
	const pillarsHtml = report.pillars.map((p) => {
		const checksHtml = p.checks
			.filter(c => !c.skipped)
			.map(c => {
				const icon = c.pass ? "check" : "x";
				const iconColor = c.pass ? "var(--green)" : "var(--red)";
				const iconSvg = c.pass
					? `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="${iconColor}" stroke-width="3"><polyline points="20 6 9 17 4 12"/></svg>`
					: `<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="${iconColor}" stroke-width="3"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`;
				const details = c.details ? `<span class="check-details">${escapeHtml(c.details)}</span>` : "";
				return `
				<div class="check-row ${c.pass ? "pass" : "fail"}">
					<span class="check-icon">${iconSvg}</span>
					<span class="check-name">${escapeHtml(c.check.name)}</span>
					${details}
				</div>`;
			}).join("");

		return `
		<div class="pillar-card" data-pillar="${p.pillar}">
			<div class="pillar-header">
				<h3>${p.displayName}</h3>
				<span class="pillar-level" style="background: ${getLevelColor(p.level)}20; color: ${getLevelColor(p.level)};">L${p.level}</span>
			</div>
			<div class="pillar-stats">
				<span class="pillar-score">${p.score}%</span>
				<span class="pillar-count">${p.passed}/${p.total}</span>
			</div>
			<div class="progress-bar">
				<div class="progress-fill ${getScoreColor(p.score)}" style="width: ${p.score}%"></div>
			</div>
			<details class="checks-details">
				<summary>View ${p.total} criteria</summary>
				<div class="checks-list">
					${checksHtml}
				</div>
			</details>
		</div>`;
	}).join("");

	// Generate blocking gaps section (at bottom)
	const blockingHtml = report.blockingGaps.length > 0 ? `
	<section class="blocking-section">
		<h2>Blocking Gaps (${report.blockingGaps.length})</h2>
		<p class="blocking-subtitle">These items must be addressed to advance to the next maturity level</p>
		<div class="blocking-grid">
			${report.blockingGaps.map((g) => `
			<div class="blocking-item">
				<span class="blocking-pillar">${PILLAR_NAMES[g.check.pillar]}</span>
				<span class="blocking-name">${escapeHtml(g.check.name)}</span>
				${g.details ? `<span class="blocking-details">${escapeHtml(g.details)}</span>` : ""}
			</div>`).join("")}
		</div>
	</section>` : "";

	// Generate apps section for monorepos
	const appsHtml = report.apps.length > 1 ? `
	<section class="apps-section">
		<h2>Applications (${report.apps.length})</h2>
		<div class="apps-grid">
			${report.apps.map((app) => `
			<div class="app-card">
				<div class="app-name">${escapeHtml(app.app.name)}</div>
				<div class="app-lang">${app.app.language}</div>
				<div class="app-score" style="color: ${getLevelColor(app.level)}">L${app.level} · ${app.score}%</div>
			</div>`).join("")}
		</div>
	</section>` : "";

	// Generate level progress bars (Factory.ai style)
	const levelBarsHtml = `
	<div class="level-bars">
		${[1, 2, 3, 4, 5].map(l => {
			const pct = levelPercentages[l - 1] ?? 0;
			const isActive = l <= report.maturityLevel;
			const isCurrent = l === report.maturityLevel;
			return `
			<div class="level-bar-item ${isActive ? "active" : ""} ${isCurrent ? "current" : ""}">
				<div class="level-bar-header">
					<span class="level-bar-label">L${l}</span>
					<span class="level-bar-name">${LEVEL_NAMES[l as Level]}</span>
					<span class="level-bar-pct">${pct}%</span>
				</div>
				<div class="level-bar-track">
					<div class="level-bar-fill" style="width: ${pct}%; background: ${isActive ? "var(--green)" : "var(--bg-tertiary)"}"></div>
				</div>
			</div>`;
		}).join("")}
	</div>`;

	const totalChecks = report.pillars.reduce((sum, p) => sum + p.total, 0);
	const passingChecks = report.pillars.reduce((sum, p) => sum + p.passed, 0);

	return `<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Agent Readiness Report | ${escapeHtml(report.repoName)}</title>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg-primary: #09090b;
      --bg-secondary: #0f0f12;
      --bg-tertiary: #18181b;
      --bg-card: #121215;
      --text-primary: #fafafa;
      --text-secondary: #a1a1aa;
      --text-muted: #71717a;
      --border-color: #27272a;
      --border-subtle: #1f1f23;
      --green: #22c55e;
      --green-dim: #16a34a;
      --yellow: #eab308;
      --red: #ef4444;
      --blue: #3b82f6;
      --orange: #f97316;
    }

    * { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      background: var(--bg-primary);
      color: var(--text-primary);
      line-height: 1.6;
      min-height: 100vh;
      -webkit-font-smoothing: antialiased;
    }

    .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }

    /* Header */
    header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      padding: 1.5rem 0 2rem;
      border-bottom: 1px solid var(--border-color);
      margin-bottom: 2rem;
    }

    .header-left h1 {
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: var(--text-muted);
      font-weight: 500;
      margin-bottom: 0.5rem;
    }

    .header-left .repo-name {
      font-size: 1.75rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }

    .header-left .meta {
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-top: 0.5rem;
    }

    .header-right { text-align: right; }

    .header-right .level-display {
      font-size: 3rem;
      font-weight: 700;
      line-height: 1;
      letter-spacing: -0.02em;
    }

    .header-right .level-name {
      font-size: 0.75rem;
      color: var(--text-secondary);
      text-transform: uppercase;
      letter-spacing: 0.08em;
      margin-top: 0.25rem;
    }

    /* Summary Row */
    .summary-row {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 1rem;
      margin-bottom: 2rem;
    }

    .summary-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 1.25rem;
    }

    .summary-card .label {
      font-size: 0.65rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--text-muted);
      margin-bottom: 0.75rem;
    }

    .summary-card .value {
      font-size: 1.75rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }

    .summary-card .value.green { color: var(--green); }
    .summary-card .value.yellow { color: var(--yellow); }
    .summary-card .value.red { color: var(--red); }

    .summary-card .subtext {
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-top: 0.25rem;
    }

    /* Executive Summary */
    .executive-summary {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 1.5rem;
      margin-bottom: 2rem;
    }

    .executive-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 1.5rem;
    }

    .executive-card h2 {
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--text-muted);
      margin-bottom: 1rem;
    }

    .strength-headline {
      font-size: 1.5rem;
      font-weight: 700;
      color: var(--green);
      margin-bottom: 0.75rem;
      letter-spacing: -0.01em;
    }

    .strength-description {
      font-size: 0.85rem;
      color: var(--text-secondary);
      line-height: 1.6;
    }

    .strength-pills {
      display: flex;
      gap: 0.5rem;
      margin-top: 1rem;
      flex-wrap: wrap;
    }

    .strength-pill {
      background: rgba(34, 197, 94, 0.1);
      border: 1px solid rgba(34, 197, 94, 0.2);
      color: var(--green);
      padding: 0.25rem 0.75rem;
      border-radius: 999px;
      font-size: 0.7rem;
      font-weight: 500;
    }

    .opportunities-grid {
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }

    .opportunity-item {
      display: flex;
      gap: 1rem;
      align-items: flex-start;
    }

    .opportunity-num {
      font-size: 1.25rem;
      font-weight: 700;
      color: var(--orange);
      min-width: 2rem;
    }

    .opportunity-content h4 {
      font-size: 0.9rem;
      font-weight: 600;
      margin-bottom: 0.25rem;
    }

    .opportunity-content p {
      font-size: 0.8rem;
      color: var(--text-muted);
      line-height: 1.5;
    }

    /* Level Progress Bars */
    .level-section {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 1.5rem;
      margin-bottom: 2rem;
    }

    .level-section h2 {
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--text-muted);
      margin-bottom: 1.25rem;
    }

    .level-bars {
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    }

    .level-bar-item {
      opacity: 0.5;
    }

    .level-bar-item.active {
      opacity: 1;
    }

    .level-bar-item.current {
      opacity: 1;
    }

    .level-bar-header {
      display: flex;
      align-items: baseline;
      gap: 0.5rem;
      margin-bottom: 0.35rem;
    }

    .level-bar-label {
      font-size: 0.75rem;
      font-weight: 600;
      min-width: 1.75rem;
    }

    .level-bar-name {
      font-size: 0.75rem;
      color: var(--text-muted);
      flex: 1;
    }

    .level-bar-pct {
      font-size: 0.75rem;
      font-weight: 600;
      color: var(--text-secondary);
    }

    .level-bar-track {
      height: 6px;
      background: var(--bg-tertiary);
      border-radius: 3px;
      overflow: hidden;
    }

    .level-bar-fill {
      height: 100%;
      border-radius: 3px;
      transition: width 0.3s ease;
    }

    /* Chart Section */
    .chart-section {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 1.5rem;
      margin-bottom: 2rem;
    }

    .chart-section h2 {
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--text-muted);
      margin-bottom: 1.25rem;
    }

    .radar-chart {
      width: 100%;
      max-width: 300px;
      margin: 0 auto;
      display: block;
    }

    /* Pillars Grid */
    .pillars-section h2 {
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--text-muted);
      margin-bottom: 1rem;
    }

    .pillars-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 1rem;
      margin-bottom: 2rem;
    }

    .pillar-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 1.25rem;
    }

    .pillar-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 0.75rem;
    }

    .pillar-header h3 {
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--text-primary);
    }

    .pillar-level {
      padding: 0.2rem 0.6rem;
      border-radius: 4px;
      font-size: 0.65rem;
      font-weight: 600;
    }

    .pillar-stats {
      display: flex;
      justify-content: space-between;
      align-items: baseline;
      margin-bottom: 0.5rem;
    }

    .pillar-score {
      font-size: 1.5rem;
      font-weight: 700;
      letter-spacing: -0.02em;
    }

    .pillar-count {
      font-size: 0.75rem;
      color: var(--text-muted);
    }

    .progress-bar {
      height: 4px;
      background: var(--bg-tertiary);
      border-radius: 2px;
      overflow: hidden;
      margin-bottom: 1rem;
    }

    .progress-fill {
      height: 100%;
      border-radius: 2px;
      transition: width 0.3s ease;
    }

    .progress-fill.green { background: var(--green); }
    .progress-fill.yellow { background: var(--yellow); }
    .progress-fill.red { background: var(--red); }

    /* Checks Details (Collapsible) */
    .checks-details {
      border-top: 1px solid var(--border-subtle);
      padding-top: 0.75rem;
    }

    .checks-details summary {
      font-size: 0.75rem;
      color: var(--text-muted);
      cursor: pointer;
      user-select: none;
      padding: 0.25rem 0;
    }

    .checks-details summary:hover {
      color: var(--text-secondary);
    }

    .checks-details[open] summary {
      margin-bottom: 0.75rem;
    }

    .checks-list {
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
      max-height: 300px;
      overflow-y: auto;
    }

    .check-row {
      display: grid;
      grid-template-columns: 18px 1fr;
      gap: 0.5rem;
      align-items: start;
      font-size: 0.75rem;
      padding: 0.35rem 0;
      border-bottom: 1px solid var(--border-subtle);
    }

    .check-row:last-child {
      border-bottom: none;
    }

    .check-icon {
      display: flex;
      align-items: center;
      justify-content: center;
      padding-top: 2px;
    }

    .check-name {
      color: var(--text-secondary);
    }

    .check-row.pass .check-name {
      color: var(--text-primary);
    }

    .check-details {
      display: block;
      grid-column: 2;
      font-size: 0.7rem;
      color: var(--text-muted);
      margin-top: 0.125rem;
    }

    /* Apps Section */
    .apps-section {
      margin-bottom: 2rem;
    }

    .apps-section h2 {
      font-size: 0.7rem;
      text-transform: uppercase;
      letter-spacing: 0.1em;
      color: var(--text-muted);
      margin-bottom: 1rem;
    }

    .apps-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 1rem;
    }

    .app-card {
      background: var(--bg-card);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 1rem;
    }

    .app-name {
      font-weight: 600;
      font-size: 0.85rem;
      margin-bottom: 0.25rem;
    }

    .app-lang {
      font-size: 0.7rem;
      color: var(--text-muted);
    }

    .app-score {
      font-size: 0.9rem;
      font-weight: 600;
      margin-top: 0.5rem;
    }

    /* Blocking Gaps Section */
    .blocking-section {
      background: rgba(239, 68, 68, 0.03);
      border: 1px solid rgba(239, 68, 68, 0.15);
      border-radius: 8px;
      padding: 1.5rem;
      margin-bottom: 2rem;
    }

    .blocking-section h2 {
      font-size: 0.8rem;
      font-weight: 600;
      color: var(--red);
      margin-bottom: 0.5rem;
    }

    .blocking-subtitle {
      font-size: 0.75rem;
      color: var(--text-muted);
      margin-bottom: 1.25rem;
    }

    .blocking-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 0.75rem;
    }

    .blocking-item {
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
      padding: 0.75rem;
      background: rgba(239, 68, 68, 0.05);
      border-radius: 6px;
    }

    .blocking-pillar {
      font-size: 0.6rem;
      text-transform: uppercase;
      letter-spacing: 0.08em;
      color: var(--red);
      font-weight: 600;
    }

    .blocking-name {
      font-size: 0.8rem;
      color: var(--text-primary);
    }

    .blocking-details {
      font-size: 0.7rem;
      color: var(--text-muted);
    }

    /* Footer */
    footer {
      border-top: 1px solid var(--border-color);
      padding: 1.5rem 0 0;
      text-align: center;
      color: var(--text-muted);
      font-size: 0.7rem;
      letter-spacing: 0.05em;
    }

    /* Responsive */
    @media (max-width: 1024px) {
      .summary-row { grid-template-columns: repeat(2, 1fr); }
      .executive-summary { grid-template-columns: 1fr; }
    }

    @media (max-width: 640px) {
      .summary-row { grid-template-columns: 1fr; }
      .container { padding: 1rem; }
      header { flex-direction: column; gap: 1rem; }
      .header-right { text-align: left; }
    }
  </style>
</head>
<body>
  <div class="container">
    <header>
      <div class="header-left">
        <h1>Agent Readiness Report v${VERSION}</h1>
        <p class="repo-name">${escapeHtml(report.repoName)}</p>
        <p class="meta">${report.language} · ${report.structure}${report.apps.length > 1 ? ` (${report.apps.length} apps)` : ""} · ${report.scoringMode} scoring · ${report.date}</p>
      </div>
      <div class="header-right">
        <div class="level-display" style="color: ${getLevelColor(report.maturityLevel)}">L${report.maturityLevel}</div>
        <p class="level-name">${LEVEL_NAMES[report.maturityLevel]}</p>
      </div>
    </header>

    <section class="summary-row">
      <div class="summary-card">
        <p class="label">Maturity Level</p>
        <p class="value">Level ${report.maturityLevel}</p>
        <p class="subtext">${LEVEL_NAMES[report.maturityLevel]}</p>
      </div>
      <div class="summary-card">
        <p class="label">Overall Score</p>
        <p class="value ${getScoreColor(report.overallScore)}">${report.overallScore}%</p>
        <p class="subtext">${passingChecks}/${totalChecks} criteria</p>
      </div>
      <div class="summary-card">
        <p class="label">Strongest Pillar</p>
        <p class="value" style="font-size: 1.25rem;">${strongestPillar?.displayName.split(" ")[0] ?? "N/A"}</p>
        <p class="subtext">${strongestPillar ? `${strongestPillar.score}%` : ""}</p>
      </div>
      <div class="summary-card">
        <p class="label">Blocking Gaps</p>
        <p class="value ${report.blockingGaps.length > 0 ? "red" : "green"}">${report.blockingGaps.length}</p>
        <p class="subtext">${report.blockingGaps.length > 0 ? "items to address" : "no blockers"}</p>
      </div>
    </section>

    <section class="executive-summary">
      <div class="executive-card">
        <h2>Strengths</h2>
        <p class="strength-headline">${getStrengthHeadline()}</p>
        <p class="strength-description">
          ${topPillars.length > 0
            ? `This codebase excels in ${topPillars.map(p => p.displayName.toLowerCase()).join(", ")} with scores above 50%. These areas provide a solid foundation for AI agent collaboration.`
            : "This codebase is building its foundation. Focus on the opportunities below to improve agent readiness."
          }
        </p>
        ${topPillars.length > 0 ? `
        <div class="strength-pills">
          ${topPillars.map(p => `<span class="strength-pill">${p.displayName} ${p.score}%</span>`).join("")}
        </div>` : ""}
      </div>
      <div class="executive-card">
        <h2>Opportunities</h2>
        ${opportunitiesHtml || "<p style='color: var(--text-muted); font-size: 0.85rem;'>All pillars are performing well. Consider advancing to the next maturity level.</p>"}
      </div>
    </section>

    <section class="level-section">
      <h2>Level Progress</h2>
      ${levelBarsHtml}
    </section>

    <section class="chart-section">
      <h2>Pillar Distribution</h2>
      ${radarChart}
    </section>

    ${appsHtml}

    <section class="pillars-section">
      <h2>Detailed Breakdown</h2>
      <div class="pillars-grid">
        ${pillarsHtml}
      </div>
    </section>

    ${blockingHtml}

    <footer>
      Generated by Agent Readiness Check v${VERSION} · <a href="https://github.com/mneves75/skills">https://github.com/mneves75/skills</a> · 9 Pillars · 5 Levels
    </footer>
  </div>
</body>
</html>`;
}

/**
 * Escape HTML special characters to prevent XSS
 */
function escapeHtml(text: string): string {
	return text
		.replace(/&/g, "&amp;")
		.replace(/</g, "&lt;")
		.replace(/>/g, "&gt;")
		.replace(/"/g, "&quot;")
		.replace(/'/g, "&#039;");
}

// ============================================================================
// Main
// ============================================================================

function showHelp(): void {
	console.log(
		generateHelp({
			name: "readiness-check",
			description: `Agent Readiness Check v${VERSION} - Factory.ai Framework\nSupports: ${getSupportedLanguages().join(", ")}`,
			options: [
				{ long: "help", short: "h", description: "Show this help message" },
				{ long: "format", short: "f", arg: "md|json|html", description: "Output format (default: md)" },
				{ long: "output", short: "o", arg: "file", description: "Write to file instead of stdout" },
				{ long: "scoring", arg: "weighted|strict|average", description: "Scoring mode (default: weighted)" },
				{ long: "language", arg: "lang", description: "Force language (override detection)" },
				{ long: "app", arg: "path", description: "Assess single app in monorepo" },
				{ long: "skip-tests", description: "Skip long-running test execution" },
				{ long: "skip-build", description: "Skip build verification" },
				{ long: "verbose", short: "v", description: "Show all checks, not just failures" },
				{ long: "min-level", arg: "1-5", description: "Exit with error if below level (for CI)" },
				{ long: "notes", description: "Generate session notes file" },
			],
			examples: [
				{ command: "bun run tools/readiness-check.ts", description: "Run with markdown output" },
				{ command: "bun run tools/readiness-check.ts --format=html --output=report.html", description: "HTML dashboard" },
				{ command: "bun run tools/readiness-check.ts --scoring=strict --min-level=3", description: "CI gate at L3 (strict)" },
				{ command: "bun run tools/readiness-check.ts --language=go --skip-tests", description: "Force Go language" },
			],
		}),
	);
}

async function main(): Promise<number> {
	const startTime = Date.now();

	const args = parseArgs(process.argv.slice(2), {
		flags: ["help", "h", "skip-tests", "skip-build", "verbose", "v", "notes"],
		options: ["format", "f", "output", "o", "min-level", "scoring", "language", "app"],
	});

	if (hasHelpFlag(args)) {
		showHelp();
		return EXIT_CODES.SUCCESS;
	}

	const format = getOption(args, "format") || getOption(args, "f") || "md";
	const outputFile = getOption(args, "output") || getOption(args, "o");
	const scoringMode = (getOption(args, "scoring") || "weighted") as ScoringMode;
	const languageOverride = getOption(args, "language") as Language | undefined;
	const appPath = getOption(args, "app");
	const skipTests = hasFlag(args, "skip-tests");
	const skipBuild = hasFlag(args, "skip-build");
	const verbose = hasFlag(args, "verbose") || hasFlag(args, "v");
	const minLevel = getOptionInt(args, "min-level");
	const generateNotes = hasFlag(args, "notes");

	// Progress logging
	const isStructuredOutput = format === "json";
	const log = isStructuredOutput ? console.error.bind(console) : console.log.bind(console);
	const progressStream = isStructuredOutput ? process.stderr : process.stdout;

	log(`Agent Readiness Check v${VERSION} (Factory.ai Framework)`);
	log("=".repeat(50));
	log("");

	// Initialize adapters
	initializeAdapters();

	// Discover applications
	log("Discovering applications...");
	const discovery = await discoverApps(process.cwd());
	const repoRoot = discovery.repoRoot;

	// Filter to single app if specified
	let apps = discovery.apps;
	if (appPath) {
		const targetPath = path.resolve(appPath);
		apps = apps.filter((a) => a.path === targetPath || a.relativePath === appPath);
		if (apps.length === 0) {
			log(`Error: No application found at ${appPath}`);
			return EXIT_CODES.VALIDATION_ERROR;
		}
	}

	// Detect or override language
	let primaryLanguage: Language;
	if (languageOverride) {
		primaryLanguage = languageOverride;
		log(`Language: ${primaryLanguage} (override)`);
	} else {
		const detection = await detectLanguage(repoRoot);
		primaryLanguage = detection.primary;
		log(`Language: ${primaryLanguage} (confidence: ${detection.confidence}%)`);
	}

	const structureType = discovery.isMonorepo ? "monorepo" : "single";
	log(`Structure: ${structureType}${apps.length > 1 ? ` (${apps.length} apps)` : ""}`);
	log(`Scoring: ${scoringMode}`);
	log("");

	// Run checks for each app
	const appScores: AppScore[] = [];
	const options: CheckOptions = {
		skipTests,
		skipBuild,
		verbose,
		timeout: 120000,
	};

	const scoringConfig: ScoringConfig = {
		mode: scoringMode,
		pillarWeights: DEFAULT_PILLAR_WEIGHTS,
	};

	// Create a single cache for the entire assessment run
	const cache = createFileCache();

	for (const app of apps) {
		log(`Checking: ${app.name} (${app.language})...`);

		// Override app language if specified
		if (languageOverride) {
			app.language = languageOverride;
		}

		const results = await runChecksForApp(app, repoRoot, options, cache, log);
		const appScore = calculateAppScore(app, results, scoringConfig);
		appScores.push(appScore);

		log(`  → L${appScore.level} (${appScore.score}%)`);
	}

	// Log cache statistics in verbose mode
	if (verbose) {
		const stats = cache.stats();
		log(`\nCache: ${stats.hits} hits, ${stats.misses} misses (${Math.round(stats.hits / (stats.hits + stats.misses) * 100) || 0}% hit rate)`);
		log(`  Files cached: ${stats.existsCached} exists, ${stats.textCached} text, ${stats.jsonCached} json, ${stats.readdirCached} dirs`);
	}

	// Aggregate org score
	const orgScore = aggregateOrgScore(appScores, scoringConfig);

	// Collect all check results for categorization
	const allChecks: CheckResultWithMeta[] = appScores.flatMap((a) => a.checks);

	// Categorize results
	const blockingGaps = allChecks.filter((r) => !r.pass && r.check.level <= 3 && !r.skipped);
	const warnings = allChecks.filter((r) => !r.pass && r.check.level > 3 && !r.skipped);
	const passingChecks = allChecks.filter((r) => r.pass);

	// Get recommendations from first app (or aggregate)
	const recommendations =
		appScores.length > 0
			? getTopRecommendations(appScores[0]!, 3).map((r) => ({
					pillar: r.pillar,
					check: { id: r.check.id, name: r.check.name },
					impact: r.impact,
					reason: r.reason,
				}))
			: [];

	const now = new Date();
	const report: ReadinessReport = {
		version: VERSION,
		repoName: getRepoName(),
		date: now.toISOString().split("T")[0] ?? now.toISOString().slice(0, 10),
		timestamp: now.toISOString(),
		structure: structureType,
		language: primaryLanguage,
		scoringMode,
		maturityLevel: orgScore.level,
		overallScore: orgScore.score,
		apps: appScores,
		pillars: orgScore.pillars.map((p) => {
			const pillarChecks = allChecks.filter((c) => c.check.pillar === p.pillar && !c.skipped);
			const passed = pillarChecks.filter((c) => c.pass).length;
			const total = pillarChecks.length;
			const score = total > 0 ? Math.round((passed / total) * 100) : 0;
			return {
				pillar: p.pillar,
				displayName: p.name,
				score,
				level: p.level,
				passed,
				total,
				checks: allChecks.filter((c) => c.check.pillar === p.pillar),
			};
		}),
		blockingGaps,
		warnings,
		passingChecks,
		recommendations,
	};

	// Render output
	let output: string;
	switch (format) {
		case "json":
			output = renderJson(report);
			break;
		case "html":
			output = renderHtml(report);
			break;
		default:
			output = renderMarkdown(report);
	}

	// Output
	if (outputFile) {
		await Bun.write(outputFile, output);
		log(`Report written to: ${outputFile}`);
	} else {
		console.log(output);
	}

	// Generate session notes if requested
	if (generateNotes) {
		const durationMs = Date.now() - startTime;
		const note = generateSessionNotes(report, durationMs);
		const notesPath = await writeSessionNotes(note, process.cwd());
		log(`Session notes written to: ${notesPath}`);
	}

	// Check minimum level requirement
	if (minLevel !== undefined && orgScore.level < minLevel) {
		log(`\nFailed: Maturity level ${orgScore.level} is below required level ${minLevel}`);
		return EXIT_CODES.VALIDATION_ERROR;
	}

	log("");
	log(formatOrgSummary(orgScore));

	return EXIT_CODES.SUCCESS;
}

try {
	const code = await main();
	process.exit(code);
} catch (err) {
	const message = err instanceof Error ? err.message : String(err);
	console.error(`readiness-check: Fatal error: ${message}`);
	process.exit(EXIT_CODES.FATAL_ERROR);
}
