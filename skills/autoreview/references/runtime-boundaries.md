# Runtime boundaries

Isolation, secret scanning, partitioning, and in-flight expectations.

## Isolation and secret scanning

The helper owns reviewer isolation, sanitized authentication, process cleanup,
Git scope, and structured result validation. Keep those controls enabled.
TruffleHog must scan the complete frozen input for partitioned reviews and each
exact outgoing pack before it is sent; missing or failed scanning stops the run.
Source-controlled ignore tags cannot suppress this gate. Scanner refusals never
echo input headings or finding payloads; remove credentials locally and rerun.
Never reproduce credentials in findings or work around an isolation failure.

## Trusted Git

Before repository detection or target selection, Git must pass `--version` within 10 seconds.
Failure exits `2` with an `incomplete` diagnostic naming the resolved executable (or the
unresolved selection); it never means `scoped-clean`. Set `AUTOREVIEW_GIT` to a trusted
external Git executable to override every helper-owned Git invocation. On macOS with a broken
selected Xcode, pass `DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer`. Only an
absolute, external `DEVELOPER_DIR` is kept in Git's sanitized environment; neither override
reaches the isolated reviewer. Git collection never runs checkout-controlled executables:
executable filter drivers are disabled for collection, and a diff that needs a converter to be
read is refused before review.

## Temporary directories on macOS

On macOS, reviewer tools cannot access the shared `/tmp` and `/var/tmp` trees
(including their `/private` aliases). Codex preflight rejects those temporary
roots before workspace, runtime, or authentication setup; unset a shared
`TMPDIR`/`TMP`/`TEMP` override to use macOS's private
temporary directory. Other engines and platforms retain their normal isolation.
Tools installed in shared scratch or requiring writes there will be denied too.

## Size and partitioning

Review files have no size/count cap and are never truncated. Large diffs and
datasets are partitioned automatically. Intact instructions and required mixed
source context must still fit the per-pass prompt budget. A failed pass does not
produce a partial clean verdict.

Each pass is an independent assignment, not a continuing conversation. Its private completion
field must confirm a finished assessment; a pass that defers to another pass leaves the overall
review incomplete (exit `2`).

## While a review runs

Do not edit inputs during a review: the helper verifies captured sources before
sending and publishing results. Long reviews are normal; advancing heartbeats
mean progress. Use `--stream-engine-output` for visibility, not extra reviewer
runs. `--dry-run` checks preparation and startup without contacting a reviewer.
