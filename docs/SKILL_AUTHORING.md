# Authoring skills

A skill is a Markdown file with YAML frontmatter that describes how a particular kind of coding task should be done. Skills are **content, not code**: you write them like documentation, the framework reads them at runtime, and the chosen agent runs the task under the rules and tool allowlist the skill defines.

This file is the canonical spec for the skill format. If you're adding a new skill or changing an existing one, follow this document.

The format intentionally mirrors [Anthropic's Claude Code skill format](https://github.com/anthropics/claude-code) so skills written for one ecosystem are easy to adapt for the other.

---

## File location and naming

- Skills live under `skills/` at the repo root.
- One file per skill. Filename is `<skill-name>.md` in `kebab-case`.
- The filename stem must match the `name` field in the frontmatter.
- Subdirectories are allowed for grouping (`skills/data/sql.md`); the skill's `name` is still the bare stem.

---

## File shape

```markdown
---
name: pr-review
description: Review a pull request for correctness, security, and style.
preferred_models:
  - claude-opus
  - claude-sonnet
allowed_tools:
  - filesystem.read
  - shell.read
  - web_search
success_criteria:
  - Every changed file has been read in full
  - Security-sensitive changes are flagged with explicit severity
  - Feedback severity matches actual impact
tags:
  - review
  - quality
---

# PR review

## When to use

Use this skill when the task is to review a pull request, code diff, or proposed change for correctness, security, style, and adherence to project conventions.

## Rules

1. Read every changed file in full before commenting. Do not comment on a file you have only seen in the diff.
2. ...

## Process

1. ...

## Output format

...

## Examples

```python
# concrete code examples for the LLM to anchor on go here
```
```

---

## Frontmatter schema

| Field             | Type           | Required | Notes                                                                                              |
| ----------------- | -------------- | -------- | -------------------------------------------------------------------------------------------------- |
| `name`            | string         | yes      | Must match the filename stem. Lowercase, kebab-case.                                               |
| `description`     | string         | yes      | One sentence. Used by the router classifier to match tasks to skills.                              |
| `preferred_models`| list[string]   | no       | Ranked list. Router treats as a hint; first available wins unless a rule overrides.                |
| `allowed_tools`   | list[string]   | no       | Write-tier tools the skill may invoke. Read-tier tools are always available.                       |
| `success_criteria`| list[string]   | no       | Acceptance bar. The agent must verify these before declaring the task complete.                    |
| `tags`            | list[string]   | no       | Free-form labels for grouping and discovery (`frontend`, `review`, `data`, etc.).                  |
| `requires`        | list[string]   | no       | Other skill names this skill builds on. Their rules are composed in before this skill's body.      |

Unknown frontmatter fields are rejected at load time so typos surface immediately.

---

## Body conventions

The Markdown body is what the LLM actually reads. Keep it focused and machine-friendly:

1. **Lead with `## When to use`.** One paragraph telling the model when this skill applies. The router classifier and the model itself both rely on it.
2. **Then `## Rules`.** Numbered, imperative, testable. Each rule should be one thing the model can either obey or violate. Bad: "write good code." Good: "every public function has a type-annotated signature."
3. **Then `## Process`** if the work has steps. Numbered. Steps should be small enough to verify mid-task.
4. **Then `## Output format`** if the skill produces a structured artifact (review comments, migration script, etc.).
5. **Then `## Examples`.** Concrete code or input/output samples. Examples are the strongest signal a model gets — invest here. Use fenced code blocks with language tags so the model parses them correctly.
6. **Then `## Anti-patterns`** (optional). Things to avoid, with brief reasons. Phrasing as "do not X" lets the model match against negative cases.

Keep the whole skill under ~400 lines. Skills longer than that usually want to be split into a base skill and a `requires:`-linked specialization.

---

## Tool tiers

Tools are grouped into tiers (see [docs/GLOSSARY.md](GLOSSARY.md)):

- **Read tier** — `filesystem.read`, `grep`, `glob`, `web_search`, `shell.read`. Available to every skill by default. Do **not** list these in `allowed_tools` — they are implicit.
- **Write tier** — `filesystem.write`, `shell.exec`, `network.post`, `git.commit`, `code_executor`. Off by default. Skills must list each write-tier tool they need by exact name.

If you find yourself listing every write tool, the skill is probably too broad — split it.

---

## Model preferences

`preferred_models` is a **ranked list of hints**, not a hard pin. The router will:

1. Apply any matching rule from `config/routing_rules.yaml` (rules win).
2. Otherwise, walk `preferred_models` top-to-bottom and pick the first one available under the current cost/quota constraints.
3. Fall back to a default model if none of the preferred models are available.

Pin a model only when there is a real reason (e.g. a skill that depends on extended thinking or a 1M-token context). Otherwise list two or three so degradation is graceful.

---

## Validation

When a skill loads, the registry checks that:

- The file parses as Markdown with YAML frontmatter.
- All required frontmatter fields are present and well-typed.
- `name` matches the filename stem.
- `allowed_tools` only references known tool names.
- `requires` only references existing skills, with no cycles.
- Body has at least the `When to use` and `Rules` sections.

Validation errors fail fast at startup, not at task time.

---

## Authoring workflow

1. Skim two or three high-quality real-world references (a security-review style guide, a frontend conventions doc, a SQL style guide, etc.) before writing.
2. Draft the skill against a real example task. If you can't think of a concrete task the skill applies to, the skill is too abstract.
3. Keep it under ~400 lines. Cut anything that doesn't change model behavior.
4. Add an entry to the example list in the README's routing intent table if the skill is broadly applicable.
5. Open a PR. Skills are reviewed for clarity and concreteness, not just correctness.
