# agent-fusion 🤖⚡

> A unified multi-agent orchestration framework that intelligently routes tasks between **Claude Code** and **OpenAI Codex**, combining the best of both for efficient, context-aware AI coding workflows.
>
> [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
> [![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
> [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)
>
> ---
>
> ## 🧠 Vision
>
> Modern AI coding agents are powerful but siloed — Claude Code excels at deep reasoning, long-context understanding, and nuanced code review, while OpenAI Codex (and GPT-4o with code interpreter) shines at rapid code generation, completion, and scripting. **agent-fusion** bridges this gap by acting as an intelligent router and orchestrator that:
>
> - Selects the **right agent for the right task** based on context, complexity, and cost
> - - Enables **parallel agent execution** for independent subtasks
>   - - Provides a **unified tool interface** so both agents share the same tools (shell, filesystem, browser, APIs)
>     - - Maintains **shared memory and context** across agent handoffs
>       - - Supports **human-in-the-loop** checkpoints for high-stakes decisions
>        
>         - ---
>
> ## 🏗️ Architecture
>
> ```
> ┌─────────────────────────────────────────────────────┐
> │                   agent-fusion                       │
> │                                                     │
> │  ┌─────────────┐     ┌──────────────────────────┐  │
> │  │   Planner   │────▶│     Task Router          │  │
> │  │  (LLM-based)│     │  (rules + LLM classify)  │  │
> │  └─────────────┘     └──────────┬───────────────┘  │
> │                                 │                    │
> │              ┌──────────────────┼──────────────┐    │
> │              ▼                  ▼              ▼    │
> │  ┌──────────────────┐  ┌──────────────┐  ┌──────┐  │
> │  │  Claude Code     │  │ OpenAI Codex │  │ Both │  │
> │  │  Agent Wrapper   │  │ Agent Wrapper│  │(par.)│  │
> │  └────────┬─────────┘  └──────┬───────┘  └──┬───┘  │
> │           │                   │             │       │
> │           └───────────────────┴─────────────┘       │
> │                         │                           │
> │              ┌──────────▼──────────┐                │
> │              │   Shared Tool Layer │                │
> │              │  shell | files | api│                │
> │              └──────────┬──────────┘                │
> │                         │                           │
> │              ┌──────────▼──────────┐                │
> │              │   Memory & Context  │                │
> │              │  (vector + episodic)│                │
> │              └─────────────────────┘                │
> └─────────────────────────────────────────────────────┘
> ```
>
> ---
>
> ## ✨ Key Features
>
> - **Intelligent Task Routing** — Automatically classifies tasks and routes to the optimal agent (Claude for reasoning/review, Codex for generation/completion)
> - - **Dual-Agent Orchestration** — Run Claude Code and Codex in parallel on independent subtasks, then merge results
>   - - **Shared Tool Layer** — Both agents access the same tools: shell execution, file I/O, web search, API calls, and more
>     - - **4-Layer Memory System** — Working memory, episodic memory, semantic (vector) memory, and learned patterns
>       - - **Hook System** — Pre/post hooks for logging, safety gates, cost tracking, and quality checks
>         - - **Context-Aware Handoffs** — Seamless context passing between agents mid-task
>           - - **Cost & Token Optimization** — Route cheap tasks to the more economical agent automatically
>             - - **Human-in-the-Loop Gates** — Define quality or safety thresholds that require human approval before proceeding
>               - - **MCP Compatible** — Works with the Model Context Protocol for standardized tool definitions
>                
>                 - ---
>
> ## 📦 Project Structure
>
> ```
> agent-fusion/
> ├── agents/
> │   ├── claude_agent.py        # Claude Code wrapper & API client
> │   ├── codex_agent.py         # OpenAI Codex / GPT-4o wrapper
> │   ├── base_agent.py          # Abstract base class for all agents
> │   └── parallel_runner.py     # Parallel agent execution engine
> ├── router/
> │   ├── router.py              # Task classification & routing logic
> │   ├── rules.py               # Rule-based routing overrides
> │   └── classifier.py          # LLM-based task classifier
> ├── tools/
> │   ├── shell.py               # Secure shell execution tool
> │   ├── filesystem.py          # File read/write/search tool
> │   ├── web_search.py          # Web search integration
> │   ├── code_executor.py       # Sandboxed code execution
> │   └── tool_registry.py       # Tool registration & discovery
> ├── memory/
> │   ├── working_memory.py      # Short-term context store
> │   ├── episodic_memory.py     # Task history & outcomes
> │   ├── vector_store.py        # Semantic search over past work
> │   └── memory_manager.py      # Unified memory interface
> ├── hooks/
> │   ├── logging_hook.py        # Structured logging
> │   ├── cost_tracker.py        # Token & API cost tracking
> │   ├── quality_gate.py        # Output quality validation
> │   └── safety_gate.py        # Safety & policy enforcement
> ├── planner/
> │   ├── planner.py             # High-level task decomposition
> │   └── task_graph.py          # DAG-based task dependency management
> ├── config/
> │   ├── config.yaml            # Main configuration file
> │   ├── routing_rules.yaml     # Routing rules and cost thresholds
> │   └── agent_profiles.yaml    # Per-agent capability profiles
> ├── cli/
> │   └── main.py                # CLI entrypoint
> ├── tests/
> │   ├── test_router.py
> │   ├── test_agents.py
> │   └── test_tools.py
> ├── docs/
> │   ├── architecture.md
> │   ├── routing.md
> │   └── adding_agents.md
> ├── .env.example
> ├── pyproject.toml
> └── README.md
> ```
>
> ---
>
> ## 🚀 Quick Start
>
> ### Prerequisites
>
> - Python 3.10+
> - - An Anthropic API key (for Claude)
>   - - An OpenAI API key (for Codex/GPT-4o)
>    
>     - ### Installation
>    
>     - ```bash
>       git clone https://github.com/ColeGlasgow/agent-fusion.git
>       cd agent-fusion
>       python -m venv .venv
>       source .venv/bin/activate  # Windows: .venv\Scripts\activate
>       pip install -e ".[dev]"
>       ```
>
> ### Configuration
>
> ```bash
> cp .env.example .env
> # Edit .env with your API keys:
> # ANTHROPIC_API_KEY=sk-ant-...
> # OPENAI_API_KEY=sk-...
> ```
>
> ### Basic Usage
>
> ```python
> from agent_fusion import FusionOrchestrator
>
> orchestrator = FusionOrchestrator()
>
> # The router automatically picks the best agent
> result = await orchestrator.run(
>     task="Refactor this Python module to use async/await and add type hints",
>     context={"file": "src/legacy_module.py"}
> )
>
> print(result.output)
> print(f"Agent used: {result.agent}")
> print(f"Tokens used: {result.token_count}")
> ```
>
> ### CLI Usage
>
> ```bash
> # Run a single task (auto-route)
> agent-fusion run "Write a FastAPI endpoint for user authentication"
>
> # Force a specific agent
> agent-fusion run --agent claude "Review this PR for security vulnerabilities"
> agent-fusion run --agent codex "Complete the docstrings in utils.py"
>
> # Run in parallel mode on a complex task
> agent-fusion run --parallel "Build and test a REST API for a todo app"
> ```
>
> ---
>
> ## 🔀 Routing Logic
>
> The router uses a combination of rule-based and LLM-based classification:
>
> | Task Type | Preferred Agent | Reason |
> |-----------|----------------|--------|
> | Code review / security audit | Claude | Deep reasoning, long context |
> | Rapid code generation | Codex | Optimized for code completion |
> | Architecture decisions | Claude | Nuanced multi-factor reasoning |
> | Boilerplate / scaffolding | Codex | Fast, cost-effective |
> | Bug analysis with stack trace | Claude | Root cause reasoning |
> | Unit test generation | Codex | Pattern completion |
> | Large codebase understanding | Claude | 200k token context |
> | Quick autocomplete-style tasks | Codex | Low latency |
>
> You can override routing with rules in `config/routing_rules.yaml`.
>
> ---
>
> ## 🔌 Open Source Foundations
>
> agent-fusion builds on and draws inspiration from:
>
> - **[alfredolopez80/multi-agent-ralph-loop](https://github.com/alfredolopez80/multi-agent-ralph-loop)** — Multi-agent orchestration patterns for Claude Code
> - - **[AgenticGoKit/AgenticGoKit](https://github.com/AgenticGoKit/AgenticGoKit)** — LLM-agnostic, event-driven agent patterns
>   - - **[swarmclaw/swarmclaw](https://github.com/swarmclawai/swarmclaw)** — Self-hosted agent runtime with MCP tools
>     - - **[unixzii/little-agent](https://github.com/unixzii/little-agent)** — Lightweight embedded agent framework
>       - - **[Protocol-Lattice/go-agent](https://github.com/Protocol-Lattice/go-agent)** — Graph-aware memory and multi-agent orchestration
>        
>         - ---
>
> ## 🧩 Adding a New Agent
>
> Subclass `BaseAgent` and implement the required interface:
>
> ```python
> from agent_fusion.agents.base_agent import BaseAgent, AgentResult
>
> class MyCustomAgent(BaseAgent):
>     name = "my-agent"
>     capabilities = ["code-generation", "text-summarization"]
>
>     async def run(self, task: str, context: dict) -> AgentResult:
>         # Call your LLM API here
>         response = await self.call_api(task, context)
>         return AgentResult(output=response, agent=self.name)
> ```
>
> Register it in `config/agent_profiles.yaml` and the router will automatically consider it.
>
> ---
>
> ## 🛡️ Safety & Cost Controls
>
> - **Budget limits**: Set per-task and per-session token/cost caps in `config.yaml`
> - - **Safety gates**: Pre-defined hooks block destructive operations without human approval
>   - - **Audit log**: Every agent action is logged with full context for review
>     - - **Sandboxed execution**: Code execution tools run in isolated environments
>      
>       - ---
>
> ## 🗺️ Roadmap
>
> - [ ] Core router and dual-agent wrappers (Claude + Codex)
> - [ ] - [ ] Shared tool layer (shell, filesystem, web search)
> - [ ] - [ ] 4-layer memory system
> - [ ] - [ ] Hook system (logging, cost, quality, safety)
> - [ ] - [ ] CLI entrypoint
> - [ ] - [ ] MCP server compatibility
> - [ ] - [ ] Web UI dashboard for session monitoring
> - [ ] - [ ] Support for additional agents (Gemini, local LLMs via Ollama)
> - [ ] - [ ] GitHub Actions integration for automated code review workflows
> - [ ] - [ ] Plugin marketplace for community tools
>
> - [ ] ---
>
> - [ ] ## 🤝 Contributing
>
> - [ ] Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on submitting issues and pull requests.
>
> - [ ] ---
>
> - [ ] ## 📄 License
>
> - [ ] This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.
