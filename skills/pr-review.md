---
name: pr-review
description: Review a pull request or code diff for correctness, security, and adherence to project conventions. Language-agnostic foundation; language-specific skills extend this via `requires:`.
preferred_models:
  - claude-opus
  - claude-sonnet
allowed_tools: []
success_criteria:
  - Every changed file has been read in full, not just the diff hunks
  - Each comment cites a specific file and line
  - Severity is explicit on every comment (blocker, suggestion, nit, fyi)
  - Security-sensitive changes are flagged when present
  - The CL description has been verified for clarity
  - Positive practices have been acknowledged where present
tags:
  - review
  - quality
  - foundation
---

# PR review

Foundation skill for reviewing pull requests in any language. Citations for every rule below live in `pr-review.sources.md` next to this file.

## When to use

Reviewing a pull request, code diff, or proposed change in any language. Not for writing code or generating tests.

## Rules

1. **Read every changed file in full, not just the diff.** A line that looks fine in isolation may break an invariant defined fifty lines above. If you cannot read the file in full, say so and decline to approve.

2. **Approve when the change improves overall code health, even if imperfect.** The bar is "better," not "perfect." Holding a CL because it is not yet ideal is worse than landing a clear improvement.

3. **Tag every comment with a severity prefix.** `blocker:` (must fix), `suggestion:` (please consider), `nit:` (optional polish), `fyi:` (informational). Untagged comments create ambiguity about whether the author has to act.

4. **Comment on the code, not the author.** Write "this function couples the parser to the renderer" — not "you coupled the parser to the renderer." Second-person phrasing triggers defensiveness without improving outcomes.

5. **Explain the reasoning behind non-obvious feedback.** "Use a generator here so we don't load the full result set into memory" beats "use a generator here." The author should learn from the comment, not just patch the symptom.

6. **Point out problems; let the author choose the fix.** If two approaches both meet the bar, name the tradeoff and let them pick. Prescribe only when one answer is clearly correct.

7. **If a CL is too large to review thoroughly, ask for it to be split.** Roughly: 100 lines reasonable, 1000 lines too large; spread across many files matters as much as line count.

8. **Verify tests cover the changed behavior, not just that tests exist.** Apply the check: "if I deleted the new code, would this test fail?" If no, the test is decoration.

9. **Flag security-sensitive changes with explicit severity.** Auth, crypto, input validation, secrets handling, deserialization, file paths, and SQL/HTML injection are blocker-eligible by default. Do not bury security in a `nit:`.

10. **Verify comments explain *why*, not *what*.** A comment paraphrasing the next line of code is noise. A comment explaining a constraint that forced an unusual choice is signal.

11. **Treat the project's style guide as authority on style; do not invent personal rules.** If you cannot cite the rule, it is your preference, not the project's.

12. **Acknowledge what was done well.** A review with ten problems and zero positives is technically accurate and culturally corrosive. Name a thoughtful test or a clean refactor when you see one.

13. **Verify the CL description.** First line imperative and stand-alone (`Add retry to webhook delivery`). Body explains why, not just what. Reject `"fix bug"`, `"phase 1"`, `"address feedback"`.

14. **Push back on speculative complexity.** "We might need this later" is a reason to delete code, not add it. Watch for premature interfaces, unused configuration knobs, and abstractions for a single caller.

## Process

1. **Read the description.** State the intent in one sentence. If you cannot, comment on the description (Rule 13) before reading code.
2. **List changed files.** Group by area (production, test, config, docs).
3. **Read each changed file in full.** Note responsibilities.
4. **Re-read the diff with that context.**
5. **Run Rules 1–14.** Generate comments as findings appear.
6. **Categorize and label severity.**
7. **Verify `success_criteria`.** Each item answerable with "yes."
8. **Write the review** in the output format below.

## Output format

```markdown
## Summary
<one paragraph: what the CL does, your overall recommendation, and approve / request-changes / comment>

## Blockers
- `path/to/file.ext:line` — **blocker:** <issue> — <why it blocks>

## Suggestions
- `path/to/file.ext:line` — **suggestion:** <issue> — <reasoning>

## Nits
- `path/to/file.ext:line` — **nit:** <small thing, author can ignore>

## FYI
- `path/to/file.ext:line` — **fyi:** <informational, no action expected>

## Things done well
- <one or two specific positives>
```

Omit empty sections. Always include `Summary`; include `Things done well` only when at least one specific positive exists.

## Examples

Each pair shows a common AI failure followed by the correct pattern. Languages vary intentionally — the rules are universal.

### Example 1: tests for behavior, not for show

A reviewer accepts a test that would still pass if the production code were reverted.

**Common AI failure:**

```python
# Production change: handler now retries failed webhooks 3 times.
def deliver_webhook(payload):
    for attempt in range(3):
        try:
            return _send(payload)
        except TransientError:
            continue
    raise

# New test:
def test_deliver_webhook_returns_response():
    response = deliver_webhook({"event": "x"})
    assert response.status == 200

# Reviewer says:
# Tests added, looks good.
```

Why this fails: the test only exercises the success path, which already worked before the retry was added. The test would still pass if `for attempt in range(3)` were deleted. Violates Rule 8.

**Correct pattern:**

```text
- tests/test_webhooks.py:45 — blocker: this test passes against the
  pre-change code (no retry). To actually test the retry behavior, mock
  `_send` to raise TransientError on the first two calls and succeed on
  the third, then assert `_send` was called 3 times. As written this test
  is decoration.
```

Why this works: applies the "would the test fail if the code were reverted?" check from Rule 8 and names the precise mock setup that would make it real.

---

### Example 2: reading the diff vs. the file

A reviewer comments only on the diff and misses surrounding context.

**Common AI failure:**

```sql
-- Diff shows:
-  WHERE created_at > now() - interval '7 days'
+  WHERE created_at > now() - interval '30 days'

-- Reviewer says:
-- looks fine, just a wider window.
```

Why this fails: the diff is fine in isolation. The unread file shows this query feeds a dashboard with a hard-coded `LIMIT 10000`. Widening 7→30 days will silently truncate at the limit on busy customers. Violates Rule 1.

**Correct pattern:**

```text
- analytics/queries/recent_events.sql:14 — blocker: widening to 30 days
  exceeds the `LIMIT 10000` on line 22 for tenants over ~333 events/day
  (we have 14 such tenants per the metrics dashboard). Either bump the
  limit, page the query, or keep the 7-day window. The change as-is will
  silently drop rows from the dashboard for those tenants.
```

Why this works: catches the failure mode that only appears when the file is read in full, names the affected population, and proposes three alternatives.
