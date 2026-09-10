# Delegation

Read before the first dispatch. `mneves-fable-orchestrator` owns routing; this file owns the budget,
the brief, and the failure modes specific to a repo-wide audit.

## Budget

Agents can't judge their own resource allocation, so it is stated here. Match the class, don't
improvise a bigger fan-out.

| Task class | Workers | Bound |
|---|---|---|
| A question answerable from one known file | 0 — read it yourself | — |
| Bounded discovery (one subsystem, known entry point) | 1 explore agent | ~10 tool calls |
| Repo-wide audit or unknown scope | ≤3 explore agents in parallel, disjoint path sets | ~15 calls each |
| Multi-file implementation | 1 execution lane per path set | serialize where paths overlap |
| Independent review with fresh context | 1 | one round |

## When delegating is a net loss

- A handful of reads, or work already assigned to another worker.
- Anything needing session-only credentials, MCP tools, or an attached device connection.
- Any decision the main session owns: requirements, architecture, authorization, acceptance.
- Subtasks that are not actually independent. If B needs A's findings, parallelism degenerates into
  serial execution plus coordination overhead — strictly worse than doing it in one context.

A multi-agent run costs roughly an order of magnitude more tokens than working directly, and
orchestration has been measured adding cost with no gain on tasks that don't split cleanly. The
value has to justify the burn. Delegate because the work is independent, substantial, and
objectively verifiable — not because parallelism feels faster.

## Worker brief

Vague briefs are the documented failure: workers duplicate each other and leave the same gap
uncovered. Every brief carries all six fields.

```
Goal:              one concrete outcome
Owned paths:       exact paths this worker may change
DO NOT touch:      the other workers' paths, named explicitly
Context:           current behavior, exact errors, evidence already gathered
Return:            required format (see below)
Stop when:         the falsifiable condition, plus the retry bound
```

Every brief also states, verbatim in substance: you share this tree with other workers, preserve
changes you did not make, do not spawn subagents, do not run OptMem, and do not commit or push.
Delegation never widens authorization — a worker inherits the task's scope and nothing more.

## Return contract

- ≤2k tokens of distilled findings. Conclusions and file references, not transcripts.
- Long output goes to a file; pass the path back, not the contents. Dumping a worker's raw output
  into the orchestrator's window defeats the reason for delegating.
- Evidence is a command and its actual result, never a claim that a check passed.

## Ownership discipline

Discovery parallelizes freely because it is read-only. **Implementation does not.** In this skill
specifically, items 1 (slop) and 2 (performance) touch the same files — running them as concurrent
writers is the degenerate case. Partition by path, or serialize.

Never measure performance while another worker is writing to the tree.

An executor stopped by an error, timeout, or quota may already have changed files outside its stated
ownership, or left a deliberate break unrestored. Inspect the actual working tree — `git status -sb`
and the real diff — before accepting or discarding its work. Review the diff, never the report.
