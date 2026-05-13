# Routing design

This document specifies how the router decides which AI agent runs a task and which skill the agent operates under. It is plain-English design — no code — written so the design can be reviewed and changed before any implementation.

## What the router is, in one paragraph

A task comes in (from a user, a CLI command, or another tool). The router looks at the task and produces a decision: "this should run on agent X, using skill Y." The agent then carries out the task with the skill's rules and tool permissions applied. The router never executes the task itself; its only job is the routing decision.

## Inputs

The router receives a `Task` object with the following shape:

| Field | Required | Description |
|---|---|---|
| `description` | yes | Free-text statement of what the user wants done. ("Write a function that…", "Review this PR", "Fix the bug where…") |
| `attachments` | no | Files, diffs, URLs, or other context the task refers to. |
| `pin.agent` | no | If set, forces the routing decision to use this agent. Bypasses inference. |
| `pin.skill` | no | If set, forces the routing decision to use this skill. Bypasses inference. |
| `metadata` | no | Free-form key/value hints from the caller (e.g. `language: python`, `repo: frontend`). |

`description` is the only required field. Everything else is optional context that improves routing accuracy.

## Outputs

The router produces a `RouteDecision`:

| Field | Description |
|---|---|
| `agent` | The agent identifier (`claude-opus`, `claude-sonnet`, `codex-medium`, etc.). |
| `skill` | The skill name (`pr-review`, `code-generation`, `debugging`, etc.) or `null` if no skill applies. |
| `confidence` | A score from 0.0 to 1.0 indicating how sure the router is. |
| `reason` | One sentence in plain English explaining the decision. Used for logging and debugging. |
| `fallback_used` | True if the decision came from the default fallback rather than a matching rule or classifier hit. |

The `reason` field is important: every routing decision must be auditable. If the wrong agent runs a task, the user should be able to look at `reason` and understand why.

## Decision strategy

The router walks three stages in order. The first stage to produce a confident decision wins; otherwise it falls through to the next.

### Stage 1: explicit pin

If `task.pin.agent` or `task.pin.skill` is set, use it. Pins are the user's explicit override and the router does not second-guess them.

- If only `pin.agent` is set, the router still chooses the skill via stages 2–3.
- If only `pin.skill` is set, the router still chooses the agent via stages 2–3, but constrained to agents listed in the skill's `preferred_models`.
- If both are set, the router returns immediately.

Confidence on a pin is always 1.0; reason is `"explicit pin"`.

### Stage 2: rule-based matching

The router consults `config/routing_rules.yaml`, a project-level file of human-written rules. Each rule has a condition (regex, keyword set, tag, file-extension presence) and a target (agent, skill, or both).

Rules are evaluated in file order; **first match wins**. This is deliberate so the file reads top-to-bottom as a priority list.

Example shape:

```yaml
rules:
  - name: pr-review-tasks
    when:
      description_matches: "(?i)\\b(review|pr|pull request|code review)\\b"
    then:
      skill: pr-review

  - name: debugging-tasks
    when:
      description_matches: "(?i)\\b(bug|broken|failing|error|crash|debug|fix)\\b"
    then:
      skill: debugging

  - name: default-coding
    when:
      always: true
    then:
      skill: code-generation
```

