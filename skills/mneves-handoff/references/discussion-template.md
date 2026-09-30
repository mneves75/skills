# Discussion-first handoff template

Use for a fresh receiving agent. Fill known facts; omit empty optional context instead of
inventing requirements. Keep the prompt standalone and preserve an explicit discussion-only
boundary. Include an existing authorized implementation scope only when the caller grants it.

```text
Task: Independently assess <problem or proposed change> in <repository/product>.
Context: <trigger, checked current state, portable issue/PR/branch/symbol anchors>.
Acceptance: <expected decision or observable behavior and required evidence>.
Constraints: <ownership, non-goals, behavior to preserve, known uncertainty>.
Delivery: Find the repository and read its instructions. Inspect affected code, callers,
tests, and relevant live issue/CI state. Assess whether the problem is real, already solved,
or better addressed another way. Start with findings and a recommendation; propose the
smallest supported next step. Preserve a discussion-only request. If implementation is
already authorized, complete that scope and report exact verification and remaining gaps.
Target: <discussion, local patch, or explicitly authorized external action/destination>.
Do not push, merge, close or label issues/PRs, or post comments beyond that authority.
```

Use portable repository identity and search anchors, not filesystem paths, unless requested.
Carry outcome, acceptance, authority, source identity, completed evidence, exact blockers,
and remaining work. Link large evidence when accessible; do not duplicate a full transcript.
