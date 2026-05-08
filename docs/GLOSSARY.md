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

The component that maps an incoming task to a specific agent. Combines deterministic rules (`config/routing_rules.yaml`) with a lightweight LLM-based classifier as a fallback. The router is stateless; it reads task metadata and returns an agent name.

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
