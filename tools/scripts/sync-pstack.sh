#!/usr/bin/env bash
# Generate collections/pstack from the commits pinned in <dest>/sources.json.
#
#   tools/scripts/sync-pstack.sh <port-repo> <official-repo> [dest]
#
# <port-repo> is a clone of the Claude Code port (michael-denyer/pstack-claude) and
# <official-repo> a clone of cursor/plugins; each must contain its pinned commit.
# The implementation and its guarantees are documented in sync-pstack.py.
#
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: 2026 Marcus Neves
set -euo pipefail
exec python3 -I "$(dirname "$0")/sync-pstack.py" "$@"
