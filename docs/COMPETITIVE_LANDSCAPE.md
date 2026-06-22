# Competitive landscape

A structured comparison of agent-fusion against five peer projects in the AI-coding-rules space: Anthropic Claude Code skills, Cursor rules, Cline rules, Continue.dev rules, and Aider conventions. The goal is to identify where agent-fusion's design choices exceed the field, where they lag, and what concrete next steps follow.

This document is a one-shot snapshot. It does not change any skill or piece of code in the repository.

## Methodology

Each peer project was studied through its official documentation, accessed via `WebFetch` and `WebSearch` against the maintainers' canonical URLs. Where a primary URL redirected or returned an error, a supplementary source was used (community-maintained reference for Cursor, blog post for Cline) and is cited separately in the Sources section. All four named dimensions (rule format, sourcing, composition, routing) and the three secondary dimensions (tool tiers, language skills, validation) come from the project's own documentation, not from second-hand summaries. No claim is made about features the documentation does not describe.

## Comparison matrix

Rows are projects (agent-fusion first). Columns are the capability dimensions that distinguish the field.

| Project | Rule format | Sourcing / audit trail | Composition | Routing | Tool tier system | Language / domain skills | Validation / loader |
|---|---|---|---|---|---|---|---|
| **agent-fusion** | Markdown with YAML frontmatter; single file `skills/<name>.md` + sidecar `<name>.sources.md` | Cited per rule, confidence-rated in sidecar | `requires:` field with graph composition and cycle detection | Task → (agent, skill) via pin + rule-based matching; Stage-3 classifier deferred | Two tiers: read-tier implicit, write-tier explicit allowlist (`filesystem.write`, `shell.exec`, `network.post`, `git.commit`, `code_executor`) | 5 skills: foundation triad (`pr-review`, `code-generation`, `debugging`) plus `python-backend` and `frontend-react` | Schema validator: frontmatter shape, kebab-case names, allowed tools, requires graph, body sections |
| Anthropic Claude Code skills | Directory `<name>/SKILL.md` + optional `scripts/`, `reference.md`, `examples/`; YAML frontmatter (`name`, `description`, `allowed-tools`, `paths`, `disable-model-invocation`, `model`, `effort`, `context`, `agent`, `hooks`) | None | None (`SKILL.md` is monolithic; subagent skill preloading is sequencing, not composition) | Activation by description match; optional `paths` glob activation | Flat `allowed-tools` list, no read/write tiering | Open Agent Skills standard; bundled set includes `/simplify`, `/batch`, `/debug`, `/loop`, `/claude-api`, `/init`, `/review`, `/security-review` | Frontmatter parsed and validated; max 64 chars on name; description capped at 1,536 chars |
| Cursor rules | `.mdc` files (also `.md`); YAML frontmatter (`description`, `globs`, `alwaysApply`) | None | None within rules; hierarchical via nested `AGENTS.md` files | Four modes: Always Apply, Apply Intelligently (agent decides via description), Apply to Specific Files (globs), Apply Manually (`@` mention) | Team Rules in Enterprise plans can be marked required by admins; no read/write classification | Community-driven `awesome-cursor-rules-mdc` repository; no canonical count | Loader validates frontmatter; documentation warns about "token tax" but no hard size enforcement |
| Cline rules | `.clinerules/` directory of `.md`/`.txt` files; optional YAML frontmatter with `paths` glob | None | Additive merge across files; no inheritance | Manual toggles in UI + glob-conditional activation via `paths` | None | Community `cline/prompts` repository; user-authored, count varies | Files combined into a "unified set of rules"; no formal schema documented |
| Continue.dev rules | YAML or Markdown with frontmatter (`name`, `globs`, `regex`, `description`, `alwaysApply`) | None | Concatenation of rule files in toolbar order; no `requires:` field | Three types: always-applied, glob/regex-conditional, agent-requested via `create_rule_block` tool | None | Hub assistant + user rules; no canonical foundation set | Hub-published rules support `uses:` references; local validation not documented |
| Aider conventions | Plain `CONVENTIONS.md` (no frontmatter); loaded read-only via `/read` or `.aider.conf.yml` | None | None (multiple files loaded independently) | None — files are added to chat manually or by config | None (read-only marking prevents edits but does not restrict model access) | Community-contributed conventions repository | No schema; conventions are free-form markdown |

