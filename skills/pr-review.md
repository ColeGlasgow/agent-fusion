---
name: pr-review
description: Review a pull request or code diff for correctness, security, and adherence to project conventions.
preferred_models:
  - claude-opus
  - claude-sonnet
allowed_tools:
  - filesystem.read
success_criteria:
  - Every changed file has been read in full, not just the diff hunks
  - Security-sensitive changes are flagged with explicit severity
  - Feedback severity matches actual impact (no style nits as blockers)
  - Each comment is actionable and points at a specific file and line
tags:
  - review
  - quality
---

# PR review

> **Status:** placeholder. This skill exists to validate the file format. Concrete rules and examples will be filled in based on deep research and real review style guides before the first router lands.

## When to use

Use this skill when the task is to review a pull request, code diff, or proposed change for correctness, security, style, and adherence to project conventions. Applies to PRs in any language.

## Rules

1. Read every changed file in full before commenting. The diff is not enough; surrounding context matters.
2. Flag security-sensitive changes (auth, crypto, input validation, secrets handling) with explicit severity.
3. Match feedback severity to actual impact. Style nits are `nit:`, suggestions are `suggestion:`, blockers are `blocker:`.
4. Do not comment on lines unchanged by the PR unless they are now broken by the change.
5. Cite a specific file and line for every comment.

## Process

1. Read the PR description and linked issue. State in one sentence what the PR is trying to do.
2. List changed files. Read each in full.
3. For each file, note: correctness, security, conventions, tests.
4. Produce review comments grouped by severity.
5. Verify each item in `success_criteria` before declaring done.

## Output format

```markdown
## Summary
<one paragraph: what the PR does and your overall recommendation>

## Blockers
- `path/to/file.py:42` — <issue>

## Suggestions
- `path/to/file.py:101` — <suggestion>

## Nits
- `path/to/file.py:7` — <nit>
```

## Examples

*To be filled in with real examples once the starter library lands.*

## Anti-patterns

- Do not approve a PR you have not fully read. "LGTM" without evidence is not a review.
- Do not invent style rules not present in the project's actual conventions.
- Do not block on personal preference. If it is not in the project's style guide or causing a real problem, mark it `nit:` or skip it.
