# Complexity evidence for code review

Use [moznion/cccc](https://github.com/moznion/cccc) as a local navigation signal
for supported source changes. It measures cognitive and cyclomatic complexity;
it does not prove correctness, security, performance or maintainability.
Run it before the independent reviewer, then adversarially challenge the change:
what plausible input, assumption or lifecycle would break it? Substantiate each
finding with the diff, a source reference or a focused behavior check.

## Installation and upgrade

`cccc` is optional and not bundled. Check `command -v cccc` and `cccc --version`.
The sibling `scripts/install-cccc.py` ships with this skill; Python 3.10+ and
network access are required. It reads the only release pin in
`scripts/cccc-release.json`, verifies the archive against reviewed SHA-256 values,
copies only its regular binary member, verifies its version and refuses replacement.
It supports macOS and Linux on ARM64 and x86-64; other platforms use the
[upstream release instructions](https://github.com/moznion/cccc#install--build).
Do not silently substitute an older unrelated tool also named `cccc`.

Pass an explicit new binary path in an existing directory, for example:

```sh
python3 /path/to/autoreview/scripts/install-cccc.py /approved/bin/cccc
/approved/bin/cccc --version
```

The installer never edits shell profiles or PATH. The caller owns approval for
outside-repository installation and existing-binary replacement. Single-skill
installs keep the script, manifest, reference and tests together. SHA-256 proves
matching the reviewed release bytes, not independent provenance or safety.
Upgrades require checking upstream assets, updating the manifest once, rerunning
the offline installer controls and real positive/failure controls. A source build
is a deliberate alternative, not an automatic fallback; crates.io omits Kotlin.

## Freeze the measurement

1. Pin the review base and target commit or snapshot. Inventory changed supported
   source files from that exact diff, including renames, deletions and untracked
   files in an authorized local review. Never reset or stash another person's work.
2. Record the binary version, source/config identity, expected files, cwd and flags.
   Check the installed version's actual language adapters and extensions: omitted
   or unsupported languages are **not analyzed**, not zero-complexity successes.
3. Use the owning repository's config and exclusions. Run from its root, or pass
   `--config` explicitly. Disable cache writes with `--no-cache` and expose the full
   population with `--min 0`. Do not disable policy with `--no-config`, add arbitrary
   limits, change exclusions or create a blocking CI gate just to improve scores.
4. Analyze focused files or source directories, never execute reviewed code. Use
   literal quoted path arguments (an array in a script), not whitespace-split Git
   output or `eval`. Do not pass newline-delimited paths through shell substitution.
   Do not prefix a whole-repo scan with `--no-ignore` to force apparent coverage.
5. Save stdout, stderr and exit code outside the source scope. A failed command is
   evidence to interpret, never a reason to discard its status using `|| true`.

For a repository with JSON output enabled and an existing evidence directory:

```sh
cccc --version
cccc --no-cache --min 0 --pretty src/ > /approved/evidence/complexity.json
# Capture stderr and the exit status in your harness, even when it fails.
```

Do not assume a `--json` switch exists. A config containing `table = true` cannot
be reversed by a CLI flag in the pinned release. Retain the table and its warning
stream, reconcile coverage manually, and report structured comparison unavailable.
Do not silently load a different config merely to obtain JSON. If the repository
explicitly permits a temporary effective config, record exactly which presentation
or cache setting changed and preserve its language, threshold and exclusion policy.

## Judge coverage before scores

The pinned CLI uses status 0 for a completed run, 1 for a threshold breach and 2
for usage/config failures. Check stderr and the report too: unreadable files may
be omitted while the command succeeds, and recovered parses can be partial.

For JSON, inspect `summary.file_count`, `summary.function_count`,
`summary.parse_error_count`, `summary.parse_error_files` and per-file
`parse_errors`. Reconcile the report's `files[].path` against the expected file
inventory after accounting for authorized exclusions. An unexpected missing file,
parse failure, invalid JSON or zero files means **incomplete/unavailable evidence**,
never PASS. A file with no functions is not itself a parse failure. Top rankings
omit the full file inventory; collect the full report first when coverage matters.

For useful comparisons, run base and target through the same version and policy
in isolated snapshots. Compare corresponding functions manually using the diff,
path, nesting/children, signature and body; names and line numbers are not stable
identifiers. A rename, overload or extracted helper can make correspondence
ambiguous: report it as not comparable. Do not compare repository sums across
different scopes, changed exclusions, parser versions or configuration policies.

A threshold breach under existing policy is a finding to resolve with the owner;
it is distinct from analyzer unavailability. High scores identify code to inspect.
Low scores do not excuse hidden coupling, complexity moved into helpers, missing
tests or an incorrect implementation. Never mechanically refactor to satisfy a
number. Report affected functions and why a change helps comprehension or behavior.

## Supply evidence to an isolated reviewer

The autoreview engine runs in an empty sandbox and cannot collect source metrics
itself. Gather evidence locally first. Put a concise version/config/coverage and
changed-function summary in a repository-relative context file and pass it through
the helper's `--prompt-file` / `--dataset` controls so the normal sensitive-path,
credential-scanning and mutation checks still apply. Do not pass raw source or
metrics to another service without the task's disclosure authorization.

Missing `cccc` is reported and independent standards/spec/adversarial review
continues. If the task makes complexity measurement an acceptance requirement,
missing or incomplete evidence marks that criterion BLOCKED; it does not change
the other criteria. Tests, independent review and frozen acceptance still decide
the outcome.

## Real binary controls

Use `python3 scripts/check-cccc.py /absolute/path/to/cccc`. It analyzes only
temporary fixtures and checks version, a known simple function, threshold breach,
parse recovery, missing input and an empty scan. It does not install or execute
fixture source. The ordinary test runner uses mocked downloads/execution and does
not contact a provider; this real-binary check is separate.

Sources: [pinned CLI](https://github.com/moznion/cccc/tree/9008fbfb747bdbd7651e3e6311307005659f003b/crates/cccc-cli/src),
[Google review guidance](https://google.github.io/eng-practices/review/reviewer/looking-for.html),
[SonarSource metric definition](https://www.sonarsource.com/docs/CognitiveComplexity.pdf).