Sources for every cell appear in the Sources section at the bottom.

## Per-dimension analysis

### Rule format

The field has converged on Markdown + YAML frontmatter. Aider is the only outlier (no frontmatter, plain prose). Claude Code is the most structurally rich (directory-per-skill with supporting files), while agent-fusion sits in the middle: single file per skill plus a sidecar for audit. Cursor's `.mdc` extension and Cline's `.clinerules/` directory are both Markdown variants. The format itself is not where agent-fusion differentiates — the body structure (`When to use` → `Rules` → `Process` → `Output format` → `Examples`) is more rigorous than the field, but the file shape is conventional.

### Sourcing / audit trail

This is agent-fusion's largest single defensibility advantage. Every peer project — Claude Code, Cursor, Cline, Continue.dev, Aider — ships rules without citations. Their documentation does not describe a sourcing system, an audit trail, or a confidence-rating mechanism. agent-fusion's `<name>.sources.md` sidecar with rule-by-rule citation table and confidence column (see `skills/code-generation.sources.md`, `skills/python-backend.sources.md`, `skills/frontend-react.sources.md`) is unique in the surveyed field. The defensibility argument is straightforward: "every rule traces to a named enterprise reference" is a claim no peer project can make.

### Composition

agent-fusion's `requires:` field resolves a named dependency graph. The skill loader (`src/agent_fusion/skills/loader.py`) prepends required skill bodies depth-first, deduplicates shared transitive dependencies, and rejects cycles at load time. The peer field has nothing equivalent:

- Claude Code: no composition. `SKILL.md` is monolithic. Preloading skills into subagents is sequencing, not graph resolution.
- Cursor: no rule-to-rule composition; hierarchical `AGENTS.md` files combine across directories.
- Cline: additive merge across all files in `.clinerules/`.
- Continue.dev: concatenation of rule files in toolbar order.
- Aider: independent loading of `CONVENTIONS.md` files.

`python-backend` requiring `code-generation` is the only example in the surveyed field of a typed, named, validated dependency between rule sets.

### Routing

This is the dimension where agent-fusion is most clearly *different* but not yet *better* — the architectural choice is unique, but unproven in production.

Every peer project assumes one agent and routes only at the rule/skill level. Claude Code activates skills by description matching. Cursor activates via globs, descriptions, or manual `@`-mention. Cline uses globs and manual toggles. Continue.dev uses globs, regex, or agent-requested. None of them dispatch the same task to a *different model or provider* based on rule matching.

agent-fusion's router (`docs/ROUTING.md`) defines a three-stage decision producing a `RouteDecision(agent, skill, confidence, reason)`. Stages 1 (pin) and 2 (rules) are implemented; Stage 3 (classifier) is deferred. The thesis — that some tasks are better served by Claude, others by Codex, and the routing decision should be auditable — is unique to agent-fusion in this field. Whether it pays off depends on agent execution shipping (see the lags section).

### Tool tier system

agent-fusion splits tools into a read tier (`filesystem.read`, `grep`, `glob`, `web_search`, `shell.read`) implicit for every skill, and a write tier (`filesystem.write`, `shell.exec`, `network.post`, `git.commit`, `code_executor`) declared per skill in `allowed_tools`. Claude Code's `allowed-tools` is a flat allowlist with no tier semantics. Cursor's Team Rules add admin-controlled enforcement but do not classify tools. Continue, Cline, and Aider have no tool permission system at all. The tier system is a security-posture choice: the principle of least privilege is enforceable at the schema level, not only by convention.

