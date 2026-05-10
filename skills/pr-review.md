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

Foundation skill for reviewing pull requests in any language. The rules below are drawn from the intersection of Google's Engineering Practices and Microsoft's Engineering Playbook; both companies converge on the same principles, so violations of these rules are violations of the published bar at two of the largest engineering organizations on the planet.

Language-specific review skills (`pr-review-python`, `pr-review-typescript`, `pr-review-sql`) extend this skill via `requires:`. They add language-specific rules and examples; the rules in this file apply regardless of stack.

## When to use

Use this skill when the task is to review a pull request, code diff, or proposed change, in any language, for any project. The task description will typically include a diff, a PR URL, or a request like "review this change."

Do not use this skill for: writing code, generating tests, or producing the change itself. Those are different skills with different priorities.

## Rules

1. **Read every changed file in full, not just the diff.** The diff strips context. A line that looks fine in isolation may break an invariant defined fifty lines above. If you cannot read the file in full, say so and decline to approve. *(Google: "Every Line")*

2. **Approve when the change definitely improves the overall code health, even if imperfect.** The bar is "better," not "perfect." Holding a CL for days because it is not yet ideal is a worse outcome than landing a clear improvement. *(Google: Standard of Code Review)*

3. **Tag every comment with a severity prefix.** Use `blocker:` (must fix to merge), `suggestion:` (please consider), `nit:` (style polish, optional), `fyi:` (informational). Untagged comments create ambiguity about whether the author has to act. *(Google: Comments)*

4. **Comment on the code, not the author.** Write "this function couples the parser to the renderer" — not "you coupled the parser to the renderer." Reviews evaluate code; phrasing in the second person triggers defensiveness without improving the outcome. *(Google: Comments)*

5. **Explain the reasoning behind non-obvious feedback.** "Use a generator here" is weak. "Use a generator here so we don't load the full result set into memory; this endpoint already paged out at 100k rows" is actionable. The author should be able to learn from the comment, not just patch the symptom. *(Google: Comments)*

6. **Point out problems; let the author choose the fix.** The author owns the change. If two approaches both meet the bar, name the tradeoff and let them pick. Reserve direct prescription for cases where there is a single correct answer. *(Google: Comments — "developer's responsibility to fix")*

7. **If a CL is too large to review thoroughly, ask for it to be split.** Google's heuristic is roughly 100 lines reasonable, 1000 lines too large; spread across many files matters as much as line count. A reviewer who cannot hold the change in their head produces a rubber-stamp review, which is worse than no review. *(Google: Small CLs)*

8. **Verify tests cover the changed behavior, not just that tests exist.** A test that would still pass if the change were reverted is not testing the change. Ask explicitly: "if I deleted the new code, would this test fail?" If no, the test is decoration. *(Google: Looking For — Tests)*

9. **Flag security-sensitive changes with explicit severity.** Auth, crypto, input validation, secrets handling, deserialization, file paths, and SQL/HTML injection are blocker-eligible by default. Do not bury security concerns in a `nit:` or alongside style feedback. *(OWASP Top 10; Google: Looking For — Every Line)*

10. **Verify comments explain *why*, not *what*.** Code already shows what it does; a comment restating that adds noise. A comment explaining the constraint that forced an unusual choice is signal. Push back on commentary that paraphrases the next line of code. *(Google: Looking For — Comments)*

11. **Treat the project's style guide as authority on style; do not invent personal rules.** If the linter and style guide are silent on a preference, do not block on it. If the author asks for a style rule's source and you cannot cite one, the rule is your preference, not the project's. *(Google: Standard — "style guides are absolute authority")*

12. **Acknowledge what was done well, not just what to fix.** A review that lists ten problems and zero positives is technically accurate and culturally corrosive. Naming a thoughtful test, a clean refactor, or a clarifying rename costs nothing and shifts the tone. *(Google: Looking For — Good Things)*

13. **Respond within one business day, even if only to schedule the full review.** A short message ("seeing this, full review tomorrow morning") unblocks the author socially even if the review itself takes longer. Silence is the worst response. *(Google: Speed of Code Reviews)*

