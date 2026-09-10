# Codex route projection

How the helper projects a named Codex route from operator configuration, and the
contract that route must satisfy.

## Selecting a route

By default, Codex preserves only authentication settings from user configuration;
provider, profile, context and catalogue settings remain ignored. To project a
named route, select it explicitly through the existing config override:

```bash
"$AUTOREVIEW" --mode local --codex-config 'model_provider="review_api"'
```

The selector must match `model_provider` in the operator's external
`CODEX_HOME/config.toml`. It accepts one bare or simply quoted identifier;
provider definitions and other capabilities cannot be supplied through overrides.
Projection requires Python 3.11 or `tomli`; default auth-only operation retains
its existing fallback parser.

## Route requirements

The selected route must use `https://api.openai.com/v1` and command authentication
with an absolute external executable. Fixed arguments belong in that executable's
wrapper; omitted or empty `auth.args` are accepted. Omitted `wire_api` and
`requires_openai_auth` retain Codex's `responses` and `false` defaults. Optional
auth timing and context settings keep native defaults and semantics.

## Isolation and diagnostics

On POSIX, a private launcher restores the validated caller `HOME` only for the
selected authentication executable; the engine and reviewer tools retain their
isolated environment and filesystem access. Caller `HOME` must be an available
absolute directory with no repository-owned path or symlink provenance. Windows
keeps the native executable route. Command-auth runs suppress raw provider
diagnostics and report fixed failure categories, while retaining compact progress,
usage and assistant report streaming. An empty final report fails without exposing
captured stdout.

## Catalogue and validation

Catalogue and authentication working-directory paths resolve relative to the
operator config directory and must remain outside the reviewed repository.
A supplied catalogue is copied byte-for-byte into the private client runtime;
retries use the same route and catalogue snapshot. Dry runs check the same
ownership and route shape without executing authentication. Codex owns catalogue
validation, model access and context clamping. Other custom provider forms and
split context overrides are unsupported when projection is selected.
