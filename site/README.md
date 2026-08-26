# site/ (GitHub Pages)

Published at https://mneves75.github.io/skills/ by `.github/workflows/static.yml` on every push
that touches this directory.

- `index.html`: landing page. Hand-written, self-contained; edit directly.
- `howto.html`: rendered from [HOWTO.md](../HOWTO.md) by `tools/scripts/build-howto.sh`. Do not edit by hand.
- `fastapi.html`: sample report from the readiness-check tool (FastAPI `9a8a13f`, 2026-08-26, static checks).

Regenerate the sample report from a FastAPI checkout:

```bash
bun --bun /path/to/skills/tools/readiness-check.ts --format=html --skip-tests --skip-build --output=/path/to/skills/site/fastapi.html
```
