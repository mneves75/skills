# Release closeout for this repository

Status: written 2026-10-27 and built on PR #29. Scope: this repository's own release procedure and
its readiness ledger, not the shipped skills.

## Assumptions (open decisions, built without an interview)

1. **PR #29 disposition is the owner's.** Every merge to `main` needs a full security audit of its
   tree or a named waiver. The options are to merge under one of those now, or to keep PR #29
   open and fold it into the next release PR. Built as: PR #29 stays open, and its body asks.
2. **Waiver horizon.** The 1.41.0 waivers expire 2026-10-28T03:37:58Z, a 24-hour ceiling the
   closing agent set, not the owner. The 1.38.0 waivers lasted a week, and the skill caps them at
   90 days. Built as: unchanged, with the question raised.
3. **Docs-only audit reuse.** For a ledger-only delta, `gates.md:74-77` reassesses only the
   always-on readiness set. The security gate still says "one full audit per tree"
   (`skills/mneves-security/SKILL.md:308`), so a ledger correction still costs a full audit. Built
   as: unchanged, and recorded here as a policy decision for the owner (an ADR if accepted). That
   skill is shared, so it is not changed from this repository.
4. **The tag needs owner approval.** Built as: a message drafted in the house format, not created.

## Problem

1.41.0 merged and went live, but on `main`, `MEMORY.md` and the readiness ledger and plan still
said "candidate, BLOCK, no waivers, nothing deployed", and the 1.40.0 entry still said
"pending". The drift is structural, not a one-off:

- **The tracked ledger cannot record its own binding result.** The gate audits a tree. Writing the
  WAIVED rows, cursor or gate-history row afterwards creates a new tree. That is why the 1.41
  closeout kept them in an ignored overlay.
- **`main` is the distribution channel.** `npx skills add mneves75/skills` installs from it, and
  Pages publishes after every green CI run on it. A standalone post-release docs merge is
  therefore a release. 1.38 needed PRs #24 and #25 for this, and 1.41 opened #29.
- **The rule already exists, but the procedure omits it.** Decision 17
  (`docs/specs/production-readiness/spec.md:62`) and `gates.md:74-77` say the binding run's
  ledger bookkeeping "waits for the next commit". `CONTRIBUTING.md#preparing-a-release` does not
  say so, and it has no tag step. As a result, v1.41.0 is untagged, and the documented rollback
  (`static.yml -f ref=<tag>`) has no anchor for the release that is live.
- **Duplicate facts are hand-maintained.** The ledger states the production commit three times
  (Cursors, Binding run, last gate-history row) and keeps a Totals summary. Nothing checks them:
  the PR #29 recount was done by hand, and the closeout's private overlay had a malformed Totals
  line (`Totals:135rows`).

## Decisions

1. **Release procedure** (`CONTRIBUTING.md#preparing-a-release`):
   - Tracked text in the release PR describes the candidate tree and points to where the binding
     result will live: the private record and the `vX.Y.Z` tag message. It makes no claim that
     merging turns false, such as "not deployed" or "BLOCK".
   - After live proof, and with owner approval, create an annotated `vX.Y.Z` tag whose message
     carries the verdict lines (security gate, readiness gate, waivers, gated tree and commit,
     CI run, Pages run with the served-byte result, and independent acceptance when one ran).
     These are the lines that v1.38.0 and v1.40.0 used between them. `mneves-security` requires the verdict in the tag message before a rollback to
     that tag can skip a new audit.
   - The previous release's binding bookkeeping (cursor, gate-history row, WAIVED rows,
     `MEMORY.md` state) lands in the next release PR, never as a standalone merge.
2. **Ledger guard.** `tools/scripts/check-readiness-catalog.py` also checks
   `docs/readiness/ledger.md`:
   - exactly one row per catalog control, plus `LOCAL-nn` rows;
   - statuses only from the contract vocabulary (plus `retired`);
   - the Totals line equals a recount;
   - Cursors, Binding run and the last gate-history row name the same production commit;
   - each WAIVED row states `underlying <status>` and an expiry in `YYYY-MM-DDTHH:MM:SSZ` form.

   The waiver check is deliberately stricter than the contract's example row
   (`references/ledger.md`). It enforces this repository's house format from 1.38: `underlying
   <status>; owner waiver @owner to <ISO-Z>`. A duplicate `LOCAL-nn` row fails. Padded cells
   and trailing spaces parse normally. Cursors and Binding run are compared even when there is no
   production gate-history row.
   CI already runs the guard and its planted-violation test (`ci.yml:97`).
3. **1.41.0 bookkeeping** (already on PR #29): the ledger, plan and `MEMORY.md` record the landed
   state, and Dependabot uses the `bun` ecosystem for `tools/`.

## Rejected alternatives

- **Skip Pages publication when `site/` bytes are unchanged.** This would remove the gate from
  skill changes. Those changes reach users through `main`, not through `site/`.
- **Write waivers into the tracked ledger before merge.** This changes the audited tree after the
  audit, so the gate would have to run again.
- **Generate the Totals and cursor lines.** A generator is more code than a check, and the
  ledger is hand-edited prose.

## Acceptance

- Every planted violation, one per guard rule, fails with a `file:line` message. The real ledger
  passes. `bash tools/scripts/check-readiness-catalog.test` exits 0, and each new case was seen
  failing before its rule existed.
- `CONTRIBUTING.md` has the three procedure steps, and `AGENTS.md` describes the guard's scope.
- The CI `check` job passes on the PR head.
- Out of scope, reported only: the `actions/checkout` Node 20 warning (the owner closed the
  Dependabot bump in PR #2), and the waiver horizon and audit-reuse policy above.
