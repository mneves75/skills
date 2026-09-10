# Exit codes and the status sidecar

Exit-code semantics and the versioned machine-readable outcome written by
`--status-output`.

## Exit codes

| Exit | Meaning                                                                         |
| ---- | ------------------------------------------------------------------------------- |
| `0`  | `scoped-clean`, or a correct verdict with only filtered lower-priority findings |
| `1`  | Accepted findings, an incorrect provider verdict, or a failed review attempt    |
| `2`  | Incomplete scope/attribution, or a missing required finding                     |

`--expect-findings` changes exit codes as before; inspect `status` independently
of `exit_code`.

## Status sidecar

Use `--status-output /outside/repo/status.json` for a separate, versioned
machine-readable outcome. It preserves the existing exit codes and
`--json-output` validated-report format. Completed reviews report `scoped-clean`,
`findings`, `filtered`, `incorrect`, or `incomplete`; a launched reviewer that
fails or returns an invalid report reports `reviewer_unavailable` with exit 1.
A failed later pass never publishes a partial review report.

```json
{"schema_version":1,"status":"reviewer_unavailable","exit_code":1,"engine":"codex","report_produced":false,"reason":"engine_failed","reviewer_exit_code":124,"timed_out":true}
```

## Field semantics

`reason` is `engine_failed`, `invalid_report`, or `runtime_validation_failed`
for unavailable reviewers and null for completed reviews. The last reason means
Amp's post-launch isolation attestation or private-result validation refused
the result; it is not a transient-provider classification. These guards still
run before report acceptance and retain their existing failure diagnostics.

`reviewer_exit_code` is the last reviewer process's exit code when retained,
including zero for rejected output, otherwise null. `timed_out` identifies the
helper's deadline, not a reviewer that happens to exit 124. Completed envelopes
have `report_produced: true`; this means a validated final report exists, not
that its verdict is clean.

## Contents and lifecycle

The sidecar contains no provider logs, prompts, findings, or model identifiers.
Existing bounded, display-safe diagnostics remain on stderr; command-auth
diagnostic suppression remains in force. Use a fresh status path per invocation:
after argument and output-path validation, a previous sidecar is removed before
target selection. Dry runs, preflight/scan refusals, pre-launch isolation failures,
source mutations, interruptions, and output failures produce no new status.
Absence means no outcome was published, never a clean review. No retry policy is added.
