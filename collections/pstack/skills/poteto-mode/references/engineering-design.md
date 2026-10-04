# Domain and interface design

Read this for a material decision about state, interfaces, or product behavior.

Start with the states the product permits, the transitions between them, and how
callers read and update the data. Choose a structure that makes the important
invariant explicit: a sum type for mutually exclusive states, a table for a closed
mapping, or a state machine when transition order matters. Avoid a framework or a
new layer when an existing domain type expresses the requirement.

Validate untrusted input once at the system boundary. Inside that boundary, rely
on the established types and framework guarantees. Keep adapter concerns out of
domain logic. Prefer exhaustive matching to a default branch that silently
accepts a newly added state; distinguish values with different meanings when
mixing them would produce a real bug.

Before introducing shared state, identify the owner and lifetime. Derive a value
from its source when practical instead of maintaining a second synchronized copy.
Keep changeable state as close as possible to the behavior that owns it.

Judge a proposed feature by what the user can accomplish and understand. Reuse
the product's existing interaction and visual conventions when they fit. For a
novel, consequential choice, compare a small number of meaningfully different
designs or test a focused prototype. An ordinary function boundary does not
require parallel architecture exploration.

Use the user's constraints to choose between viable options. Ask only when a
material product preference remains unresolved by the request and evidence.
