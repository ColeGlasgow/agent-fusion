# agent-fusion

A unified multi-agent orchestration framework that routes coding tasks between Claude Code and OpenAI Codex, choosing the right agent per task and coordinating shared tools, memory, and context.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Status: design phase](https://img.shields.io/badge/status-design%20phase-orange.svg)](#project-status)

---

## Project status

agent-fusion is in the **design phase**. This repository currently contains the project vision, target architecture, and planned structure. No runtime code is implemented yet. Issues, design discussion, and proposals are welcome — see [Contributing](#contributing).

The roadmap below tracks what lands first.

---

## Vision

Today's AI coding agents are powerful but siloed. Claude Code is strong at long-context reasoning, code review, and architectural judgment; OpenAI Codex (and GPT-class completion models) is strong at fast generation, scaffolding, and pattern completion. agent-fusion treats these as complementary tools and provides:

- A **task router** that picks the right agent for each unit of work based on task type, context size, and cost.
- A **shared tool layer** so both agents call the same shell, filesystem, and web tools.
- A **shared memory layer** so context survives handoffs between agents.
- **Parallel execution** for independent subtasks, with result merging.
- **Human-in-the-loop gates** for high-stakes or destructive actions.

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
                    └──┬────────┬──┘
                       │        │
              ┌────────▼──┐  ┌──▼─────────┐
              │  Claude   │  │  Codex     │
              │  wrapper  │  │  wrapper   │
              └────────┬──┘  └──┬─────────┘
                       │        │
                    ┌──▼────────▼──┐
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
│   ├── planner/         # Task decomposition and DAG
│   ├── tools/           # Shared tool layer (shell, fs, web, etc.)
│   ├── memory/          # Working, episodic, and vector memory
│   ├── hooks/           # Pre/post hooks (logging, cost, safety)
│   └── cli/             # CLI entrypoint
├── tests/               # Unit and integration tests
├── docs/                # Architecture and contributor docs
├── config/              # Default configuration files
├── examples/            # Example tasks and notebooks
├── .github/             # Issue templates, PR template, workflows
├── pyproject.toml
├── LICENSE
└── README.md
```

The `src/` layout is intentional: it keeps the importable package isolated from repo tooling and prevents accidental imports from the working directory during tests.

---

## Roadmap

Milestones are tracked as GitHub issues once filed. The current ordering:

1. Base agent interface and Claude/Codex wrappers
2. Rule-based task router with a small classifier fallback
3. Shared tool layer (shell, filesystem, web search)
4. Working and episodic memory
5. Hook system (logging, cost tracking, safety gates)
6. CLI entrypoint
7. Parallel execution and result merging
8. Vector memory and semantic recall
9. MCP-compatible tool definitions
10. Additional agents (Gemini, local models via Ollama)

---

## Routing intent

The router will combine deterministic rules with a lightweight classifier. Initial heuristics:

| Task type                       | Preferred agent | Reason                            |
| ------------------------------- | --------------- | --------------------------------- |
| Code review / security audit    | Claude          | Long context, deep reasoning      |
| Architecture decisions          | Claude          | Multi-factor reasoning            |
| Bug analysis with stack trace   | Claude          | Root-cause inference              |
| Large codebase understanding    | Claude          | Long-context window               |
| Rapid code generation           | Codex           | Optimized for completion          |
| Boilerplate and scaffolding     | Codex           | Fast and economical               |
| Unit test generation            | Codex           | Pattern completion                |
| Quick autocomplete-style edits  | Codex           | Low latency                       |

Rules will be overridable via configuration.

---

## Prior art and inspiration

agent-fusion draws on ideas from existing open-source agent projects:

- [alfredolopez80/multi-agent-ralph-loop](https://github.com/alfredolopez80/multi-agent-ralph-loop) — multi-agent orchestration patterns for Claude Code
- [AgenticGoKit/AgenticGoKit](https://github.com/AgenticGoKit/AgenticGoKit) — LLM-agnostic, event-driven agent patterns
- [unixzii/little-agent](https://github.com/unixzii/little-agent) — lightweight embedded agent framework
- [Protocol-Lattice/go-agent](https://github.com/Protocol-Lattice/go-agent) — graph-aware memory and orchestration

---

## Contributing

Issues and design discussion are the most useful contributions during the design phase. See [CONTRIBUTING.md](CONTRIBUTING.md) for how to file issues and propose changes, and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) for community expectations.

To report a security concern, see [SECURITY.md](SECURITY.md).

---

## License

MIT — see [LICENSE](LICENSE).
