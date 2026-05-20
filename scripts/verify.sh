#!/usr/bin/env bash
# One-stop health check: run locally before pushing, and in CI on every PR.
# Gates: pytest, ruff lint, ruff format check, exporter smoke tests.

set -euo pipefail

cd "$(dirname "$0")/.."

PY=${PYTHON:-$(command -v python || command -v python3)}

echo "==> pytest"
"$PY" -m pytest tests/

echo "==> ruff check"
"$PY" -m ruff check src/ tests/

echo "==> ruff format --check"
"$PY" -m ruff format --check src/ tests/ --exclude src/agent_fusion/export/claude_code.py

echo "==> exporter smoke test"
tmpdir=$(mktemp -d)
trap 'rm -rf "$tmpdir"' EXIT

PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}" "$PY" -m agent_fusion.export.claude_code --output-dir "$tmpdir/claude-code"
for skill in code-generation python-backend frontend-react; do
    if [ ! -f "$tmpdir/claude-code/$skill/SKILL.md" ]; then
        echo "exporter smoke test failed: $tmpdir/claude-code/$skill/SKILL.md missing" >&2
        exit 1
    fi
done
echo "    ok: 3 expected Claude Code SKILL.md files written"

PYTHONPATH="src${PYTHONPATH:+:$PYTHONPATH}" "$PY" -m agent_fusion.export.cursor --output-dir "$tmpdir/cursor"
for skill in code-generation python-backend frontend-react; do
    if [ ! -f "$tmpdir/cursor/$skill.mdc" ]; then
        echo "exporter smoke test failed: $tmpdir/cursor/$skill.mdc missing" >&2
        exit 1
    fi
done
echo "    ok: 3 expected Cursor .mdc files written"

echo "==> all gates passed"
