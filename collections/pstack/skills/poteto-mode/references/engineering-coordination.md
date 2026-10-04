# Coordination and task boundaries

Read this for concurrent actors, delegation, retries, or long-running work.

Separate ownership before serializing access: independent files, directories,
branches, or state keys avoid races more simply than a global lock. When actors
must share state, define the owner, atomic transition, and recovery behavior.
Use idempotent operations where retries or restarts are expected; do not assume
an interrupted worker left its owned files untouched.

Delegate only concrete independent work with disjoint ownership and observable
acceptance criteria when delegation is available and authorized. Give workers the
needed artifacts, constraints, and expected result. Inspect their actual changes
and evidence before accepting them. Keep the parent responsible for requirements,
integration, and the final claim.

Keep context focused on decisions and current evidence. Search before reading
large files, pass paths rather than copies when the worker can read them, and
return concise findings with locations. Avoid delegation merely to offload a
small lookup that the main session can finish directly.

Continue authorized reversible work without redundant permission checks. Ask
for missing input only when it materially changes the result or blocks safe
progress. Prior authorization persists for its named action, target, and scope.
Under an explicit full-autonomy grant, decide a call the grant covers, act on it,
and report it. For a call only the operator can make, apply a default and report
it with a full explanation, and say in plain words what the operator could tell you
to do instead. The operator answers in their own words; never give a shorthand
token to type back. Gates the operator named still need the operator. Publication, external messages, credential access, destructive actions, and scope
expansion follow the user's active authorization policy; a request to continue
working does not independently authorize any of them.