14. **Verify the CL description.** The first line should be imperative and stand alone (`Add retry to webhook delivery`, not `Adding retry`). The body should explain why, not just what. Reject `"fix bug"`, `"phase 1"`, `"address feedback"`. The description is permanent project history. *(Google: Writing Good CL Descriptions)*

15. **Push back on speculative complexity.** "We might need this later" is a reason to delete code, not add it. Watch for premature interfaces, configuration knobs nobody requested, and abstractions for a single caller. Complexity earned by a current need is fine; complexity for a future hypothesis is not. *(Google: Looking For — Complexity)*

## Process

Walk this in order. Skipping steps produces shallow reviews.

1. **Read the description.** Note the stated intent in one sentence. If you cannot, the description fails Rule 14 — comment on it before reading code.
2. **List the changed files.** Group by logical area (production, test, config, docs).
3. **Read each changed file in full.** Not just the diff. Note its responsibilities.
4. **Re-read the diff with that context.** Now the changes are interpretable.
5. **Run the rules in order.** Mentally pass over Rules 1–15. Generate comments as findings appear.
6. **Categorize and label severity.** Group findings into Blockers, Suggestions, Nits, FYIs.
7. **Verify success criteria.** Re-read this skill's `success_criteria` block. Each item should be answerable with "yes."
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

If no comments fall in a category, omit the section. Always include `Summary` and `Things done well`.

## Examples

The following pairs each show a common AI failure followed by the correct pattern. Languages vary intentionally — the rules are universal.

### Example 1: severity calibration

A reviewer flags a style preference as a blocker.

**Common AI failure:**

```text
- src/handlers/user.py:42 — This function name should be `get_user_by_id`,
  not `fetch_user`. Please change before merging.
```

Why this fails: the project has no rule on `get_` vs `fetch_`. Treating personal preference as a blocker violates Rule 11 (style-guide authority) and Rule 3 (severity must reflect actual impact).

**Correct pattern:**

```text
- src/handlers/user.py:42 — nit: the rest of this module uses `get_*` for
  read accessors (see `get_session`, `get_role`). Renaming to `get_user_by_id`
  would make this consistent. Optional.
```

Why this works: the comment cites a real local convention, marks the severity honestly as `nit:`, and explicitly lets the author decline.

---

### Example 2: code-not-developer phrasing

A reviewer addresses the author rather than the code.

**Common AI failure:**

```text
- src/auth/session.ts:88 — Why did you use a global mutable map for the
  session cache? Did you not consider concurrency at all?
```

Why this fails: violates Rule 4. The phrasing makes the author defend a choice instead of evaluating the code. Also lacks reasoning per Rule 5.

**Correct pattern:**

```text
- src/auth/session.ts:88 — blocker: this session cache is a module-level
  mutable map without synchronization. Under concurrent requests (which
  this service handles per the deployment config), a read during write can
  return a partial entry. A `Map` wrapped in a per-key lock, or a request-
  scoped cache, would avoid this. The concurrency model is the issue, not
  caching itself.
```

Why this works: focuses on the code's behavior under the system's actual conditions, names the failure mode, and offers two alternatives without prescribing one.

---

### Example 3: reading the diff vs. the file

A reviewer comments only on the diff and misses the surrounding context.

**Common AI failure:**

```sql
-- Diff shows:
-  WHERE created_at > now() - interval '7 days'
+  WHERE created_at > now() - interval '30 days'

-- Reviewer says:
-- looks fine, just a wider window.
```

Why this fails: the diff is fine in isolation. But the file (unread) shows this query feeds a dashboard with a hard-coded `LIMIT 10000`. Widening from 7 to 30 days will silently truncate at the limit on busy customers. Violates Rule 1.

**Correct pattern:**

```text
- analytics/queries/recent_events.sql:14 — blocker: widening to 30 days
  exceeds the `LIMIT 10000` on line 22 for tenants over ~333 events/day
  (we have 14 such tenants per the metrics dashboard). Either bump the
  limit, page the query, or keep the 7-day window. The change as-is will
  silently drop rows from the dashboard for those tenants.
```

