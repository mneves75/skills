# How to use these skills

Nine skills, one install. This page shows what each one does, how to trigger it, and what a
session looks like. For the one-line summaries see the [README](README.md); for the exact
procedure an agent follows, open `skills/<name>/SKILL.md`.

## Install once

```bash
npx skills@latest add mneves75/skills --all -g -y
```

That links every skill into the agents found on your machine (Claude Code, Codex, Cursor,
OpenCode, pi and others). Check what got installed with `npx skills@latest list`. If you
prefer git, clone the repo into your agent's skills directory; the README has the paths.

The readiness tool runs locally. An image-generation skill may send prompts and authorized
references to the image provider configured in your agent. Autoreview sends authorized review
inputs to the selected review provider after scanning them for credentials.

A skill is loaded when the agent decides your request matches its `description`. You can
also name it directly: in Claude Code, `/mneves-verify` or "use the mneves-eli5 skill".

| Skill | Use it when you want to… | Say something like |
|---|---|---|
| `autoreview` | review a fixed Git target with an isolated AI reviewer | "use autoreview on my local changes, including P3 findings" |
| `imagegen-frontend-mobile` | generate mobile screen or flow images, not code | "design a 4-screen iOS onboarding flow" |
| `mneves-eli5` | explain a thing to a specific audience | "explain OAuth to my dad" |
| `mneves-expert-review` | stress-test a plan or answer before it ships | "challenge this design" |
| `mneves-verify` | get an independent PASS/FAIL before "done" | "verify it", "prove it" |
| `mneves-fable-orchestrator` | split heavy work across models | "delegate the backend to codex" |
| `mneves-agent-readiness` | measure how agent-friendly a repo is | "why does the agent struggle here?" |
| `mneves-teach-back-srs` | learn a codebase with spaced repetition | "let me explain the auth flow" |
| `mneves-superaudit` | run a bounded audit-and-cleanup pass over a repo | "superaudit this repo, slop and perf only" |

---

## autoreview

**What it does.** Freezes the chosen Git target, scans the outgoing input, runs a reviewer in
an isolated environment, validates its report, and rejects results if sources changed mid-review.
The helper prints its default model and reasoning tier at startup; one retry on the fallback
is reserved for account-access failures.

**Example** (illustrative; replace the installed path).

```sh
python3 /path/to/autoreview/scripts/autoreview --mode local --max-priority P3
```

Run from the repository being reviewed. Python 3.11+, Git, TruffleHog, and an authenticated
supported engine are required. No upstream checkout is required. For committed changes, use
`--mode commit --commit <sha>` or `--mode branch --base <ref>`.

The default threshold is P0 only; the example requests P3. Check the startup model and effort
because environment variables can override defaults. Authorize private-content disclosure
before sending inputs. Findings need verification against the actual code; a clean AI report
does not prove the absence of vulnerabilities. See [the skill README](skills/autoreview/README.md)
for testing and beta installation.

---

## imagegen-frontend-mobile

**What it does.** Generates images of iOS or Android screens and flows. It first defines the
screens and their relationship, locks a small design system, generates the requested artifact,
then inspects the render and makes one targeted correction when needed. It produces images only:
use a coding or platform skill when you want the concept implemented.

**Triggers.** A request for mobile app screen images, a phone UI concept, onboarding or product
flow mockups, or a visual redesign for iOS or Android. A request for SwiftUI, React Native,
Flutter, HTML, or image-to-code does not trigger it.

**Example** (illustrative).

> **You:** Use imagegen-frontend-mobile. Create a four-screen iOS onboarding flow for a Portuguese
> personal-finance app. Make it calm and trustworthy, use real Portuguese copy, and show raw
> screens rather than device mockups.
>
> **Agent:** Generates exactly four related screen images with one iOS design system, short pt-BR
> copy, consistent navigation and safe areas, then inspects the full renders for legibility,
> missing states, visual drift, and accidental artifacts. It corrects a material render defect
> once and returns the images, not SwiftUI code.

