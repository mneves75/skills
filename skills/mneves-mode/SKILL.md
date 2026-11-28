---
name: mneves-mode
description: Explicit operator mode (/mneves-mode, "use mneves mode") that frames a task, orders its phases, and runs each phase's gate through the installed skill or a stated fallback. Use only when invoked by name.
license: Apache-2.0
---

# mneves-mode

Use only when the user types `/mneves-mode` or `$mneves-mode`, or asks for "mneves mode" by name.
Never start it from an ordinary prompt. Every skill stays directly discoverable without it; this
mode adds the order of phases and the gates between them.

## 1. Authority

- **No new permissions.** Invoking this mode grants nothing. A review-only request stays
  read-only, and a mandatory gate stays closed until it passes or the authority its rule names
  waives it.
- **Explicit-only skills stay explicit.** Never start one yourself: `full-stop`, `poteto-mode`,
  `statechart`, `thermos`, `thermo-nuclear-review`, `reframe`, `automate-me`, any skill whose own
  description says it runs only by name, or a deploy through `mneves-ship-deploy`. Name it and
  let the user type it. Plain "ship" never deploys.
- **Host overlays.** The user's own instructions may name an overlay that adds skills, gates or
  ordering for their machine. An overlay can add or tighten a gate, never relax one.

## 2. Frame

Before touching files or picking a skill:

1. Restate the goal, the smallest correct change that meets it, and how it will be checked.
2. Name the phase: plan or decide, build or fix, refactor, review or audit, PR lifecycle,
   release or deploy, or a specialized artifact.
3. Name the risk tier.
   - **Standard:** reversible work inside the repository.
   - **Risky:** a release or deploy, security or privacy, permissions or secrets, production or
     client data, money, legal terms, or a contested result.
4. Before editing in a repository, fetch the remote and reconcile the working branch with its
   upstream. Never stash, reset or switch someone else's uncommitted work to do it.

## 3. Pick skills from the live catalog

The host's skill listing is the catalog; this file keeps no inventory of it.

- An explicit request for a skill wins. Otherwise pick the most specific listed skill for the
  current phase. A skill listed by name without a description still counts as installed.
- Read the chosen `SKILL.md` before following, describing or skipping any of its steps.
- If a skill the playbook names is missing, say so once and use the playbook's fallback. Never
  imply a skill ran when it did not.
- Third-party siblings this mode can use, with their sources and fallbacks, are listed in
  [references/optional-siblings.md](references/optional-siblings.md).
- Reassess when the phase changes (build, then review, then verification, then release). Keep the
  same skill for small follow-ups inside one phase.

## 4. Playbooks

Open only the playbook for the current phase and run its steps in order.

| Phase | Playbook |
|---|---|
| Build or fix | [playbook-build.md](references/playbook-build.md) |
| Scoped refactor | [playbook-refactor.md](references/playbook-refactor.md) |
| Plan or high-stakes decision | [playbook-decide.md](references/playbook-decide.md) |
| Review, audit or verification | [playbook-audit.md](references/playbook-audit.md) |
| PR lifecycle | [playbook-pr.md](references/playbook-pr.md) |
| Release and deploy | [playbook-release.md](references/playbook-release.md) |
| Specialized artifacts and learning | [playbook-artifacts.md](references/playbook-artifacts.md) |

## 5. Gate order for a full task

When one request runs from change to release, the gates run in this order. Skip a gate only
when it does not apply to the task; say which ones you skipped and why.

1. **Origin:** reconciled before work (section 2, step 4).
2. **Frame:** goal, smallest verifiable change, risk tier.
3. **Test first:** behavior changes get a failing test before the fix (`tdd`).
4. **Improvement survey:** only when the user asks for one (`improve`).
5. **Standards and spec review** of the diff (`code-review`, else `autoreview`). Commit on the
   working branch first: `code-review` reads committed history only.
6. **Source security audit:** only when the user asks for one. Use `security-audit` for the audit
   and `mneves-security` for the fixes.
7. **Independent verification** in a fresh context (`mneves-verify`). Fix what it finds and run
   it again until it passes.
8. **Release record:** version, changelog and docs updated and committed on a working branch.
   Check which pushes, merges and tags trigger a deploy; push now only if the push deploys
   nothing.
9. **Pre-deploy security verdict** on the exact commit (`mneves-security`), before any deploying
   push, merge or tag. It binds to the audited tree, so a merge that lands a different tree
   needs a new verdict before it deploys.
10. **Readiness** on the same commit before a staging or production deploy
    (`mneves-production-readiness`).
11. **Merge:** only with the user's authorization in this request. A merge that deploys
    production belongs to step 12: it waits for the staging proof and the owner's approval of the
    exact candidate and target. Then remove the worktree and the local branch the task created
    (`git branch -d`, never `-D`). Delete the remote branch only when this session opened the PR
    from a branch it created, the PR is not from a fork and no open PR uses the branch as its base:
    `git push --force-with-lease=refs/heads/<branch>:<merged head SHA> origin --delete refs/heads/<branch>`.
    Name the full ref both times: a bare `<branch>` can resolve to a tag of the same name, which
    the lease does not cover. If the push is refused or any condition fails, keep the branch and
    report it. Tag here only
    when no deploy follows.
12. **Deploy:** only on an explicit `ship-staging` or `ship-prod` (`mneves-ship-deploy`). It
    proves the release live, then applies that target's tag (beta for staging, `vX.Y.Z` for
    production). After production succeeds, it tears down the staging resources the task
    started; `ship-staging` stops after the staging proof and its beta tag.
13. **Cleanup:** remove the scratch files, worktrees and caches the task created. List what is
    left with its exact removal command.
14. **Report** (section 7).

Two rules hold throughout. On a long task, keep the status in a checked-in file, so the work
survives a lost context. Stop before any action under section 8's hard stops.

## 6. Independent gates

- Review and verification run in a fresh context that did not build the change. Self-review,
  passing tests and green CI never count as an independent verdict.
- If a required review, security or readiness gate cannot run, mark it `BLOCKED` and continue
  only work that does not depend on it. Never fabricate or backfill a gate record.
- Risky work always gets an adversarial challenge to its weakest assumption before it is called
  done.

## 7. Report

Lead with the outcome. Then give the commands run with their exact results, what remains
unverified, the decisions made, and what you need from the user. Separate facts from
assumptions, and never claim done on a failing or skipped gate.

## 8. Cross-cutting rules

- **Local autonomy, hard stops.** Reversible work in the repository proceeds without asking:
  reading, searching, editing, tests, builds, linters, and commits on a working branch. Always
  stop before any of these:
  - deleting files or data you did not create;
  - force-pushing or rewriting history;
  - merging, tagging, releasing, deploying, or submitting to a store;
  - changes outside the repository;
  - handling credentials the task does not name;
  - opening client or personal records;
  - external messages or purchases;
  - materially expanding scope.

  "Run until done" never crosses this line.
- **Prototype reversible forks.** When a small local experiment can settle a reversible technical
  choice inside scope, run it and decide from what it shows. Product and preference calls stay
  with the user.
- **No model ids here.** Model and effort choices belong to `mneves-fable-orchestrator` when it
  is installed, otherwise to the host's configuration.
- **poteto-mode boundary.** If `poteto-mode` is active too, this mode selects the skills, gates
  and playbook. Use a poteto playbook only for a step this playbook does not cover. When both
  modes set a gate, apply the stricter one.
