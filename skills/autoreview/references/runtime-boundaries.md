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

## While a review runs

Do not edit inputs during a review: the helper verifies captured sources before
sending and publishing results. Long reviews are normal; advancing heartbeats
mean progress. Use `--stream-engine-output` for visibility, not extra reviewer
runs. `--dry-run` checks preparation and startup without contacting a reviewer.