### Language / domain skills

agent-fusion has 5 skills. Cursor's `awesome-cursor-rules-mdc` community repository, Cline's `cline/prompts` repository, and Continue.dev's Hub all host substantial third-party rule sets. Claude Code ships a bundled set and follows the Agent Skills open standard (`agentskills.io`) for community contributions. agent-fusion's skill depth (foundation triad + two specializations, each with citations) is high; its breadth is negligible. Both numbers matter — depth proves the format works, breadth proves the format scales.

### Validation / loader

agent-fusion validates more than the field documents: kebab-case names matching filename stems, the `requires` graph for cycles, that only known frontmatter fields appear (typos surface as errors at load time), that body has `When to use` and `Rules` sections. Claude Code validates frontmatter shape, caps name length at 64 chars, caps description at 1,536 chars. The other three projects do not document loader validation in detail. Strict validation is a small but real differentiator: it catches authoring errors immediately rather than at task time.

## Per-peer summary

Reading the matrix dimension-by-dimension is one view; reading it peer-by-peer is another. Each peer below is one paragraph on how it differs from agent-fusion in particular.

**Anthropic Claude Code skills.** The most architecturally rich peer. Directory-per-skill format with supporting files (`scripts/`, `reference.md`, `examples/`), rich frontmatter (`paths`, `disable-model-invocation`, `model`, `effort`, `context: fork`), and dynamic context injection via `` !`<command>` ``. Subagent skill preloading provides a kind of sequencing but not composition — there is no `requires:` graph. Crucially, no sourcing or citation system. The Agent Skills open standard (`agentskills.io`) it follows is the most plausible interoperability target for agent-fusion's format.

**Cursor rules.** IDE-native. Four activation modes (Always, Auto Attached, Agent Requested, Manual) cover the editor-context patterns well. `.mdc` files with `description`, `globs`, `alwaysApply` are the most-imitated peer format in the wider community. Composition is hierarchical via nested `AGENTS.md` rather than typed dependency. No sourcing. Team Rules add admin enforcement on Enterprise plans, the closest thing to a permission system in the surveyed peers.

**Cline rules.** Workspace-first. `.clinerules/` is a directory of `.md`/`.txt` files combined into a "unified set of rules." Activation by glob `paths` or manual toggle in the rules panel. Strong community-distribution story via `cline/prompts`. No formal schema, no composition, no sourcing. Cline also auto-detects `.cursorrules`, `.windsurfrules`, and `AGENTS.md`, signalling a posture toward standard-format compatibility.

**Continue.dev rules.** Most explicit about rule types: always-applied, glob/regex-conditional, agent-requested via a `create_rule_block` tool. YAML/Markdown frontmatter with `name`, `globs`, `regex`, `description`, `alwaysApply`. Hub-published rules support a `uses:` field for referencing other rules — the closest thing in the field to agent-fusion's `requires:`, but framed as "include this rule" rather than "this skill builds on that skill." No sourcing.

**Aider conventions.** The simplest peer by design. `CONVENTIONS.md` is plain Markdown with no frontmatter; conventions are loaded as read-only files via `/read` or `.aider.conf.yml`. No composition, no permissioning, no routing, no sourcing. Aider's philosophy is "small surface area, terminal-attached" — most of the dimensions agent-fusion competes on are not dimensions Aider has chosen to develop.

## Where agent-fusion exceeds

1. **Rule-by-rule sourcing with confidence ratings.** Every skill ships a `.sources.md` sidecar with a rule-by-rule citation table and an honesty column flagging synthesis vs. cross-sourced rules. None of Claude Code skills, Cursor rules, Cline rules, Continue.dev rules, or Aider conventions document a sourcing or citation system. This is the largest single defensibility gap between agent-fusion and the field — it converts "we wrote some rules" into "every rule traces to a named enterprise reference, with synthesis flagged honestly."

