# Agent skills

Portable procedures and supporting resources installed into coding agents.

## Language

**Security finding**: A candidate weakness that names the lower-trust principal, its input,
the control, the crossed boundary, the affected resource and the observed result. Its
disposition is confirmed (carries a severity), needs-validation (one external fact missing;
no severity) or disproved. An unconfirmed suspicion is not a verified defect.

**Disposition**: Whether a security finding is true: confirmed, needs-validation or
disproved. Distinct from a gate's verdict (pass, block, waived) and from a fix state.

**Evidence scope**: The environment and surface a check actually establishes, such as
source configuration, local behavior, deployed behavior or an owner's dated attestation.

**Independent acceptance**: A fresh assessor checks frozen criteria against actual
artifacts. It establishes a scoped verdict, not universal security or launch approval.

**Renderer skill**: A procedure that guides an agent to build a repeatable document
renderer within the user's project. It is not itself a universal conversion service.

**Source document**: The authoritative Markdown content from which requested deliverables
are produced. Rendering preserves its meaning, facts and structure.

**Rendered deliverable**: An HTML, editable DOCX or PDF document generated from the source
document and the project's presentation rules.

**Readiness control**: A falsifiable statement about one way a launch can fail customers,
with its tier, applicability, verification and minimum evidence scope.

**Readiness ledger**: The tracked, canonical record of every readiness control's status and
evidence for one deployable unit.

**Readiness gate**: An assessment of a candidate commit for one target, staging or
production, ending in a ready or not-ready verdict.

**Readiness record**: The ignored file a binding gate run writes for one unit, target and
commit. A release script checks it; it is a precondition, not an authorization.

**Waiver**: An owner's dated acceptance of a named gap. The underlying status stays visible
and returns when the waiver expires.
