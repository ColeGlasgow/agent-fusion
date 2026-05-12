---
name: debugging
description: Diagnose and fix broken code by isolating root causes rather than patching symptoms. Language-agnostic foundation; pairs with pr-review and code-generation.
preferred_models:
  - claude-opus
  - claude-sonnet
allowed_tools:
  - filesystem.write
  - shell.exec
success_criteria:
  - The bug has been reproduced before any fix was attempted
  - The root cause has been named, not just the symptom site
  - Only one change was made at a time when testing hypotheses
  - Recent changes (git log, deploys, config) were checked before deep investigation
  - The error message and stack trace were read in full, not pattern-matched
  - The fix has been verified by re-running the reproduction
  - A regression test has been added that fails against the original buggy code
  - Correlation was not treated as causation when multiple things changed together
tags:
  - debugging
  - quality
  - foundation
---

# Debugging

Foundation skill for diagnosing and fixing broken code in any language. Citations for every rule live in `debugging.sources.md` next to this file.

## When to use

A reported bug, a failing test, an incident, or any "this isn't working the way it should." Not for writing new code (use `code-generation`) or reviewing changes (use `pr-review`).

## Rules

1. **Reproduce before fixing.** A bug you cannot reproduce on demand is a bug you cannot prove you fixed. Reproduction comes first — the smallest input that triggers the failure, the exact command, the exact environment. If the reproduction takes ten minutes to set up, build it anyway; every subsequent step depends on it.

2. **Read the actual error and the full stack trace.** Do not pattern-match the exception type and skip the message. The specific message and the deepest frame inside *your* code (not framework internals) usually name the bug. Quote the relevant lines in your reasoning so it is clear you read them.

3. **The symptom is not the root cause.** The error surfaces where the system gave up, not where the bug lives. A `NoneType has no attribute 'name'` does not mean "wrap this in a null check" — it means "find out why `user` is None when this code is reached." Fix the cause, not the call site.

4. **Check recent changes before deep investigation.** Systems have inertia: code that worked yesterday and is broken today usually broke because *something changed*. Run `git log` on the affected files, check recent deploys, check config changes. The bug is more often in the last commit than in a deep architectural flaw.

5. **Form a hypothesis, then test it.** State an explicit "if X is the cause, then I should observe Y" prediction, then check Y. Random poking — "let me try this and see what happens" — burns time and creates the change-many-things-at-once trap.

6. **Change one thing at a time.** When testing a hypothesis or trying a fix, change exactly one variable. If you change three things and the bug goes away, you do not know which change fixed it — and one of the other two may have created a different bug you have not noticed yet.

7. **Do not confuse correlation with causation.** Two things changing together does not prove one caused the other. A deploy and an error spike at the same time is a starting hypothesis, not a conclusion. Verify by reverting, or by reproducing the failure without the suspected cause present.

8. **Bisect when the search space is large.** For "works at commit A, broken at commit B," use `git bisect`. For broken behavior somewhere in a long pipeline, log at the midpoint, then halve again. Bisection turns linear search into logarithmic search; do it before reading every file.

9. **Verify the fix actually fixed it.** Re-run the exact reproduction from Rule 1 and confirm the failure is gone. "It should work now" is not a fix; "I re-ran the failing case and it passes" is. If the reproduction was intermittent, run it enough times to be statistically confident.

10. **Add a regression test that fails against the original buggy code.** The bug got past the test suite; the suite has a gap. The fix is not complete until that gap is closed by a test which would have caught the bug before it shipped. Mentally revert your fix — the new test must fail.

## Process

1. **Restate the bug in one sentence.** Expected behavior, actual behavior, the trigger. If you cannot, the report is underspecified — ask for the missing piece.
2. **Reproduce the bug.** Build the smallest reliable reproduction. Save it; you will use it again.
3. **Read the full error and stack trace.** Identify the deepest frame inside the project's code.
4. **Check recent changes.** `git log --since="N days ago" -- <affected files>`, recent deploys, config changes.
5. **Form a hypothesis.** Write one explicit "if X, then Y" statement.
6. **Test the hypothesis.** Change one variable. Observe.
7. **Iterate.** If the hypothesis is wrong, form a new one with what you just learned — do not start guessing.
8. **Identify the root cause.** Name it explicitly, in one sentence. If you cannot, you are not done.
9. **Fix the cause.** The minimum change that addresses the root cause, not the symptom.
10. **Verify with the reproduction from step 2.**
11. **Add the regression test (Rule 10).**
12. **Summarize in the output format below.**

## Output format

```markdown
## Bug
<one sentence: expected vs. actual, with the trigger>

## Reproduction
<the exact steps or input that reliably triggers the bug>

## Root cause
<one sentence naming the actual cause, not the symptom site>

## Fix
- `path/to/file.ext` — <what changed and why this addresses the root cause>

## Regression test
- `path/to/test.ext` — <what is asserted, and confirmation that this test fails against the original buggy code>

## Hypotheses tested and rejected
- <hypothesis> — <how it was ruled out>
```