2. **Typed composition with a `requires:` graph.** `skills/python-backend.md` declares `requires: [code-generation]` and the skill loader (`src/agent_fusion/skills/loader.py`) prepends the foundation body before the specialization, deduplicating shared transitive dependencies and rejecting cycles at load time. Continue.dev concatenates rule files in toolbar order; Cline additively merges; Cursor relies on nested `AGENTS.md`. None of them resolve a named dependency graph the way agent-fusion does.

3. **Read/write tool tier system.** `docs/SKILL_AUTHORING.md` separates tools into a read tier that is implicit for every skill, and a write tier that must be declared per skill. Claude Code's `allowed-tools` is a flat allowlist with no tier semantics; Cursor's Team Rules enforce admin-controlled requirements but do not classify tools; Continue, Cline, and Aider have no tool permission system.

4. **Router with explicit task → (agent, skill) mapping.** `docs/ROUTING.md` specifies a three-stage decision (pin, rules-based match, classifier) producing a single `RouteDecision`. Every peer project assumes one agent and routes only at the rule/skill level. agent-fusion is the only piece of the field that proposes a way to dispatch the same task to Claude or Codex based on rule matching.

5. **Schema-validating skill loader with cycle detection.** The loader rejects unknown frontmatter fields, validates kebab-case names against filename stems, checks the `requires` graph for cycles, and enforces body sections — at load time, not task time. Claude Code validates frontmatter shape and caps name length, but does not document a cycle check (its skills do not compose). Continue, Cline, and Aider do not document loader validation in detail.

6. **Rigorous body structure per skill.** agent-fusion's `When to use → Rules → Process → Output format → Examples` is mandatory for skills that need them and `When to use + Rules` minimums are enforced at load time. The peer field treats body structure as a convention, not a contract.

## Where agent-fusion lags

1. **No runtime; rules cannot fire yet.** Claude Code, Cursor, Cline, Continue.dev, and Aider all ship working agent executors. Their rules govern real coding tasks today. agent-fusion has a skill loader and a router but no agent runner, so the entire benefit of the rules is unverified in production. `AGENTS.md` explicitly states the repo is in "design phase. No runtime code exists yet." Until an executor lands, the project is a specification, not a tool.

2. **No IDE integration.** Cursor is itself an IDE. Cline and Continue.dev are IDE extensions for VS Code and JetBrains. Aider is a terminal CLI. Claude Code ships VS Code and JetBrains plugins. agent-fusion has no editor surface. A developer cannot use agent-fusion's skills today without copying them into another tool.

3. **Tiny skill count.** Five skills total. Cursor's `awesome-cursor-rules-mdc` community repository hosts third-party rule sets at scale. Cline's `cline/prompts` repository does the same. Continue.dev has a Hub for sharing rules. The Anthropic Claude Code ecosystem follows the Agent Skills open standard with an agentskills.io community catalog. agent-fusion's rule depth is high; its breadth is negligible.

4. **No file-path activation.** Claude Code (`paths` field), Cursor (`globs`), Cline (`paths`), and Continue.dev (`globs`/`regex`) all activate rules based on which files are in scope. agent-fusion's router uses task description matching only, so a skill cannot auto-load when a Python file is open. For an interactive editor experience, this is a meaningful UX gap; for a programmatic-task router, it is less critical but still missing.

5. **No supporting-file pattern.** Claude Code skills can ship `scripts/helper.py`, `reference.md`, `examples/sample.md` alongside `SKILL.md`. agent-fusion's single-file format forces everything into the body. The `.sources.md` sidecar is audit metadata, not loaded content — there is no way today to ship an executable helper alongside a skill.

6. **No dynamic context injection.** Claude Code's `` !`<command>` `` syntax runs shell commands and inlines their output before the model sees the skill body, turning skills into live procedures, not static instructions. agent-fusion has no equivalent. A `pr-review` skill in Claude Code can pull `gh pr diff` automatically; agent-fusion's `pr-review` cannot.

