# AGENTS.md

Instructions for AI coding agents (Claude Code, OpenAI Codex, Cursor, Aider, and similar) working on this repository. Human contributors should read [CONTRIBUTING.md](CONTRIBUTING.md); the rules here are the agent-readable counterpart.

This file follows the convention used by Claude Code (`CLAUDE.md`) and the broader `AGENTS.md` ecosystem. Both names work — this repo uses `AGENTS.md` as the canonical source and treats `CLAUDE.md` (if present) as an alias.

---

## Repository identity

- **Name:** agent-fusion
- **Purpose:** Route coding tasks between Claude Code and OpenAI Codex via a shared tool, memory, and orchestration layer.
- **Stage:** Design phase. No runtime code exists yet. Most agent work right now is documentation, design proposals, and scaffolding the first components on the roadmap.
- **Language:** Python 3.10+
- **License:** MIT

If a request asks you to implement something not on the roadmap or not yet designed in an issue, **stop and ask the human** before writing code. Do not improvise architecture in this repo.

---

## Where things go

| Concern                              | Location                              |
| ------------------------------------ | ------------------------------------- |
| Agent wrappers (Claude, Codex, base) | `src/agent_fusion/agents/`            |
| Task router and classifier           | `src/agent_fusion/router/`            |
| Task decomposition / DAG             | `src/agent_fusion/planner/`           |
| Shared tools (shell, fs, web, api)   | `src/agent_fusion/tools/`             |
| Memory tiers                         | `src/agent_fusion/memory/`            |
| Hooks (logging, cost, safety, etc.)  | `src/agent_fusion/hooks/`             |
| CLI entrypoint                       | `src/agent_fusion/cli/`               |
| Default config                       | `config/`                             |
| Tests (mirror `src/` layout)         | `tests/`                              |
| Architecture / design docs           | `docs/`                               |
| Domain glossary                      | `docs/GLOSSARY.md`                    |
| Issue and PR templates               | `.github/`                            |

When introducing a new module, place it in the directory that matches the planned architecture rather than inventing a new top-level folder. If nothing fits, open a design issue first.

---

## Build, test, lint

These commands are reserved targets. They will be wired up as the project lands. Until they exist, prefer dry-run and document-only changes.

| Action            | Command (planned)        |
| ----------------- | ------------------------ |
| Install (dev)     | `pip install -e ".[dev]"` |
| Run tests         | `pytest`                 |
| Type-check        | `mypy src`               |
| Lint              | `ruff check .`           |
| Format            | `ruff format .`          |
| Run the CLI       | `agent-fusion --help`    |

If you add code, also add (or extend) the relevant command in `pyproject.toml` and update this table in the same PR.

---

## Hard rules

These are non-negotiable. Violations should be reverted before merge.

1. **Do not fabricate APIs, file paths, or imports.** If a module isn't present, don't reference it as if it were. Check before citing.
2. **Do not invent architecture.** If the change isn't covered by an issue tagged `design` or already-merged design doc, ask before implementing.
3. **No emojis** in source code, comments, commit messages, PR descriptions, README, or any project documentation.
4. **No speculative abstractions.** A single concrete implementation beats a premature interface. Three similar lines is better than a generic helper for two callers.
5. **No silent dependency additions.** New runtime or dev dependencies require an explicit note in the PR description with a justification.
6. **No secrets in code, tests, fixtures, or commits.** Use environment variables. The expected vars are `ANTHROPIC_API_KEY` and `OPENAI_API_KEY`.
7. **No destructive git operations** (force push to `main`, `git reset --hard` on shared branches, deleting branches you didn't create) without explicit human approval.
8. **No bypassing safety.** Do not use `--no-verify`, `--no-gpg-sign`, or similar flags to skip hooks unless the human explicitly tells you to.
9. **Match existing style.** If linters or formatters are configured, run them and accept their output.
10. **Surface uncertainty.** When you are not sure what the human wants, say so and ask. Don't guess into a 200-line PR.

---

## Style and conventions

- **Python:** target 3.10+, prefer standard library where reasonable, use type hints on public APIs, prefer `dataclasses` or `pydantic` (TBD) over loose dicts for structured data.
- **Naming:** modules and packages are `snake_case`; classes are `PascalCase`; constants are `UPPER_SNAKE`. Agent classes end with `Agent` (e.g. `ClaudeAgent`). Tools end with `Tool` (e.g. `ShellTool`).
- **Docstrings:** one short line for obvious functions; full docstrings for public interfaces. Don't restate the signature in prose.
- **Comments:** write comments that explain *why*, not *what*. Don't reference tickets, authors, or task context in source — that belongs in the commit or PR description.
- **Tests:** new code requires tests. Mirror the `src/agent_fusion/<area>/foo.py` layout under `tests/<area>/test_foo.py`. Prefer fast unit tests; mark slow or network-using tests with `@pytest.mark.integration`.
- **Commits:** present-tense imperative subject under 72 chars (`add base agent interface`). Body explains the *why*. One logical change per commit.
- **PRs:** scoped, with a clear summary, motivation, and test plan. Use the PR template.

---

## Domain vocabulary

Use these terms consistently. Definitions live in [docs/GLOSSARY.md](docs/GLOSSARY.md). Brief reference:

- **Agent** — a wrapper around an LLM provider that exposes a uniform `run(task, context) -> AgentResult` interface.
- **Router** — picks an agent for a given task using rules plus an optional classifier.
- **Planner** — decomposes a high-level task into a DAG of subtasks for the router to dispatch.
- **Tool** — a capability shared across agents (shell, filesystem, web search, API call).
- **Hook** — a pre/post callback applied around agent invocations (logging, cost tracking, safety gates, quality checks).
- **Memory tier** — working (in-conversation), episodic (past task outcomes), or vector (semantic recall).
- **Handoff** — passing partial state from one agent to another mid-task without losing context.

If you find yourself inventing a synonym for any of these, stop and use the canonical term.

---

## What "in scope" means right now

Because the repo is in design phase, in-scope work is roughly:

1. Documentation and design proposals.
2. The first roadmap milestone: base agent interface and Claude/Codex wrappers.
3. Repo plumbing: `pyproject.toml`, lint/format/test config, CI workflows, release tooling.

Out of scope without explicit approval:

- Adding new agents beyond Claude and Codex.
- Vector memory or RAG infrastructure.
- Web UI or dashboard work.
- Any third-party SaaS integration.

When in doubt, open an issue using the **Design proposal** template before writing code.

---

## When you finish a change

- Run the build/test/lint commands from the table above (or note in the PR which ones are not yet available).
- Update this file if you changed conventions, layout, or commands.
- Update [docs/GLOSSARY.md](docs/GLOSSARY.md) if you introduced or renamed a domain term.
- Open the PR with the template's summary, motivation, and test plan filled in.

---

## Aliases

This file's content also applies if your tooling looks for any of:

- `CLAUDE.md`
- `.cursorrules`
- `.aider.conf.yml` instructions
- `AGENT.md` (singular)

Treat `AGENTS.md` as the source of truth and keep aliases (if any) thin pointers back to this file.