Include `Hypotheses tested and rejected` whenever more than one hypothesis was considered — it is part of the audit trail and prevents the same dead end being explored again.

## Examples

Each pair shows a common AI debugging failure followed by the correct pattern. Languages vary intentionally — the rules are universal.

### Example 1: fixing the symptom instead of the root cause

Bug: production logs show `AttributeError: 'NoneType' object has no attribute 'email'` in the order-confirmation handler.

**Common AI failure:**

```python
def send_confirmation(order: Order) -> None:
    user = users.get(order.user_id)
    if user is not None:  # added to silence the error
        send_email(user.email, render_confirmation(order))
```

Why this fails: the error stopped, but no order confirmations are being sent for affected users — a silent correctness regression worse than the original crash. The `AttributeError` was telling us "for some orders, `users.get(order.user_id)` returns `None`." That is the bug. Wrapping in a null check hides the symptom without explaining *why* a paid order has no associated user. Violates Rule 3 (symptom vs. root cause).

**Correct pattern:**

The fix begins with the diagnostic question, not a code change:

```text
1. Reproduce: pick an `order_id` from the error logs, call send_confirmation(order)
   in a shell — error reproduces.
2. Run: users.get(order.user_id) → None. Confirmed.
3. Check the DB: orders.user_id = 8421 exists; users.id = 8421 does not exist.
4. git log on users/repository.py: last week's "soft delete" migration set
   `users.deleted_at` and added a default filter to `users.get` that excludes
   soft-deleted users. Order 8421 belongs to a deleted user account.
5. Root cause: the order-confirmation handler does not account for orders
   placed by accounts that were later soft-deleted.
6. Fix the cause, not the call site.
```

```python
def send_confirmation(order: Order) -> None:
    user = users.get(order.user_id, include_deleted=True)
    if user is None:
        log.error("order has no associated user", extra={"order_id": order.id})
        raise OrphanedOrderError(order.id)
    send_email(user.email, render_confirmation(order))
```

Why this works: the root cause is explicit (soft-deleted users still need their order confirmations), the fix addresses it at the source (look up the user including deleted accounts), and the truly impossible case (orphaned order) raises loudly instead of being silently swallowed.

---

### Example 2: changing many things at once, then claiming it's fixed

Bug: integration test `test_payment_webhook` started failing intermittently this week. Passes about 70% of the time.

**Common AI failure:**

```text
I made the test more reliable. Changes:
- Added a 2-second sleep before the assertion to let the webhook process.
- Switched the HTTP client to a session-scoped fixture for connection reuse.
- Increased the database transaction isolation level to SERIALIZABLE.
- Retried the assertion up to 5 times.

The test passes now.
```

Why this fails: four changes at once, with no isolation of which one (if any) addressed the actual bug. The test "passes" but the underlying race condition or ordering issue is unidentified and may still cause failures in production. The retry loop in particular masks the bug rather than fixing it. Violates Rule 5 (hypothesize first), Rule 6 (one change at a time), and Rule 9 (verify the actual fix).

**Correct pattern:**

```text
1. Reproduce: run the test in a loop until it fails. ~30% failure rate confirmed.
2. Read the failure: assertion is "Payment.status == 'completed'" but actual
   value is 'pending'. Webhook is being received (log line present), but the
   status row update has not landed by the time the assertion runs.
3. Hypothesis A: the webhook handler commits the transaction asynchronously
   and the test's read happens before the commit lands. If true, polling for
   the expected status (with a timeout) should succeed; a fixed sleep should
   also succeed; SERIALIZABLE isolation would not change anything.
4. Test hypothesis A in isolation: replace the immediate assertion with a
   poll-for-status-with-timeout, change nothing else. Run 100 iterations.
   100/100 pass. Hypothesis confirmed.
5. Root cause: the test assumes synchronous webhook processing; the production
   handler is asynchronous. The test, not the production code, was wrong.
6. Fix: keep the poll-for-status helper; revert the other three changes I
   was tempted to make.
```

```python
def test_payment_webhook(client, db):
    response = client.post("/webhooks/payment", json=fixtures.completed_payment())
    assert response.status_code == 200

    payment = poll_until(
        lambda: db.get(Payment, payment_id),
        condition=lambda p: p.status == "completed",
        timeout=5.0,
    )
    assert payment.status == "completed"
```

Why this works: one hypothesis, isolated and tested. The diagnosis names *why* the test was flaky (async vs. sync mismatch) rather than masking it with retries. The other three "fixes" were thrown out because there was no evidence any of them addressed the actual cause.
