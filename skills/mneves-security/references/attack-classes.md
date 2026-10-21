# Attack classes

Hunting prompts for a full audit or deploy gate. The twelve audit areas say *what* to cover;
these classes say *how a boundary breaks*. Select every class the inventory makes reachable,
and record the unselected ones with the inventory fact that excludes them. A class with no
candidate is a coverage note, not a pass: say what was traced.

Every class ends in the same test: name the lower-trust principal, its input or action, the
control that should stop it, the boundary crossed, the affected principal or resource and the
observed result. Without all six it is a hardening note or a needs-validation record.

## Core classes (every target)

**Injection, including the indirect kind.** Trace untrusted data to each interpreter: SQL/NoSQL,
shell, templates, HTML/DOM, file paths, redirects, deserializers, LDAP/XPath, log and CSV
consumers. Follow data stored safely and later read into a dangerous context by other code.
Inject through keys, field names, headers and metadata, not only values. Check secondary
systems: search indexes, caches, analytics, admin views, emails.

**Access control.** Look for a second path to the same state change that checks a weaker
permission; a body field that overrides what the permission meant to restrict; routes that
authenticate but do not authorize; batch, export, import and bulk endpoints that skip per-item
checks; and the same object reachable through two routes with different checks.

**Business logic.** Skip, repeat or reverse workflow steps; replay a completed flow; leave step
one applied after step two fails. Race check-then-act operations (double spend, double approve,
lost update). Feed negative, zero, huge, fractional and string-typed quantities. Test boundary
instants of expiry, schedules and rate windows, and clock or timezone differences between
components. Ask what the posture is when config is missing, a flag is off, a dependency is down
or a migration is half done.

**Feature abuse and side channels.** Export, backup and preview as exfiltration (data above the
caller's level, deleted or draft content, other tenants). Import and restore as injection
(overwrites, records that skip validation, writes into collections the caller cannot touch).
Search, filter and sort as an oracle for hidden records or fields. Enumeration through distinct
errors, status codes, sizes or timing in login, reset, invite and signup.

**Cryptography and secrets.** Predictable randomness for tokens and nonces, nonce or IV reuse,
unauthenticated encryption, non-constant-time secret comparison, missing MAC checks, and error
paths that fall back to no verification. Secrets in URLs, logs, errors or client bundles.

## Domain classes (select from the inventory)

**HTTP protocol, sessions and identity** (web apps, APIs, proxies, CDNs, custom parsers).
Request framing that two hops parse differently (Content-Length versus Transfer-Encoding,
duplicate or folded headers, HTTP/2 downgrade); web cache poisoning through unkeyed inputs and
cache deception that stores a private response under a public key; host-header trust in reset
links. Session fixation, missing rotation on privilege change, revocation that leaves other
sessions alive. OAuth/OIDC: state and PKCE binding, redirect-URI matching, mix-up across
providers, ID token accepted where an access token was meant. Account linking or recovery that
lets an unverified email, phone or federated identity take over an existing account; MFA steps
that can be skipped or reused; passkey and API-key scoping and rotation.

**Client side and browser** (SPAs, extensions, webviews, service workers). DOM sinks fed by
URL, storage or messages; `message` handlers that act on data without checking `event.origin`, and `postMessage`
calls that send confidential data with target origin `*`;
prototype pollution reaching a gadget; DOM clobbering; service-worker scope and cache poisoning
that outlives logout; tokens in storage readable by any script; cross-site leaks through frame
counts, timing or error events; clickjacking of consequential actions; open redirects chained
into token theft.

**Supply chain, CI and release** (dependencies, workflows, signing, updates, plugins).
Workflows that run untrusted pull-request code with secrets or write tokens
(`pull_request_target`, `workflow_run`), script injection through issue, branch or title text,
unpinned third-party actions, cache and artifact poisoning between jobs, dependency or registry
confusion, install scripts, lockfiles that do not bind what is built, release and update paths
that skip signature or provenance checks, plugin or extension loading from writable locations.

**Cloud and deployment** (IAM, infrastructure as code, containers, serverless and edge).
Wildcard or confused-deputy IAM grants; workload identity usable from outside its workload;
metadata-service reachability through SSRF; public buckets, snapshots and queues; containers
running privileged or with host mounts; secrets baked into images or build logs; environment
bindings that differ between staging and production; ingress that exposes admin or debug ports;
event triggers that accept forged provider events.

**Protocols, RPC and messaging** (gRPC, GraphQL, queues, brokers, webhooks, streams).
Schema or framing differences between producer and consumer; unknown fields that reach
storage; RPC methods reachable without the gateway's auth; caller identity taken from message
content instead of the transport; topics and queues shared across tenants; replay, reordering
and duplicate delivery against non-idempotent handlers; GraphQL depth, alias and batching
amplification; webhook signature checked on a re-serialized body.

**Resource exhaustion and spend** (shared workers, quotas, paid APIs). Small inputs that cause
large work: regex backtracking, decompression, nested parsing, fan-out, unbounded pagination.
Accumulation that never expires: sessions, uploads, queue entries, retries. Quotas keyed on a
value the caller controls. Failure paths that retry forever, hold locks or drop the audit trail.
Operator spend (AI tokens, SMS, email, egress) a caller can drive without a cap.

**Data isolation and lifecycle** (multi-tenant stores, caches, search, backups). Tenant keys
missing from cache, search, vector or analytics keys; signed or shareable links that outlive
the share; derived copies (thumbnails, exports, embeddings, logs) that keep data after deletion;
restore and migration paths that re-enable deleted users or cross tenants; deletion that leaves
backups, replicas or third-party copies without a recorded retention.

**Desktop, mobile and local IPC** (native apps, deep links, helpers, daemons). Deep links and
custom schemes that reach privileged actions without confirmation; webview bridges exposed to
remote content; exported components, intents, XPC services, Unix sockets or D-Bus methods that
trust any local caller; privileged helpers that act on caller-supplied paths (symlink races);
sensitive state left in backups, screenshots, clipboard or logs.

**Native code and memory safety** (C, C++, unsafe Rust, FFI, parsers, decoders). Length and
integer arithmetic before allocation or copy; signed and unsigned mixing; use after free and
double free across error paths; data races on shared state; FFI boundaries that drop ownership
or length; parsers fed attacker-controlled offsets. Confirm with a sanitizer build of a minimal
fixture in the sandbox; a crash alone is not a security result until the boundary is named.

**AI, agents and tools** (beyond the conditional section in the audit areas). Retrieved pages,
files, tool output and memory treated as instructions; tool calls whose arguments the model
chooses for an action the user did not authorize; MCP servers or sub-agents trusted with the
caller's full credentials; memory written by one user and read by another; model output
rendered as HTML, SQL or shell. A prompt is not a control; the server-side check is.

## Coverage critic

After hunting, a fresh agent reads the inventory, the selected classes and the candidate list
and answers one question: which reachable surface and class pair got no trace? Accepted gaps
become hunting work in this run or a named coverage gap in the report. Stop when a critic pass
adds nothing, or when the agreed budget ends; record which.

One pass finds only part of what repeated passes find, so a single run reports its coverage as
partial. A later run reads the earlier report: a disproved claim stays suppressed only while its
source and the assumptions its disproof rested on (provider policy, identity, dependency
versions, topology) are unchanged; any change makes it current work again. Public buckets,
unpinned actions and unknown fields are leads to trace, not findings by themselves.
