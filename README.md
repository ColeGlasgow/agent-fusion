# agent-fusion

A unified multi-agent orchestration framework that routes coding tasks between Claude Code and OpenAI Codex, choosing the right agent per task and coordinating shared tools, memory, and context.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Status: design phase](https://img.shields.io/badge/status-design%20phase-orange.svg)](#project-status)

---

## At a glance

| Field             | Value                                                           |
| ----------------- | --------------------------------------------------------------- |
| Purpose           | Route coding tasks between Claude Code and OpenAI Codex         |
| Stage             | Design phase (no runtime code yet)                              |
| Language          | Python 3.10+                                                    |
| Package layout    | `src/agent_fusion/` (planned)                                   |
| Entry point       | `agent_fusion.cli:main` (planned)                               |
| Build system      | `pyproject.toml` (planned)                                      |
| External services | Anthropic API (Claude), OpenAI API (Codex/GPT)                  |
| Required secrets  | `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`                           |
| Skill format      | Markdown + YAML frontmatter, see [docs/SKILL_AUTHORING.md](docs/SKILL_AUTHORING.md) |
| Agent guide       | [AGENTS.md](AGENTS.md)                                          |
| Glossary          | [docs/GLOSSARY.md](docs/GLOSSARY.md)                            |

## Project status

agent-fusion is in the **design phase**. This repository currently contains the project vision, target architecture, and planned structure. No runtime code is implemented yet. Issues, design discussion, and proposals are welcome — see [Contributing](#contributing).

The roadmap below tracks what lands first.

---

## Vision

Different LLMs are good at different jobs, and the same LLM does its best work when it's given the right rules, conventions, and tools for the task at hand. agent-fusion is built around two pillars:

1. **Routing** — for each task, pick the agent that's best at *this kind* of work (code review vs. scaffolding vs. refactor vs. data-platform SQL, etc.).
2. **Skills** — once the agent is chosen, run the task under a *skill profile* that supplies the rules, success criteria, and tool allowlist optimized for that domain. Skills are the difference between "the model wrote some code" and "the model wrote code that follows the conventions and quality bar this kind of work demands."

Around these two pillars sit the supporting components:

- A **shared tool layer** so every agent calls the same shell, filesystem, and web tools through a uniform interface.
- A **shared memory layer** so context survives handoffs between agents.
- **Parallel execution** for independent subtasks, with result merging.
- **Human-in-the-loop gates** for high-stakes or destructive actions.

Skills are content, not code: each skill is a Markdown file with YAML frontmatter (the same shape Anthropic uses for Claude Code skills). That makes skills easy to author, review, version, and share — and over time the skills directory becomes a curated library of best practices for different kinds of work.

---

## Planned architecture

```
                    ┌──────────────┐
                    │   Planner    │
                    │ (task graph) │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │    Router    │
                    │ rules + LLM  │
                    └──────┬───────┘
                           │  selects (agent, skill)
                           │
                    ┌──────▼───────┐
                    │    Skill     │  ◄── skills/*.md
                    │   profile    │      rules · tools
                    │              │      criteria · model
                    └──────┬───────┘
                           │  composes prompt + tool allowlist
                           │
                ┌──────────▼──────────┐
                │   Agent execution   │
                │  Claude · Codex ·   │
                │  (future agents)    │
                └──────────┬──────────┘
                           │
                    ┌──────▼───────┐
                    │  Tool layer  │
                    │ shell · fs · │
                    │   web · api  │
                    └──────┬───────┘
                           │
                    ┌──────▼───────┐
                    │    Memory    │
                    │ working ·    │
                    │ episodic ·   │
                    │  vector      │
                    └──────────────┘
```

---

## Planned project structure

This is the target layout. Directories will be created as their components land on the roadmap.

```
agent-fusion/
├── src/agent_fusion/
│   ├── agents/          # Agent wrappers (Claude, Codex, base class)
│   ├── router/          # Task classification and routing
│   ├── skills/          # Skill loader, registry, schema validation
│   ├── planner/         # Task decomposition and DAG
│   ├── tools/           # Shared tool layer (shell, fs, web, etc.)
│   ├── memory/          # Working, episodic, and vector memory
│   ├── hooks/           # Pre/post hooks (logging, cost, safety)
│   └── cli/             # CLI entrypoint
├── skills/              # Skill files (Markdown + YAML frontmatter) — content, not code
├── tests/               # Unit and integration tests
├── docs/                # Architecture and contributor docs
│   └── SKILL_AUTHORING.md
├── config/              # Default configuration files
├── examples/            # Example tasks and notebooks
├── .github/             # Issue templates, PR template, workflows
├── pyproject.toml
├── LICENSE
└── README.md
```

`skills/` is content, not code. Each file describes how a specific kind of work should be done; the framework loads and applies skills at runtime. See [docs/SKILL_AUTHORING.md](docs/SKILL_AUTHORING.md) for the format.

The `src/` layout is intentional: it keeps the importable package isolated from repo tooling and prevents accidental imports from the working directory during tests.

---

## Roadmap

Milestones are tracked as GitHub issues once filed. The current ordering:

1. Skill schema, loader, and registry (Markdown + YAML frontmatter)
2. Shared tool layer (shell, filesystem, web search) with read/write tier defaults
3. Base agent interface and Claude/Codex wrappers
4. Rule-based task router with a small classifier fallback — output is `(agent, skill)`
5. Starter skill library (PR review, frontend, backend, data-platform SQL, etc.)
6. Hook system (logging, cost tracking, safety gates)
7. CLI entrypoint
8. Working and episodic memory
9. Parallel execution and result merging
10. Vector memory and semantic recall
11. MCP-compatible tool definitions
12. Additional agents (Gemini, local models via Ollama)

---

## Routing intent

The router output is `(agent_or_model, skill)`. It combines deterministic rules with a lightweight classifier, and respects each skill's `preferred_models` field as a ranked hint when selecting the model.

Initial heuristics — these become routing rules in `config/routing_rules.yaml` and inform the matching skill's `preferred_models`:

| Task type                       | Preferred agent | Likely skill              | Reason                       |
| ------------------------------- | --------------- | ------------------------- | ---------------------------- |
| Code review / security audit    | Claude          | `pr-review`               | Long context, deep reasoning |
| Architecture decisions          | Claude          | `architecture`            | Multi-factor reasoning       |
| Bug analysis with stack trace   | Claude          | `bug-fix`                 | Root-cause inference         |
| Large codebase understanding    | Claude          | `codebase-survey`         | Long-context window          |
| Rapid code generation           | Codex           | `scaffolding`             | Optimized for completion     |
| Boilerplate and scaffolding     | Codex           | `scaffolding`             | Fast and economical          |
| Unit test generation            | Codex           | `unit-tests`              | Pattern completion           |
| Quick autocomplete-style edits  | Codex           | `quick-edit`              | Low latency                  |
| Frontend component work         | (skill-pinned)  | `frontend`                | Domain-specific conventions  |
| Data platform SQL / dbt         | (skill-pinned)  | `data-platform-sql`       | Domain-specific conventions  |

Rules are overridable via configuration. Skills may also pin a preferred model, which the router treats as a hint unless rules override.

---

## Prior art and inspiration

agent-fusion draws on ideas from existing open-source agent projects:

- [alfredolopez80/multi-agent-ralph-loop](https://github.com/alfredolopez80/multi-agent-ralph-loop) — multi-agent orchestration patterns for Claude Code
- [AgenticGoKit/AgenticGoKit](https://github.com/AgenticGoKit/AgenticGoKit) — LLM-agnostic, event-driven agent patterns
- [unixzii/little-agent](https://github.com/unixzii/little-agent) — lightweight embedded agent framework
- [Protocol-Lattice/go-agent](https://github.com/Protocol-Lattice/go-agent) — graph-aware memory and orchestration

---

## For AI coding agents

If you are an AI coding agent (Claude Code, Codex, Cursor, Aider, etc.) working on this repository, read [AGENTS.md](AGENTS.md) **before making changes** — Claude Code users get a short summary in [CLAUDE.md](CLAUDE.md), which is auto-loaded on session start and points back here. `AGENTS.md` defines:

- The repo's current stage and what kinds of changes are in scope.
- The package layout, entry points, and where new code belongs.
- Build, test, and lint commands once they are wired up.
- Conventions to follow (Python style, commit messages, no emojis in source or docs).
- Hard rules to never violate (no fabricated APIs, no speculative abstractions, no destructive git operations without explicit approval).

For domain terms used throughout the codebase (`router`, `planner`, `tool`, `hook`, `agent`, `memory tier`), see [docs/GLOSSARY.md](docs/GLOSSARY.md).

---

## Contributing

Issues and design discussion are the most useful contributions during the design phase. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to file issues and propose changes, and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community expectations.

To report a security concern, see [SECURITY.md](SECURITY.md).

---

## License

MIT — see [LICENSE](LICENSE).