## Three concrete recommendations

Each is small enough to ship as one PR.

**1. Add `paths:` frontmatter and route on it.**
Add a `paths` field to the skill schema (list of glob patterns). Extend `src/agent_fusion/router/router.py` to consider paths in `task.attachments` when matching, so a task with a `.py` attachment will prefer skills whose `paths` includes `**/*.py`. This closes the largest UX gap with Claude Code, Cursor, Cline, and Continue.dev in one change.

Scope: schema addition in `loader.py`, one new router stage, tests for matching and non-matching paths. No skill body changes needed; existing skills work unchanged because the field is optional.

Acceptance criteria: (a) `paths` declared on a test skill auto-matches tasks whose `attachments` contain a path matching the glob; (b) the router's `reason` field cites the matching `paths` entry; (c) existing tests still pass; (d) `docs/SKILL_AUTHORING.md` documents the field with one example.

**2. Support directory-per-skill format alongside the single-file format.**
Extend `load_skills_dir` to accept `skills/<name>/SKILL.md` in addition to `skills/<name>.md`. Loaded skill body comes from `SKILL.md`; the sources sidecar is recognized at `skills/<name>/sources.md`. Supporting files in `skills/<name>/scripts/` or `skills/<name>/examples/` are not auto-loaded but are referenceable from the body. This matches the emerging Agent Skills open standard Claude Code follows and unlocks the supporting-file pattern.

Scope: loader + tests. No skill body changes needed.

Acceptance criteria: (a) both `skills/foo.md` and `skills/foo/SKILL.md` load to equivalent `Skill` objects; (b) a directory-format skill with `scripts/` and `examples/` subdirectories loads cleanly; (c) duplicate name across the two formats is rejected at load time; (d) `docs/SKILL_AUTHORING.md` documents the directory option.

**3. Publish a `docs/COMPARISON.md` derived from this analysis.**
Take the matrix and the "Where agent-fusion exceeds" section, condense to a public-facing comparison page, and link from the README. The unique selling points (sourcing, composition, tool tiers, routing) are invisible to anyone who lands on the repo cold.

Scope: one new doc derived from this one, one README link.

Acceptance criteria: (a) `docs/COMPARISON.md` exists and is linked from the README; (b) every claim about a peer cites a public URL; (c) the doc is under 100 lines (the long-form analysis stays here; the public version is a quick-read summary).

## Implications for the project roadmap

Read alongside the open-items list in the project's working memory:

- The lags section identifies "no runtime" as the largest external gap. The agent executor (previously item 3 in the roadmap) is the single change that converts agent-fusion from specification to tool. Until it lands, every other improvement is incremental.
- Recommendations 1 (`paths`) and 2 (directory-per-skill) are both small loader-level changes that unblock the executor's UX without committing to an execution model. Both can ship before the executor.
- Recommendation 3 (`docs/COMPARISON.md`) is a marketing artifact, not a code change. Its value is proportional to the project's public discoverability — high if a public launch is on the horizon, low otherwise. Sequence accordingly.
- The exceeds section identifies sourcing, composition, and the tool tier system as defensibility. These should be preserved as load-bearing differentiators in any future refactor. They are the answers to "why agent-fusion and not Cursor rules."

## Caveats

- This analysis is a snapshot in May 2026 and will go stale. Peer projects iterate rapidly; the Claude Code skills documentation has updated multiple times in the past year and the Cursor rules schema has shifted between `.cursorrules` and `.mdc`. Re-run the comparison every 6 months.
- The Cursor primary documentation URL redirected during data gathering and the supplementary community-maintained reference was used for the `.mdc` frontmatter field detail. The fields cited (`description`, `globs`, `alwaysApply`) are stable across the community references and forum discussions but could not be verified directly on Cursor's docs site during this study.
- "Where agent-fusion exceeds" is measured against documented features, not actual user value. Sourcing rules with citations is unique; whether it improves agent output is an open question that requires a separate A/B test, not a comparison study.

