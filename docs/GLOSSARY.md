# Glossary

Canonical terms used across agent-fusion. Use these names exactly in code, docs, commits, and discussion. If you need a concept that isn't here, propose it in a design issue before introducing a new term.

---

## Agent

A wrapper around an LLM provider (Claude, Codex, future providers) that conforms to a single interface. Every agent exposes:

```python
async def run(self, task: str, context: dict) -> AgentResult: ...
```

Agents do not decide *whether* to handle a task — that's the router's job. Agents only execute.

Class names end with `Agent`: `ClaudeAgent`, `CodexAgent`, `BaseAgent`.

## AgentResult

The structured value returned by `Agent.run`. Carries the output, the agent name that produced it, token/cost accounting, and any tool invocations made during the run.

## Router

The component that maps an incoming task to a specific agent **and** a skill profile. Combines deterministic rules (`config/routing_rules.yaml`) with a lightweight LLM-based classifier as a fallback. The router is stateless; it reads task metadata and returns a `RouteDecision(agent_or_model, skill)`. When a chosen skill declares `preferred_models`, the router treats that ranked list as a hint and uses the highest-priority available model unless a rule overrides it.

## Skill

A bundle of rules, success criteria, tool allowlist, and optional model preferences that defines *how* a particular kind of work should be done (e.g. PR review, frontend component work, data-platform SQL). Skills are authored as Markdown files with YAML frontmatter — same shape as Anthropic's Claude Code skills — and live under `skills/` at the repo root. Skills are content, not code.

When the router picks a skill for a task, the agent runs with the skill's body composed into the system prompt and the skill's tool allowlist applied.

## Skill registry

The runtime index of available skills. Loaded by `src/agent_fusion/skills/` from the `skills/` directory plus any user-configured additional skill directories. The registry validates frontmatter against the schema, resolves name conflicts, and exposes lookup by name or capability tag.

## Tool tier

The default access level a skill has to a given tool. Tools are grouped into tiers:

- **Read tier** — filesystem read, grep/glob, web search, shell read-only commands. Available to every skill by default; the model needs these to gather context.
- **Write tier** — filesystem write, shell exec, network POST, git mutations, code execution. Off by default. A skill must list specific write-tier tools in `allowed_tools` to use them.

Tool tiers exist so that skills don't have to redeclare baseline read access while destructive capabilities still require explicit opt-in. See `src/agent_fusion/tools/` for the registry and tier definitions.

## Planner

The component that decomposes a high-level task into a DAG of subtasks. Each subtask becomes a separate router call. Use the planner only when a task is genuinely multi-step; for atomic tasks, the router runs directly.

## Task graph

The DAG output of the planner. Nodes are subtasks, edges are dependencies. Independent nodes may be dispatched in parallel.

## Tool

A capability that any agent can call (shell, filesystem, web search, code execution, API call). Tools live in `src/agent_fusion/tools/` and are registered through the tool registry. Tools have a stable, agent-agnostic interface so the same tool works across providers.

Class names end with `Tool`: `ShellTool`, `FilesystemTool`, `WebSearchTool`.

## Tool registry

The single source of truth for available tools. Both agents resolve tool calls through the registry rather than holding tool references directly.

## Hook

A pre- or post-execution callback wrapped around agent runs. Hooks handle cross-cutting concerns: structured logging, token/cost tracking, output quality gates, safety policy enforcement. Hooks may abort a run (e.g. budget exceeded, safety violation) but should not silently mutate task results.

## Memory tier

agent-fusion plans three tiers of memory:

- **Working memory** — in-conversation, short-lived, scoped to the current task or session.
- **Episodic memory** — durable record of past tasks and their outcomes, queried by recent-history lookup.
- **Vector memory** — semantic recall over prior work via embeddings, used for retrieving distant-but-relevant context.

Use the term "memory tier" rather than "memory layer" or "memory store" for the high-level concept.

## Handoff

Passing partial state from one agent to another mid-task — for example, Claude does the design, Codex implements, Claude reviews. The orchestrator preserves working memory and tool state across the handoff so the receiving agent doesn't restart from zero.

## Parallel execution

Running independent subtasks on different agents simultaneously and merging their results. Used when the planner produces siblings in the task graph that share no data dependency.

## Human-in-the-loop gate

A safety hook that pauses execution and requires explicit human approval before continuing. Triggered by destructive actions, budget thresholds, or policy rules. Distinct from a quality gate, which can fail-fast without human intervention.

## Routing rule

A declarative override in `config/routing_rules.yaml` that pins a task pattern to a specific agent. Rules win over the classifier; if no rule matches, the classifier decides.

## Agent profile

A capability description in `config/agent_profiles.yaml`. The router uses profiles to know what each agent claims to handle (e.g. `["code-review", "long-context-reasoning"]`) when scoring candidates.

## Cost tracking

The sum of API charges incurred by agent runs in a session, attributed per agent and per task. Surfaced through the cost-tracking hook and capped by configured budgets.

## MCP

Model Context Protocol. agent-fusion plans to expose its tool layer in MCP-compatible form so external clients can use the same tools. See https://modelcontextprotocol.io for the specification.