Why this works: catches the failure mode that only appears when the file is read in full, names the affected population, and proposes three alternatives.

---

### Example 4: tests for behavior, not for show

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

Why this works: explicitly applies the "would the test fail if the code were reverted?" check from Rule 8 and names the precise mock setup that would make it real.

---

### Example 5: comments that explain why, not what

A reviewer accepts a comment that paraphrases the next line.

**Common AI failure:**

```python
# Increment the retry counter
retry_count += 1
```

Comment passes review, no flag.

Why this fails: the comment adds zero information. Violates Rule 10 — comments should carry context the code lacks.

**Correct pattern:**

```text
- src/queue/worker.py:104 — nit: this comment paraphrases the line below
  it. If the intent is to flag *why* we increment here (e.g. "increment
  before sleep so a crash mid-sleep doesn't undercount"), say that.
  Otherwise the comment can go.
```

Why this works: distinguishes the case where the comment carries hidden context (keep, but rewrite) from the case where it doesn't (delete).

## Anti-patterns

Things reviewers commonly do that this skill exists to prevent:

- **Approving without reading.** "LGTM" with no evidence of having read the change. Violates Rule 1 and undermines Rule 13 (speed should not come from skipping work).
- **Inventing house style.** Asserting a rule the project doesn't actually have. Violates Rule 11.
- **Bikeshedding.** Long threads about variable names while a real correctness issue goes uncommented. Misallocates Rule 3.
- **Punitive nitpicking.** Listing every small imperfection as a blocker to demonstrate thoroughness. Violates Rules 2 and 3.
- **Buried security concerns.** A serious vulnerability mentioned offhandedly mid-review without a `blocker:` tag. Violates Rule 9.
- **Silent reviews.** Sitting on a CL for days without acknowledgment. Violates Rule 13.
- **Dictating the fix.** Telling the author exactly how to rewrite a function when multiple valid options exist. Violates Rule 6.

## Sources

Each rule above traces to one or more of these references. Where multiple sources agree, the rule is high-confidence; where only one does, it is flagged.

- **Google, Engineering Practices — Code Review Developer Guide** ([eng-practices](https://github.com/google/eng-practices); rendered at https://google.github.io/eng-practices/review/)
  - [Standard of Code Review](https://google.github.io/eng-practices/review/reviewer/standard.html) — informs Rules 2, 11.
  - [What to Look For](https://google.github.io/eng-practices/review/reviewer/looking-for.html) — informs Rules 1, 8, 10, 12, 15.
  - [How to Write Code Review Comments](https://google.github.io/eng-practices/review/reviewer/comments.html) — informs Rules 3, 4, 5, 6.
  - [Speed of Code Reviews](https://google.github.io/eng-practices/review/reviewer/speed.html) — informs Rule 13.
  - [Small CLs](https://google.github.io/eng-practices/review/developer/small-cls.html) — informs Rule 7.
  - [Writing Good CL Descriptions](https://google.github.io/eng-practices/review/developer/cl-descriptions.html) — informs Rule 14.

- **Microsoft, Engineering Fundamentals Playbook — Code Reviews** ([code-with-engineering-playbook](https://github.com/microsoft/code-with-engineering-playbook); rendered at https://microsoft.github.io/code-with-engineering-playbook/code-reviews/) — agrees with the Google guidance and explicitly cites Google as the canonical reference. Cross-references Rules 1, 2, 3, 4, 5, 13.

- **OWASP Top 10** ([https://owasp.org/Top10/](https://owasp.org/Top10/)) — informs Rule 9. Reviewers should be alert to the categories OWASP enumerates (broken access control, cryptographic failures, injection, insecure design, etc.) when reading any code that touches authn/authz, network input, persistence, or deserialization.

Cross-reference confidence:

- Rules 1, 2, 3, 4, 5, 13 — agreed across Google and Microsoft. High confidence.
- Rules 6, 7, 8, 10, 11, 12, 14, 15 — sourced primarily to Google. High confidence individually given Google's depth on each topic, but flagged as single-source.
- Rule 9 — sourced to OWASP for the security categories themselves; the meta-rule (flag with explicit severity) is universal across review guides.
