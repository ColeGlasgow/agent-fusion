---
name: code-generation
description: Write new code or modify existing code to meet enterprise quality standards. Language-agnostic foundation; language-specific skills extend this via `requires:`.
preferred_models:
  - claude-opus
  - claude-sonnet
allowed_tools: []
success_criteria:
  - Every API, import, and file path used has been verified to exist in the project or its declared dependencies
  - The change is the minimum necessary to solve the stated problem
  - Existing project style and conventions have been matched, not overridden
  - Tests cover the new behavior and would fail if the change were reverted
  - Security-sensitive boundaries (input, auth, secrets, persistence) are handled explicitly
  - The unhappy path is handled — errors caught narrowly, resources closed deterministically
  - Names communicate intent; comments, if any, explain why
  - Uncertainty has been surfaced, not hidden behind plausible-sounding code
  - Documentation invalidated by the change has been updated in the same commit
tags:
  - coding
  - quality
  - foundation
---

# Code generation

Foundation skill for writing or modifying code in any language. Citations for every rule below live in `code-generation.sources.md` next to this file.

## When to use

Writing new code, modifying existing code, or producing a code change in response to a task. Not for reviewing code (use `pr-review`) or pure research/analysis.

## Rules

1. **Verify every API, import, and path before using it.** If you cannot point to where a function, package, or file exists, do not call it. Hallucinated APIs are the single most common failure mode of generated code. When unsure, read the file or check the dependency list before writing.

2. **Write the minimum code that solves the stated problem.** Nothing speculative. No "we might need this later" abstractions, configuration knobs nobody requested, or interfaces with one implementation. Complexity earned by a current requirement is fine; complexity for a hypothetical future is not.

3. **Match existing project style and conventions.** Read a neighboring file before writing a new one. Follow the linter and style guide the project already enforces. If your preference conflicts with the project, the project wins.

4. **Do not enlarge scope beyond what the task asked for.** One logical change per commit. Do not fix unrelated issues, reformat untouched code, or refactor things that are not broken. Note unrelated problems for a follow-up; do not include them.

5. **Write tests that would fail if the change were reverted.** A test exercising only the pre-existing success path is decoration. The test must directly cover the new behavior — new branch, new error case, new output — so reverting the production change breaks the test.

6. **Handle security at every system boundary.** Input from users, network, or files must be validated. Secrets are never hardcoded. SQL and shell commands are parameterized, not interpolated. Auth, crypto, deserialization, and file paths get explicit attention or an explicit `TODO` flag. Do not invent crypto.

7. **Names communicate intent; comments explain *why*; no magic literals.** Use descriptive names long enough to be self-evident in their scope. Reserve comments for non-obvious context — a constraint, an invariant, a workaround — not for paraphrasing the next line. A literal that carries meaning (`86400`, `"admin"`, `0x1F`) gets a named constant; trivially obvious values (`0`, `1`, empty string) do not.

8. **Handle the unhappy path explicitly.** Catch the specific exception you can recover from, at the layer that can recover — never `except:`, never empty `catch` blocks, never swallow errors silently. Files, sockets, locks, transactions, and database connections must close on every path including errors; use the language's resource-scoping construct (context manager, `using`, RAII, `defer`, `try-with-resources`), not garbage collection.

9. **Functions stay focused.** One responsibility per function. Roughly 40 lines is a soft ceiling — past it, the function is usually doing two things and should be split. Long parameter lists are the same signal.

10. **Surface uncertainty; do not paper over it.** If a requirement is ambiguous, state the assumption and ask. If an API contract is unknown, read it or say so. Plausible-sounding code generated under uncertainty is worse than a question, because it looks like a working answer.

## Process

1. **Restate the task in one sentence.** If you cannot, the task is underspecified — ask before writing.
2. **Read the surrounding code.** Open the file you will modify and at least one neighboring file. Identify existing conventions.
3. **Identify the minimum surface.** What files must change? What can stay the same? Resist enlarging the surface.
4. **Plan the change.** A 1–5 line plan stating files, what changes in each, and what tests will prove it works.
5. **Write the change.** Apply Rules 1–10 as you go.
6. **Write or update tests.** Apply Rule 5 — mentally run the test against the reverted code; it should fail.
7. **Update invalidated documentation.** Signatures, READMEs, config tables, CL descriptions.
8. **Verify `success_criteria`.** Each item answerable with "yes."
9. **Summarize in the output format below.**

## Output format

```markdown
## Change summary
<one paragraph: what changed and why>

## Files modified
- `path/to/file.ext` — <what changed>

## Tests
- `path/to/test.ext` — <what is covered, and why this test would fail if the change were reverted>

## Assumptions and uncertainty
- <any assumption made, any question the author should confirm>

## Out of scope
- <related things deliberately not changed, with one-line reason>
```

Omit `Assumptions` and `Out of scope` only if genuinely empty. Never omit `Tests` — if no test was written, state why explicitly.

## Examples

Each pair shows a common AI failure followed by the correct pattern. Languages vary intentionally — the rules are universal.

### Example 1: speculative complexity

Task: "Add a function that formats a user's full name as `Last, First`."

**Common AI failure:**

```python
class NameFormatter:
    def __init__(self, separator: str = ", ", order: str = "last_first",
                 locale: str | None = None, fallback: str = ""):
        self.separator = separator
        self.order = order
        self.locale = locale
        self.fallback = fallback

    def format(self, user: User) -> str:
        if self.order == "last_first":
            return f"{user.last_name}{self.separator}{user.first_name}"
        elif self.order == "first_last":
            return f"{user.first_name} {user.last_name}"
        # ... locale handling, fallback handling, etc.
```

Why this fails: a class, four configuration knobs, two order modes, and locale handling — none of which were asked for. Single caller, single format. Violates Rule 2 (minimum code) and Rule 9 (focus).

**Correct pattern:**

```python
def format_last_first(user: User) -> str:
    return f"{user.last_name}, {user.first_name}"
```

Why this works: solves exactly the stated problem in one obvious line. If a second format is ever needed, add a second function then — the second caller will reveal what the abstraction should look like.

---

### Example 2: insecure string interpolation

Task: "Add an endpoint that looks up an order by its ID from the database."

**Common AI failure:**

```python
@app.get("/orders/{order_id}")
def get_order(order_id: str):
    query = f"SELECT * FROM orders WHERE id = '{order_id}'"
    return db.execute(query).fetchone()
```

Why this fails: `order_id` is user input interpolated directly into SQL. An attacker sends `1' OR '1'='1` and reads every row. Errors are also unhandled — a malformed ID surfaces a stack trace to the client. Violates Rule 6 (security at boundaries) and Rule 8 (handle the unhappy path).

**Correct pattern:**

```python
@app.get("/orders/{order_id}")
def get_order(order_id: str) -> Order:
    if not ORDER_ID_PATTERN.fullmatch(order_id):
        raise HTTPException(status_code=400, detail="invalid order id")
    try:
        row = db.execute(
            "SELECT * FROM orders WHERE id = :id",
            {"id": order_id},
        ).fetchone()
    except DatabaseError:
        log.exception("order lookup failed", extra={"order_id": order_id})
        raise HTTPException(status_code=503, detail="order lookup failed")
    if row is None:
        raise HTTPException(status_code=404)
    return Order.from_row(row)
```

Why this works: input is validated against a known pattern (Rule 6), the query uses parameter binding the driver escapes (Rule 6), the `except` catches only `DatabaseError` so unrelated bugs still surface (Rule 8), and the not-found case is distinct from the error case so the client sees the right status.
