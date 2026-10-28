# Map: adopt what tstack is worth

Type: wayfinder:map
Status: open

## Destination

Release 1.43.0 of this repository: the tstack skills worth having adapted into `skills/`, the
lessons tstack teaches folded into the existing skills where they change behavior, plus two
owner rules (proof, staging off after production) carried into every skill they touch. The
decisions are in [spec.md](spec.md).

## Notes

- Upstream: <https://github.com/t3dotgg/tstack> at `1085050f3baed1ac724caa4a8166145fb2ac88af`
  (2026-10-27), MIT, copyright Theo Browne.
- Execution is carried into this map: the owner said "implement all" on 2026-10-28, after
  confirming the destination. One branch (`feat/tstack-adoption`), stacked on PR #29 (1.42.0).
- Merging is the owner's. A merge to `main` is a Pages production deploy and needs the security
  gate on the exact commit.
- Domain: `GLOSSARY.md` (Council amended; Proof and Merge gate added).

## Decisions so far

- Destination interview (grilling, three rounds, 2026-10-28): the shared understanding in
  [spec.md](spec.md#decisions).
- Name collisions: none of `full-stop`, `takeover`, `modernize`, `leaving-pr-comments` or
  `babysit-pr` is installed under another skill on the owner's hosts or in `collections/pstack`
  (pstack has `babysit`, a different name), so the upstream names stay.
- pi as a council member: established on pi 1.4.0. `pi -p --no-session --tools read,grep,find,ls
  --no-extensions --no-skills --no-context-files --no-mcp --no-prompt-templates --no-approve
  @<prompt-file>` answered from the file and could not create a file; the same prompt without
  `--tools` created it (positive control). Reads are not confined.
- GitHub billing failures: see [spec.md](spec.md#github-billing-failures).
- Cloudflare staging idle proof: see [spec.md](spec.md#staging-off-after-production).

## Not yet specified

Nothing: the owner's "implement all" took every open item into the build.

## Out of scope

- `full-send` as a merging skill, `sol-loop` and `file-pr` as separate skills: their content is
  folded into `full-stop`, `autoreview`, `council` and `mneves-ship-deploy`.
- `collections/pstack` (vendored, never hand-edited) and third-party skills installed on the
  owner's hosts.
- Installing the new skills into the owner's agent folders: outside the repository, asked
  separately.
