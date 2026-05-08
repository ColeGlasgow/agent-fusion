# CLAUDE.md

Guidance for Claude Code working in this repository. Claude Code loads this file automatically on session start.

The canonical, full agent guide is [AGENTS.md](AGENTS.md). Read it before making non-trivial changes — it covers repository identity, where code goes, build/test/lint commands, hard rules, style, and what's in scope during the design phase.

The four principles below are the most important rules to keep in mind for every change. They are duplicated here (rather than only in `AGENTS.md`) because they should be visible at session start without a second file load. `AGENTS.md` remains the source of truth; if these ever diverge, `AGENTS.md` wins.

---

## Working principles

### 1. Think before coding

Don't assume. Don't hide confusion. Surface tradeoffs. State assumptions explicitly. If uncertain or multiple interpretations exist, ask before implementing. If a simpler approach exists, say so.

### 2. Simplicity first

Minimum code that solves the problem. No features beyond what was asked. No abstractions for single-use code. No "flexibility" that wasn't requested. No error handling for impossible scenarios. If 200 lines could be 50, rewrite.

### 3. Surgical changes

Touch only what you must. Don't "improve" adjacent code or formatting. Match existing style. If you notice unrelated dead code, mention it — don't delete it. Every changed line should trace directly to the request.

### 4. Goal-driven execution

Define success criteria. Loop until verified. Turn vague asks into testable goals ("fix the bug" → "write a failing test, then make it pass"). For multi-step work, state a brief plan with a verification check per step.

---

## Project-specific reminders

- This repo is in the **design phase**. Most code paths in `AGENTS.md`'s "Where things go" table do not exist yet. Don't reference them as if they did.
- **No emojis** in source, comments, commits, or docs.
- Out-of-scope work without explicit approval: new agents beyond Claude/Codex, vector memory infrastructure, web UI, third-party SaaS integrations.
- When in doubt, open a **Design proposal** issue before writing code.

For the full conventions, hard rules, and scope details, see [AGENTS.md](AGENTS.md).
