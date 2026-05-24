# A/B skill benchmark - Codex

This sequential A/B run compares two implementations of the same small FastAPI task service: `unskilled/`, produced before the benchmark step loaded the repository skill files, and `skilled/`, produced after reading `code-generation` plus `python-backend`. The score below judges the committed artifacts only; a passing test run is useful evidence, but each skill rule is scored against concrete code or report lines.

## Scoring

| Rule | Unskilled | Skilled |
|------|-----------|---------|
| code-generation 1. Verify APIs, imports, and paths | pass - `unskilled/main.py:4` imports FastAPI and HTTPException; `unskilled/main.py:5` imports BaseModel and pytest loads them. | pass - `skilled/main.py:6` imports FastAPI, Header, Response, and status; captured pytest imports the app successfully. |
| code-generation 2. Minimum code for the problem | pass - `unskilled/main.py:22` defines the only route and `unskilled/main.py:24` uses a direct in-memory loop. | pass - `skilled/storage.py:17` isolates only the store needed for task persistence, conflicts, and idempotent retries. |
| code-generation 3. Match project style and conventions | partial - `unskilled/main.py:23` leaves the public handler without a return type. | pass - `skilled/main.py:22` has a typed public handler and `skilled/models.py:6` keeps schemas in a dedicated model module. |
| code-generation 4. Do not enlarge scope | pass - `unskilled/main.py:22` implements only `POST /tasks`. | pass - `skilled/main.py:21` implements only `POST /tasks`; idempotency is tied to the skill's POST retry rule. |
| code-generation 5. Tests fail if behavior is reverted | partial - `unskilled/test_main.py:12` tests success and `unskilled/test_main.py:25` tests validation, but no test covers conflict handling. | pass - `skilled/test_main.py:12` tests success, `skilled/test_main.py:26` validation, `skilled/test_main.py:35` conflict, and `skilled/test_main.py:45` idempotent retry. |
| code-generation 6. Security-sensitive boundaries handled | partial - `unskilled/main.py:13` uses a Pydantic model, but `unskilled/main.py:14` accepts an empty title. | pass - `skilled/models.py:7` constrains title length and `skilled/main.py:23` accepts a schema before business logic. |
| code-generation 7. Names explain intent; avoid magic literals | partial - `unskilled/main.py:22` and `unskilled/main.py:26` use raw numeric status codes. | pass - `skilled/main.py:12` names the idempotency header and `skilled/main.py:21` uses FastAPI status constants. |
| code-generation 8. Handle unhappy paths explicitly | partial - `unskilled/main.py:26` handles duplicate conflicts, but there is no narrow domain exception. | pass - `skilled/main.py:30` catches IdempotencyConflictError and `skilled/main.py:33` catches TaskConflictError separately. |
| code-generation 9. Functions stay focused | pass - `unskilled/main.py:23` keeps the route small, with one persistence branch. | pass - `skilled/storage.py:26` owns persistence and `skilled/main.py:22` owns HTTP translation. |
| code-generation 10. Surface uncertainty | fail - `unskilled/main.py:25` defines duplicate title/date as the conflict rule without documenting that assumption. | pass - `skilled/ASSUMPTIONS.md:3` documents the conflict definition and `skilled/ASSUMPTIONS.md:4` documents idempotency behavior. |
| python-backend 1. Complete type-annotated public signatures | partial - `unskilled/main.py:23` omits the handler return type and `unskilled/settings.py:5` omits `__init__` annotations. | pass - `skilled/main.py:22` returns `Task`, `skilled/storage.py:22` returns `None`, and `skilled/storage.py:26` returns `tuple[Task, bool]`. |
| python-backend 2. Validate inputs with a schema | pass - `unskilled/main.py:13` defines TaskCreate as a Pydantic model before handler logic. | pass - `skilled/models.py:6` defines TaskCreate with typed fields and `skilled/models.py:7` adds title bounds. |
| python-backend 3. HTTP semantics and idempotency | partial - `unskilled/main.py:22` returns 201 and `unskilled/main.py:26` returns 409, but POST retries can still duplicate without an idempotency key. | pass - `skilled/main.py:21` returns 201 on create, `skilled/main.py:37` returns 200 on replay, and `skilled/storage.py:38` stores idempotency keys. |
| python-backend 4. No blocking IO in async handlers | pass - `unskilled/main.py:23` uses a sync handler, so no event loop can be blocked. | pass - `skilled/main.py:22` uses a sync handler, so there is no async event loop path. |
| python-backend 5. Structured logging with correlation ID | fail - `unskilled/main.py:1` through `unskilled/main.py:31` contain no logging. | pass - `skilled/main.py:16` creates a module logger and `skilled/main.py:39` logs request_id and task_id. |
| python-backend 6. Typed settings from environment | fail - `unskilled/settings.py:4` is a hand-written class and `unskilled/settings.py:6` reads os.getenv directly. | pass - `skilled/settings.py:4` defines Settings as BaseSettings and `skilled/settings.py:7` configures an environment prefix. |

## What changed

- The skilled run split schemas, storage, settings, and HTTP translation into focused modules; the unskilled run put everything in `main.py`.
- The skilled run made the conflict assumption explicit and added idempotency behavior for safe POST retries.
- The skilled run improved validation from "date parses" to a bounded title schema plus date parsing.
- The skilled run added structured logs with `request_id`, while the unskilled run emitted no logs.
- The skilled run tested conflict and idempotency behavior; the unskilled run tested only success and validation.

## What did not change

- Both runs produced a working FastAPI service with in-memory persistence and server-generated IDs.
- Both runs used Pydantic request models and let FastAPI return 422 for malformed input.
- Both runs avoided `async def`, so neither introduced sync IO inside an async handler.

## Verdict

The skills earned their tokens on this task: they did not change the core endpoint, but they moved the output from a working toy service toward an auditable backend artifact with explicit assumptions, stronger validation, safer retry semantics, logging, and broader tests.
