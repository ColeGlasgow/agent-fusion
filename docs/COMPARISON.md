# How agent-fusion compares

agent-fusion routes a coding task to the best-suited AI agent (Claude Code, Codex) and hands that agent a cited, composable rulebook called a *skill* before it starts. This page compares agent-fusion against five peer projects in the AI-coding-rules space so you can see where its design choices differ from the field. It is a summary; the full analysis with per-cell sources lives in the internal landscape doc.

## Comparison matrix

| Project | Sourcing / audit trail | Composition | Tool tiers | Routing | Path activation | Validation |
|---|---|---|---|---|---|---|
| **agent-fusion** | Per-rule citations with confidence ratings (`.sources.md` sidecar) | `requires:` dependency graph, cycle detection | Read tier implicit, write tier declared per skill | Task to (agent, skill) mapping | `paths` glob auto-attach | Schema loader: names, frontmatter, requires graph, body sections |
| Claude Code skills | None | None (monolithic `SKILL.md`) | Flat `allowed-tools` allowlist | Description match, single agent | `paths` glob | Frontmatter shape, name and description caps |
| Cursor rules | None | Hierarchical via nested `AGENTS.md` | Admin-enforced Team Rules, no tiers | Description, globs, or manual mention; single agent | `globs` | Frontmatter validation, no size enforcement |
| Cline rules | None | Additive merge across files | None | Globs plus manual toggles; single agent | `paths` glob | No documented schema |
| Continue.dev rules | None | Concatenation in toolbar order | None | Globs, regex, or agent-requested; single agent | `globs` / `regex` | Not documented |
| Aider conventions | None | None | Read-only marking, no access control | Manual or config; single agent | None | None |

## What is unique to agent-fusion

- **Rule-by-rule sourcing.** Every skill ships a `.sources.md` sidecar with a citation table and a confidence column that flags synthesized rules honestly. No peer project documents a sourcing or audit system.
- **Typed composition.** `requires:` resolves a named dependency graph: the loader prepends foundation skills, deduplicates shared dependencies, and rejects cycles at load time. Peers concatenate or merge; none resolve a typed graph.
- **Read/write tool tiers.** Read-tier tools are implicit; write-tier tools must be declared per skill, making least-privilege enforceable at the schema level rather than by convention.
- **Task to (agent, skill) routing.** Every peer assumes one agent and routes only at the rule level. agent-fusion is the only project that proposes dispatching the same task to a different model based on rule matching, with an auditable reason for each decision.
- **Schema-validating loader.** Unknown frontmatter fields, bad names, requires cycles, and missing body sections fail at load time, not at task time.

## Honest gaps

- **No runtime executor yet.** Peers all ship a working agent runner, so their rules govern real tasks today. agent-fusion has a loader and a router but no executor, so the rules are not yet exercised end to end.
- **No IDE integration.** Cursor is an IDE; Cline and Continue.dev are editor extensions; Claude Code ships IDE plugins. agent-fusion has no editor surface, so skills must be exported into another tool to use them.
- **Small skill count.** Five skills today. The peer ecosystems host community rule sets at much larger scale. agent-fusion's depth per skill is high; its breadth is not.