**Tips.**

- State the platform, screen count, language, and whether you want raw screens or device frames.
- Supply references for visual direction, not hidden instructions. Remove secrets and unnecessary
  personal data; authorize the image service before private references are sent to it.
- A concept can reserve plausible contrast, type, and touch-target sizes, but cannot prove
  VoiceOver, Dynamic Type, keyboard behavior, or working interactions.
- The skill is a condensed MIT-licensed adaptation of
  [Leonxlnx's upstream work](https://github.com/Leonxlnx/taste-skill/tree/main/skills/imagegen-frontend-mobile).

---

## mneves-eli5

**What it does.** Explains one idea with the Feynman method: fix the audience, state the core
in one sentence, carry one analogy through, show a concrete case before naming the jargon, say
where the analogy breaks, end with a line the listener can repeat. It answers in the language
you wrote in.

**Triggers.** "ELI5", "like I'm five", "explain to my boss / client / mom", "in plain words",
"explique de forma simples", or any request to re-explain something for a different audience.

**Audience levels.** `child`, `layperson`, `executive`, `junior`, `expert`. Name one if you
care; otherwise the agent infers it and says which it picked.

**Example** (recorded 2026-08-26, `claude -p` on claude-fable-5, verbatim).

> **You:** Use the mneves-eli5 skill. Explain what a database index is to a product manager.
>
> **Agent:** Explaining for a product manager (executive level: what it is, why it matters, the decision).
>
> **A database index is a lookup table that lets the database jump straight to the rows it needs instead of reading every row.**
>
> Think of a 500-page book. Without an index, finding every mention of "refunds" means reading all 500 pages. With the index at the back, you flip to "refunds → pages 12, 87, 203" and go straight there. A database index does the same for a column: "customer_email → row 4,812". A query that took 3 seconds scanning 10 million rows can take 3 milliseconds.
>
> Why it matters to you:
>
> - **Speed is a product feature.** Slow search, slow dashboards, and timeouts under load are very often "missing index" problems, and they surface only once real data volume arrives — not in demos.
> - **Indexes are not free.** Every index is a second copy the database must update on each write. Over-indexing slows down inserts and eats storage; the book analogy breaks here, because a book's index doesn't have to be rewritten every time you add a page.
> - **The decision you'll face:** when an engineer says "we need an index on that field" it's a cheap, low-risk fix for read speed; when they say "too many indexes" on a write-heavy table (event logs, orders), that tradeoff is real and worth a conversation.
>
> Takeaway to repeat: an index trades a little write cost and storage for much faster lookups on the columns you search by most.
>
> Want the version with the mechanism (B-trees, composite indexes, why the column order matters)?

**Tips.**
- "Now for my CTO" re-explains at another level without starting over.
- The skill refuses "it's easy" and "obviously". If you want that tone, you are on your own.
- Mixed room? It writes for the least technical person and adds a marked "for the engineers"
  block.

---

## mneves-expert-review

**What it does.** Runs a six-step pass over a draft (or a request with no draft yet): clarify
the real objective, rebuild from first principles, research only when it changes the answer,
attack it from three angles at once (hostile panel, pre-mortem, the strongest opposing case),
generate alternatives that differ in kind and compare them on weighted criteria, then improve,
audit once, and deliver. It scales with the stakes: a factual one-liner gets the mental
version, a migration plan gets the full pass.

**Triggers.** "expert review", "rigorous pass", "best possible answer", "challenge this",
"stress-test", "revisão rigorosa", "melhor solução", or before any high-stakes plan, design,
recommendation or architecture decision.

**Example** (recorded 2026-08-26, `claude -p` on claude-fable-5, verbatim; the prompt asked for under 400 words).

> **You:** Use the mneves-expert-review skill. Challenge this plan and return the improved version: "We will move user sessions from Redis to Postgres to cut one piece of infrastructure. Steps: 1) add a sessions table, 2) change the auth middleware to read/write Postgres, 3) run a script that copies live Redis keys into the table and deletes them from Redis, 4) turn off Redis. Session reads are rare so performance is not a concern."
>
> **Agent:** **Improved plan: sessions Redis → Postgres**
>
> **Challenge the premise first.** "Cut one piece of infrastructure" only holds if nothing else uses Redis (rate limiting, caches, queues, pub/sub). Grep for every Redis client before step 1 — if anything else depends on it, this migration removes nothing and the plan should stop here. Also: "reads are rare" is almost never true for sessions — the auth middleware reads on *every authenticated request*. Measure current Redis ops/sec; that number is the real load Postgres inherits.
>
> **Plan**
>
> 1. **Inventory and baseline.** List all Redis usages. Record session read/write rates and p99 auth-middleware latency (the acceptance bar for step 5).
> 2. **Schema.** `sessions(id PK, user_id, data jsonb, expires_at timestamptz, created_at)`, index on `expires_at` and `user_id`. Redis TTL is free; Postgres needs a scheduled purge (`DELETE WHERE expires_at < now()` via pg_cron or a job) — without it the table grows forever. Session IDs stay opaque/random; store a hash if you treat them as secrets.
> 3. **Dual-write, Redis-read.** Middleware writes to both, reads Redis. Ships behind a flag, fully reversible.
> 4. **Backfill.** Copy remaining Redis keys with their TTLs (`TTL` → `expires_at`) into Postgres. **Do not delete from Redis** — the original step 3's "copy then delete" is a one-way door with no rollback and a race against sessions written mid-copy.
> 5. **Flip reads to Postgres.** Compare latency/error rate against the step 1 baseline for at least one full session-lifetime cycle. Roll back = flip the flag.
> 6. **Stop writing to Redis, then decommission** after the longest session TTL has elapsed — remaining keys expire on their own, no deletion script.
>
> **Key risks the original missed**
> - Write amplification: touching `last_seen` on every request creates a hot UPDATE row per user and WAL/vacuum churn. Update at most once per N minutes, or drop the sliding-expiry behaviour.
> - Logout / "revoke all sessions" must work identically in both stores during dual-write.
> - Connection pool: middleware now holds a DB connection per request; check pooler limits (PgBouncer) before flipping.
>
> **Rejected alternative worth stating:** stateless signed tokens (JWT/PASETO) remove the session store entirely — but revocation becomes hard. Only pick it if you don't need server-side logout.
>
> **Remaining uncertainty:** whether Redis is actually single-purpose, and the real read rate. Both are five-minute checks and decide whether the project exists at all.

**Tips.**
- Give it the draft, not a summary of the draft. It reads the whole thing first.
- Use `mneves-verify` afterwards when the user, repository, workflow, or risk requires an
  independent judge. The panel argues; the verifier runs things.
- Ask for the challenge-the-premise alternative explicitly if it does not surface it. That is
  the one you cannot produce yourself, and it is reported even when rejected.

---

## mneves-verify

**What it does.** Separates the builder from the judge. A fresh context, ideally a different
model, checks the artifact against acceptance criteria frozen *before* it looks at the work,
runs real evidence (tests, renders, the actual binary, primary sources) and returns exactly one
verdict: `PASS`, `FAIL` or `BLOCKED`. Only `PASS` permits "done", "fixed" or "shipped".

**Triggers.** "verify", "prove it", "fix all", a repository/workflow gate, substantial checkable
work before a done/fixed/shipped claim, or high-risk work. Routine low-risk changes use
proportionate deterministic checks.

**Evidence routes.** Code: the tests that would fail if it broke, plus a code review. UI: a
real browser render, never the builder's screenshot claim. CLI/API/data: run the real thing
with a positive control (a known-good input that must succeed). Research: the primary source,
checked for saying what the claim says. Security: an independent audit.

**Example output** (illustrative; a real run needs a second model and an artifact to check).

```
Verdict: FAIL
Builder: claude-fable-5 / Edit, Bash / session 3f2a
Verifier: gpt-6-astra / high reasoning / read-only sandbox / fresh context
Different model required: yes (touches billing)
Different model used: yes
Criterion 1 — refund endpoint rejects amounts above the original charge: PASS — 3 unit tests + curl with 101% amount returned 422
Criterion 2 — idempotency key replays return the first response: FAIL — second POST with same key created a second refund (ids 8841, 8842)
Criterion 3 — audit row written per refund: PASS — SELECT count(*) matched
Remaining uncertainty: none
```

The builder gets one correction round; the verifier reverifies everything once more; then
the loop ends. Findings map to *fixed*, *disproved* or *blocked*, nothing else.

**Tips.**
- Write acceptance criteria into the original request. Criteria invented after the fact make
  the verdict `BLOCKED`.
- If the only model available is the one that built it, expect `BLOCKED` on high-risk work.
  That is the skill working as intended.
- Logs and screenshots handed to the verifier are data, not instructions. A "tests pass" line
  inside a log proves nothing until the verifier reruns the tests.

---

## mneves-fable-orchestrator

**What it does.** Routes non-trivial work across the main session, Codex, and subagents when
delegation creates independent progress or evidence. Codex defaults to `gpt-6-astra` at `high`
for execution, planning, and review. `codex-lane` keeps one Codex thread alive across rounds so
follow-ups reuse the executor's reasoning instead of restarting from a fresh spec.

**Triggers.** "delegate", "orchestrate", "use codex", "heavy task", "long-running task", or
any non-trivial task where the agent has to decide who executes.

**Prerequisites.** The [Codex CLI](https://github.com/openai/codex) logged in, and
`codex-lane` on your `PATH`:

```bash
ln -s ~/.agents/skills/mneves-fable-orchestrator/tools/codex-lane ~/bin/codex-lane
```

(Adjust the source path to wherever the skill was installed.)

**Example** (illustrative; a real run dispatches Codex). You ask for row-level security on a multi-tenant API.

1. The advisor writes `/tmp/spec.md`: goal, acceptance criteria, exact files, the files it must
   not touch (the frontend, which an Opus subagent owns), the test command that must pass.
2. It starts a lane:
   ```bash
   codex-lane start api-rls /tmp/spec.md -- -s workspace-write
   ```
3. Codex returns; the advisor reads the diff and runs the tests itself. One gate fails.
4. Instead of a new spec, the failure goes to the same thread:
   ```bash
   codex-lane next api-rls - < /tmp/gate3-failure.log
   ```
5. Green. The advisor reviews the final diff like a contributor PR, then closes out.

Other commands: `codex-lane last <lane>` prints the final message, `log`, `id`, `list`,
`drop`. A plain `codex exec` that unexpectedly needs a second round can be wrapped after the
fact with `codex-lane adopt <lane> <thread-id>`.

**Tips.**
- One goal per dispatch. A grab-bag spec produces a grab-bag diff.
- Pair every hard "never" in a spec with an exit ("if the gate fails after honest attempts, stop and report"). A cornered executor satisfies the letter of the rule in ways you will not like.
- Keep small direct edits in the current session; delegation costs more than it saves.
- Verify the real diff and focused proof. Add a fresh-context review when task risk or a gate
  requires it.
- A lane is bound to the directory and sandbox flags it started with, on purpose: resuming
  from another repo cannot aim Codex at the wrong tree.

---

## mneves-agent-readiness

**What it does.** Scores a repository on how well it supports an agent's loop of gathering
context, making a change, verifying it and iterating. Nine pillars (style, build, testing,
documentation, dev environment, observability, security, task discovery, product), fifty-plus
checks, a percentage and a maturity level L1–L5. Ships with a Bun/TypeScript tool that runs
locally and uploads nothing.

**Triggers.** "agent readiness", "why isn't the agent working well here", onboarding a repo,
planning infrastructure work.

**Running the tool.** It assesses the current directory.

```bash
git clone https://github.com/mneves75/skills.git ~/src/skills
cd ~/src/skills/tools && bun install

cd /path/to/your-project
bun --bun ~/src/skills/tools/readiness-check.ts                     # markdown to stdout
bun --bun ~/src/skills/tools/readiness-check.ts --format=html --output=report.html
bun --bun ~/src/skills/tools/readiness-check.ts --skip-tests --skip-build   # static checks only, fast
bun --bun ~/src/skills/tools/readiness-check.ts --min-level=3       # exit 1 below L3, for CI
bun --bun ~/src/skills/tools/readiness-check.ts --app packages/api  # one app in a monorepo
```

`--help` lists the rest (`--format json`, `--scoring strict|average`, `--language`).

**Example** (real run, 2026-08-26). Against FastAPI (`9a8a13f`, static checks) the tool reports L3 at 61.7%:
Style 88%, strong documentation, weaker on task discovery and product signals. The
[live report](https://mneves75.github.io/skills/fastapi.html) shows the full breakdown.

**The five-question shortcut** the skill uses when you just want a feel for a repo:

1. Is there a `CLAUDE.md` / `AGENTS.md` / `.cursorrules` with build and test commands?
2. Strict typing and a linter?
3. Do tests run without manual setup?
4. Does CI give a clear pass/fail?
5. Is the whole loop under five minutes?

Five yes answers is L5; each no drops a level. Level 3 is the working minimum.

**Tips.**
- The single highest-impact fix is a context file under 300 lines with commands that work.
- Scores are this tool's own; they are not comparable with Factory.ai's hosted assessment,
  whose pillar structure inspired them.

---

## mneves-superaudit

**What it does.** Turns "audit everything and clean it up" into a bounded pass with four
selectable items — slop removal, performance wins, agent DX and verification loops, PR/issue
triage — each ending on a falsifiable condition, run through five phases with stop gates before
every external write. It grants no authority: commit, push, tag, release, deploy and PR merge each
need your explicit word for that action and target.

**Triggers.** "superaudit", "audit the codebase and clean it up", "hunt for performance wins",
"find slop", "audit open PRs", or an end-to-end review → fix → verify → release pass. Not for a
single bug fix or a one-file change.

**Example** (illustrative). You point it at a repo and pick two items:

```
superaudit ~/dev/myapp — items 1,2 only
```

1. It fills the brief with you, then opens `agent_planning/superaudit-2026-09-10.md` and records
   `git status -sb` before touching anything.
2. Three read-only explore agents sweep disjoint path sets. Discovery parallelizes; nothing is
   edited yet.
3. It reports ranked findings — what, `path:line`, why it's wrong, the fix, the risk, and the check
   that would prove the fix safe. **Stop.** You pick what to cut.
4. It implements only your selections. Items 1 and 2 touch the same files, so those run
   partitioned by path or serialized, never as concurrent writers.
5. It measures: baseline and candidate, same recorded conditions, one variable. Two of the three
   "wins" land inside noise and are reported inconclusive rather than claimed.
6. **Stop.** You read the diff. Release only happens if you then ask for it by destination.

**Tips.**
- Name the items explicitly. `items 1,2` skips agent DX and PR triage entirely, and the release
  phase never loads.
- Don't run it on a tree another agent is writing to. It preserves changes it doesn't own, but
  concurrent writes make the item-2 measurements worthless.
- Fill `Out of scope` in the brief. It is the field that most reliably prevents a three-hour run.
- The progress file is the point of a long run, not a byproduct — it is what survives compaction,
  and it is the deliverable for item 3.
- Amend the skill only from failures you actually saw. Instructions added "just in case" cost
  context on every future run.

---

## mneves-teach-back-srs

**What it does.** You explain part of a codebase; the agent reads the actual code while you
talk, asks three to five follow-up questions aimed at what you got wrong or skipped, and turns
each gap into a flashcard. Cards live in `.ai-learn/srs.db` inside the project (auto-ignored
by git) and come back on an SM-2 schedule, the same algorithm Anki uses.

**Triggers.** "let me explain", "teach back", "quiz me", "review cards", "what do I know
about", "test my understanding".

**Prerequisite.** Python 3.10+. No packages.

**Four modes.**

| You say | Mode | What happens |
|---|---|---|
| "Let me explain how X works" | Teach-back | you talk, agent verifies against code, asks follow-ups, writes cards |
| "Quiz me" / "what's due?" | Review | due cards one at a time; you self-rate 0–5 |
| "How am I doing?" | Stats | totals, due, mastered, struggling, average ease |
| "Export cards" | Export | Markdown or CSV (Anki-importable) |

**Example.**

> **You:** Let me explain the safety pipeline in ai-shell. There's a regex matcher for
> dangerous commands and a scorer from 1 to 10; high scores get blocked.
>
> **Agent** *(illustrative session; reads `safety/`)*: Pattern detection and scoring are right. Three follow-ups:
> 1. `safety/intent.rs` runs *before* the matcher. What does it do, and why first?
> 2. `safety/scorer.rs:47` treats 7+ and 9+ differently. What is the difference?
> 3. The matcher uses `RegexSet` instead of looping. Why does that matter for 56 patterns?
>
> *(after your answers)* Two gaps found. Cards added:
> - "Why does the intent gate run before pattern matching?" (medium)
> - "What happens at score 7–8 versus 9+?" (easy)
> Session recorded. First review due in one day.

Later, "quiz me" shows the question, waits, shows the answer, asks for a 0–5 rating, and
reschedules: a 5 pushes the card out, anything under 3 resets it.

**Behind the scenes** the agent runs `scripts/srs_db.py` from the skill's folder, with your
project as the working directory. Recorded 2026-08-26 in an empty directory:

```
$ python3 scripts/srs_db.py init
Initialized SRS database at /tmp/demo/.ai-learn/srs.db

$ python3 scripts/srs_db.py add-card --question "Why does the intent gate run before pattern matching?" \
    --answer "It can reject catastrophic intents without a model call (safety/intent.rs), so the cheaper check runs first." \
    --context "safety/intent.rs" --tags "safety,pipeline" --difficulty medium
Card #1 added: Why does the intent gate run before pattern matching?...

$ python3 scripts/srs_db.py due
1 card(s) due:

  #1 [medium] Why does the intent gate run before pattern matching?
    EF=2.50 | interval=0d | reps=0

$ python3 scripts/srs_db.py review --card-id 1 --quality 4
{"card_id": 1, "quality": 4, "new_interval_days": 1, "new_ease_factor": 2.5, "next_review": "2026-08-27 19:14:48", "repetitions": 1}

$ python3 scripts/srs_db.py stats
{"total_cards": 1, "due_now": 0, "mastered": 0, "struggling": 0, "sessions": 1, "total_reviews": 1, "today_reviews": 1, "upcoming_7d": 1, "avg_ease_factor": 2.5, "next_scheduled": "2026-08-27 19:14:48"}
```

`export --format csv > cards.csv` writes an Anki-importable file.

**Tips.**
- Scope a session to one subsystem or one data flow. "The whole backend" produces vague cards.
- Good cards ask *why* and point at a file. The agent is told to refuse cards that don't.
- The database is the memory. A new conversation starts by reading it, so nothing is lost
  between sessions.

---

## Combining them

A typical shipping flow: `mneves-fable-orchestrator` splits the work and dispatches it;
`mneves-expert-review` challenges the plan before code is written; `mneves-verify` gives the
final verdict before anything is called done. `mneves-agent-readiness` is what you run first
on a repo where agents keep failing, and `mneves-eli5` is for the moment you have to explain
any of this to someone else. `imagegen-frontend-mobile` is the image-only path for mobile concepts;
hand its chosen direction to the relevant implementation workflow when code is required.