## Appendix: frontmatter cheat sheet

A side-by-side of the actual frontmatter fields each project recognizes. Useful when designing the `paths` and directory-format changes in Recommendations 1 and 2, and when deciding which fields agent-fusion should adopt from the field.

**agent-fusion** (`docs/SKILL_AUTHORING.md`):

```yaml
name: kebab-case-name        # required, must match filename stem
description: one sentence    # required
preferred_models:            # optional, ranked list for router
  - claude-opus
allowed_tools:               # optional, write-tier only
  - filesystem.write
success_criteria:            # optional, agent verifies before completion
  - condition
tags:                        # optional, free-form
  - foundation
requires:                    # optional, named skill dependencies
  - code-generation
```

**Claude Code skills** (`SKILL.md`):

```yaml
name: kebab-case-name        # optional, defaults to directory name
description: one sentence    # recommended
when_to_use: extra context   # optional
allowed-tools: "Read Grep"   # optional, flat allowlist
disable-model-invocation: false  # optional
user-invocable: true         # optional
paths: "**/*.py"             # optional, glob activation
model: inherit               # optional
effort: medium               # optional
context: fork                # optional, subagent
agent: Explore               # optional, subagent type
hooks: {...}                 # optional
arguments: [issue, branch]   # optional, $name substitution
```

**Cursor rules** (`.mdc`):

```yaml
description: when this rule applies   # required for Agent Requested mode
globs: ["src/**/*.tsx"]               # optional, file-pattern activation
alwaysApply: false                    # optional, always-on toggle
```

**Cline rules** (`.clinerules/*.md`):

```yaml
paths:                       # optional, glob activation
  - "src/components/**"
```

**Continue.dev rules** (YAML or MD):

```yaml
name: rule-name              # required for YAML rules
description: summary         # optional
globs: "**/*.{ts,tsx}"       # optional
regex: "useEffect"           # optional
alwaysApply: false           # optional
```

**Aider conventions** (`CONVENTIONS.md`): no frontmatter — plain Markdown loaded as read-only context.

The fields that recur across most peers and would be the highest-leverage additions to agent-fusion: `paths` / `globs` for file-context activation (Recommendation 1), and an optional `disable-model-invocation` equivalent if the executor ever supports user-only skills.

## Sources

- **Anthropic Claude Code skills** — Anthropic. _Extend Claude with skills._ https://code.claude.com/docs/en/skills (redirected from `docs.anthropic.com/en/docs/claude-code/skills`).
- **Agent Skills open standard** — referenced by the Claude Code skills documentation. https://agentskills.io
- **Cursor rules** — Cursor. _Rules._ https://cursor.com/docs/context/rules
- **Cursor rules supplementary** — Vibe Coding Academy. _Cursor Rules: Complete .mdc Guide & 15 Templates (2026)._ https://www.vibecodingacademy.ai/blog/cursor-rules-complete-guide (used for `.mdc` frontmatter field confirmation when the primary URL redirected).
- **Cline rules** — Cline. _Rules._ https://docs.cline.bot/customization/cline-rules
- **Cline rules supplementary** — Cline blog. _.clinerules: Version-Controlled, Shareable, and AI-Editable Instructions._ https://cline.bot/blog/clinerules-version-controlled-shareable-and-ai-editable-instructions
- **Continue.dev rules** — Continue. _Rules deep dive._ https://docs.continue.dev/customize/deep-dives/rules
- **Aider conventions** — Aider. _Specifying coding conventions._ https://aider.chat/docs/usage/conventions.html
- **agent-fusion routing design** — this repository. `docs/ROUTING.md`.
- **agent-fusion skill authoring spec** — this repository. `docs/SKILL_AUTHORING.md`.
- **agent-fusion skill loader implementation** — this repository. `src/agent_fusion/skills/loader.py`.