When a rule matches, confidence is 1.0 (the rule is the user's stated intent). Reason is `"matched rule: <rule name>"`.

If no rule matches and no `always: true` catch-all exists, the router falls through to Stage 3.

### Skill paths and auto-attach

If no explicit non-catch-all rule matches, the router checks task attachments against each skill's `paths` frontmatter globs before using an `always: true` catch-all. A matching path selects that skill with confidence 0.9 and records the matched glob in the decision reason. If multiple skills match, the longest matched glob wins as the most specific path rule; ties are broken alphabetically by skill name. If no skill path matches, routing continues to the catch-all or fallback behavior as usual.

### Stage 3: classifier inference (future)

When rule-based matching is insufficient, a small classifier model reads the task description and the list of available skills (`name` + `description` from each skill's frontmatter) and returns its best guess.

This stage is **deliberately out of scope for iteration 1**. The router will ship with rule-based matching only; the classifier is added once we have enough skills (probably 6–10) that hand-writing every rule becomes impractical.

When introduced, the classifier output includes a confidence score, and decisions below a configurable threshold (default 0.6) trigger fallback.

### Fallback

If all stages fail to produce a confident decision:

- Skill defaults to `code-generation` (the most general foundation skill).
- Agent defaults to the first entry in the chosen skill's `preferred_models`.
- `fallback_used` is set to `true`.
- Reason is `"no rule or classifier match; defaulted to <skill> / <agent>"`.

A failed routing decision should never block execution — there must always be a reasonable default.

## Skill composition with `requires`

If the chosen skill declares `requires: [foundation-skill]` in its frontmatter, the foundation skill's rules are composed in before the chosen skill's rules at execution time. The router itself does not perform the composition — it returns a single skill name, and the skill loader handles composition when the agent starts.

This keeps the router's output simple: one `(agent, skill)` pair.

## Agent selection within a skill

Once a skill is chosen, the router selects an agent by walking the skill's `preferred_models` list top to bottom and picking the first one available under current cost/availability constraints. Availability is determined by an `AgentRegistry` (out of scope for this doc; specified separately).

If no preferred model is available, the router falls back to a project-wide default agent specified in `config/defaults.yaml`.

## Failure modes the router must handle

| Failure | Behavior |
|---|---|
| Empty `description` | Reject the task with a validation error before routing. |
| `pin.skill` references an unknown skill | Reject with an error naming the skill. Do not silently fall through. |
| `pin.agent` references an unavailable agent | Reject with an error. Do not silently substitute. |
| Rules file is missing | Skip Stage 2; log a warning; proceed to Stage 3 / fallback. |
| Rules file has a syntax error | Fail the router at startup, not at task time. |
| Two rules match | First match wins (already specified). Log the rules that were skipped at debug level. |
| Skill exists but has no preferred_models | Use the project-wide default agent; log at debug level. |

## What the router is NOT responsible for

To keep the contract narrow:

- **The router does not execute the task.** That is the agent runner's job.
- **The router does not compose skill bodies.** That is the skill loader's job.
- **The router does not call out to LLM APIs.** Stage 3, when added, will use a separate classifier service.
- **The router does not enforce tool permissions.** That is the agent runner's job using the skill's `allowed_tools`.
- **The router does not track cost.** A separate cost-tracking layer wraps the agent runner.

The router's only output is a `RouteDecision`. Everything downstream is somebody else's concern.

## Open questions for future iterations

These are deliberately deferred — flagged here so they are not forgotten:

1. **Multi-skill tasks.** Some tasks naturally span two skills (write code *and* its tests; debug a bug *and* add a regression test). Does the router return one skill, two, or an ordered list? Iteration 1: one. Revisit when the foundation triad shows real friction.
2. **Classifier provider.** Which model runs Stage 3 when added? Likely a small Anthropic or OpenAI model. Decide when implementing.
3. **Per-rule confidence.** Today rules return confidence 1.0. Some rules ("description contains the word 'bug'") are weaker than others ("description starts with 'Review PR'"). Per-rule confidence may help when the classifier is introduced.
4. **Learning from corrections.** If the user overrides a routing decision repeatedly for similar tasks, the router could promote that into a rule automatically. Out of scope until usage data exists.
5. **Routing in agentic loops.** A long-running agent task may decompose into subtasks, each needing its own routing decision. The router contract is designed for one task at a time; multi-step routing is a separate concern.

## Implementation status

1. ✅ Router with Stage 1 (pins) and Stage 2 (rule-based) — `src/agent_fusion/router/router.py`.
2. ✅ `config/routing_rules.yaml` checked into the repo with the default rules.
3. ✅ `AgentRegistry` interface — minimal `StaticAgentRegistry` implementation in `src/agent_fusion/router/agent_registry.py`.
4. ✅ Tests covering each stage and failure mode — `tests/test_router.py`.
5. ✅ Path-based auto-attach (added after the original document was written) — see the "Skill paths and auto-attach" section above.

Stage 3 (the classifier) is a follow-up project once the rule-based router is in production and we know which routing decisions humans actually make.
