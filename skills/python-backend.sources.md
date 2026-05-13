# python-backend — sources

Audit trail for `python-backend.md`. Not loaded at runtime. Update this file whenever a rule is added, changed, or removed.

`python-backend` extends `code-generation` via `requires:`. Foundation rules (verify APIs, minimum code, match style, scope, tests-that-fail-when-reverted, boundary security, naming/comments, unhappy path, focused functions, surface uncertainty) are inherited and not re-sourced here.

## References

- **Google, Python Style Guide** ([pyguide](https://google.github.io/styleguide/pyguide.html))
  - [§3.19 Type Annotations](https://google.github.io/styleguide/pyguide.html#319-type-annotations) — public APIs should be annotated; annotations enable static analysis and tooling.
  - [§2.21 Logging](https://google.github.io/styleguide/pyguide.html#2161-logging) — always use the `logging` module, prefer `%`-style or structured fields over f-strings, log exceptions with `log.exception`.

- **PEP 484 — Type Hints** ([peps.python.org/pep-0484](https://peps.python.org/pep-0484/)) — canonical reference for the type-hint system Python frameworks build on.

- **RFC 9110 — HTTP Semantics** ([rfc-editor.org/rfc/rfc9110](https://www.rfc-editor.org/rfc/rfc9110.html))
  - [§9.2.2 Idempotent Methods](https://www.rfc-editor.org/rfc/rfc9110.html#section-9.2.2) — GET, HEAD, OPTIONS, TRACE, PUT, DELETE are idempotent; POST is not.
  - [§15 Status Codes](https://www.rfc-editor.org/rfc/rfc9110.html#section-15) — 2xx success, 4xx client error (401 unauthenticated, 403 forbidden, 404 not found, 422 unprocessable), 5xx server error.

- **Python `asyncio` documentation** ([docs.python.org/3/library/asyncio.html](https://docs.python.org/3/library/asyncio.html)) — the event-loop model and the contract that blocking calls inside coroutines stall the loop.
  - [Running blocking code in a thread](https://docs.python.org/3/library/asyncio-task.html#asyncio.to_thread) — `asyncio.to_thread` is the prescribed escape hatch for sync IO inside async code.

- **FastAPI — Concurrency and async/await** ([fastapi.tiangolo.com/async](https://fastapi.tiangolo.com/async/)) — explicit guidance that `async def` handlers must not perform blocking IO; if the library is sync, declare the handler `def`, not `async def`.

- **OWASP Secure Coding Practices Quick Reference Guide** ([project page](https://owasp.org/www-project-secure-coding-practices-quick-reference-guide/)) — Input Validation section: validate at the trust boundary against a schema, reject before processing.

- **OWASP Cheat Sheet — Logging** ([cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)) — never log secrets or full PII; correlate logs with request identifiers.

- **The Twelve-Factor App** ([12factor.net](https://12factor.net/))
  - [III. Config](https://12factor.net/config) — config in the environment, strict separation from code, no environment-conditional literals.

- **Microsoft, Engineering Fundamentals Playbook** ([repo](https://github.com/microsoft/code-with-engineering-playbook))
  - [Observability](https://microsoft.github.io/code-with-engineering-playbook/observability/) — structured logs, correlation IDs across service boundaries.

## Rule-by-rule sourcing

| Rule | Source(s) | Confidence |
|------|-----------|------------|
| 1. Type-annotated public signatures | Google Python Style Guide §3.19; PEP 484 | High (cross-sourced) |
| 2. Validate inputs with a schema | OWASP SCP (input validation); framework canon (Pydantic / marshmallow / DRF serializers) | High |
| 3. HTTP semantics — status codes match outcomes; idempotent verbs stay idempotent | RFC 9110 §15 and §9.2.2 | High (single authoritative source) |
| 4. No blocking IO in `async def` handlers | Python `asyncio` docs; FastAPI Concurrency guide; AI-failure-mode synthesis | High (cross-sourced) |
| 5. Structured logging via `logging`, with correlation IDs, no secrets | Google Python Style Guide §2.21; OWASP Logging Cheat Sheet; Microsoft Observability | High (cross-sourced) |
| 6. Typed settings + env-based config | Twelve-Factor §III; OWASP SCP (system configuration) | High (cross-sourced) |

## Notes

- Six rules, deliberately. The foundation (`code-generation`) already carries verification, minimum-code, security-at-boundaries, unhappy-path handling, and function-focus rules; repeating them here would burn tokens at composition time. Each rule below is something `code-generation` does not say or cannot say in language-agnostic form.
- Rule 3 merges HTTP status semantics and idempotency. They share a citation (RFC 9110) and a single failure mode (the API contract is unclear to clients). Splitting them into two rules added length without changing behavior.
- Rule 4 has the strongest AI-failure-mode component. Sync-in-async is the highest-impact, hardest-to-detect Python-backend mistake LLMs make: the code looks correct, tests pass at low concurrency, and the failure surfaces only under production load. The canonical sources (asyncio docs, FastAPI docs) describe the mechanism; the rule formulation here addresses the AI-specific failure pattern.
- Process and Output format sections are deliberately omitted. They are inherited from `code-generation` through `requires:` composition. Duplicating them would burn ~30 lines at every load.
- Examples cover Rules 2, 3, 4, 5, 6 (the async/httpx example pulls in five rules' worth of correct patterns; the login example covers schema validation and status semantics). Rule 1 (type hints) is covered implicitly in every example. No standalone example for Rule 1 — type annotations alone are not a failure mode worth a 30-line example, they are a default state the other examples demonstrate.
- `pydantic-settings`, `dynaconf`, and `structlog` are named in rule text as concrete options, not pinned. The framework world moves; the principle (typed settings from env; structured logging) is stable.
