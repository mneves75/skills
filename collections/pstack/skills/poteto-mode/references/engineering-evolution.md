# Evolving an existing system

Read this for a refactor, migration, or change to an established design.

Understand the current callers and behavior before minimizing the diff. Prefer
the smallest complete change to the correct owner. Remove dead paths and redundant
adapters when doing so is part of the requested change, rather than building
another layer around them. Preserve unrelated changes and behavior.

Measure complexity by the decisions a reader must trace and the mutable state
they must remember. A module earns its boundary by hiding a meaningful decision;
a pass-through wrapper with one caller often does not. There is no fixed allowed
number of files or layers: collapse only indirection that adds no useful contract.

When adding a requirement, reconsider the affected model as though that requirement
had existed originally. Prefer a direct representation over permanent flags for
temporary migration stages. Keep compatibility only when required by the task or
production-data safety. Migrate in-scope callers, verify them, and delete the old
internal API in the same completed unit when safe.

Sequence a larger migration as independently verifiable behavior changes. Keep
the destination explicit so intermediate scaffolding does not become the final
design. A forward data migration may be necessary even when obsolete code can be
removed. Do not broaden scope merely to improve neighboring code.
