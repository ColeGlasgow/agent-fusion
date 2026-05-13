---
name: python-backend
description: Build Python HTTP API backends to enterprise standards. Extends `code-generation` with Python and web-API specifics.
preferred_models:
  - claude-opus
  - claude-sonnet
allowed_tools:
  - filesystem.write
requires:
  - code-generation
success_criteria:
  - Every public function has a complete type-annotated signature, return type included
  - Request inputs are validated by a schema (Pydantic, marshmallow, attrs) before reaching business logic
  - HTTP status codes match outcomes; success bodies do not carry error envelopes
  - Idempotent verbs (GET, PUT, DELETE) are safe to retry
  - No blocking IO runs inside an `async def` handler
  - Logs are structured with `logging` and include a request or trace identifier
  - URLs, credentials, and feature flags are loaded from a typed settings object, not literals
tags:
  - python
  - backend
  - api
  - web
paths:
  - "**/*.py"
---

# Python backend

Specialization of `code-generation` for Python HTTP API services. The foundation rules apply unchanged; the rules below add what is specific to Python and to web APIs. Citations live in `python-backend.sources.md` next to this file.

## When to use

Writing or modifying a Python HTTP API — handler functions, request/response schemas, routing, middleware, persistence, or background work invoked from a web layer. Applies whether the framework is FastAPI, Flask, Django, Starlette, or no framework. Not for non-web Python (CLIs, data pipelines, libraries) — those belong to a different specialization or to `code-generation` alone.

## Rules

1. **Every public function has a complete type-annotated signature.** Parameters and return type. Type hints are how Python frameworks (Pydantic, FastAPI, SQLAlchemy 2.x, dataclasses) generate schemas, dependency wiring, and editor help; leaving them off forfeits half the language's static-analysis surface. Internal helpers may skip return types when the value is obviously throwaway; public handlers, service functions, and module-level functions may not.

2. **Validate request inputs with a schema before they reach business logic.** Use the framework's native schema layer — Pydantic for FastAPI, marshmallow or attrs for Flask, serializers for DRF. Do not hand-roll `isinstance` chains in handlers, do not call `.get(...)` on raw dicts, do not trust query parameters or JSON bodies as-is. Schema validation gives you typed objects, consistent 4xx responses, and a single audit point for input handling.

3. **HTTP semantics match outcomes.** Success responses use 2xx and carry the resource, not an error envelope. 4xx means the client must change something; 5xx means the server failed. Distinguish 401 (not authenticated) from 403 (authenticated, not allowed) and 404 (resource missing) from 422 (input malformed). Idempotent verbs — GET, PUT, DELETE — must be safe to call twice with the same effect; POST is the only verb where retry can create duplicates, and that is the verb where you need idempotency keys.

4. **Do not block the event loop inside an `async def` handler.** Synchronous IO — `requests.get`, `time.sleep`, blocking DB drivers, file reads — freezes every concurrent request on the same worker until it returns. If a handler is `async`, every IO call inside it must be async too; if the only client you have is sync, either run the whole handler sync or push the sync call onto a thread pool with `asyncio.to_thread`. Mixing sync and async silently destroys throughput, and the failure mode is invisible until load.

5. **Logs are structured, correlated, and not `print()`.** Use the standard `logging` module (or a structured wrapper like `structlog`), not `print`. Attach a request or trace identifier to every log line so a single request can be reconstructed across services. Log exceptions with `log.exception(...)` so the traceback is captured. Do not log secrets, full request bodies, or PII — log identifiers and decisions, not payloads.

6. **Configuration loads from a typed settings object backed by environment variables.** No URLs, credentials, feature flags, or environment-conditional logic as literals in handler code. Use `pydantic-settings`, `dynaconf`, or an equivalent typed loader; secrets come from the environment or a secrets manager, never the repo. A single `Settings` instance is read at startup and injected — not re-read per request, not imported globally from a constants module.

## Examples

### Example 1: blocking IO in an async handler

Task: "Add an endpoint that fetches the latest exchange rate from an internal pricing service and returns it."

**Common AI failure:**

```python
import requests
from fastapi import FastAPI

app = FastAPI()

@app.get("/rates/{currency}")
async def get_rate(currency: str) -> dict:
    response = requests.get(f"http://pricing.internal/rates/{currency}")
    return response.json()
```

Why this fails: `requests.get` is synchronous. Inside `async def`, it blocks the event loop until the upstream returns. Every other concurrent request on this worker — health checks, unrelated endpoints, websocket pings — stalls behind this call. Under any real concurrency the service falls over, and the only symptom is mysterious latency spikes. The code looks correct, the tests pass at low concurrency, the failure mode appears only in production. Violates Rule 4.

**Correct pattern:**

```python
import httpx
from fastapi import FastAPI, HTTPException

from .settings import settings

app = FastAPI()

@app.get("/rates/{currency}")
async def get_rate(currency: str) -> Rate:
    async with httpx.AsyncClient(timeout=settings.pricing_timeout_s) as client:
        try:
            response = await client.get(f"{settings.pricing_base_url}/rates/{currency}")
            response.raise_for_status()
        except httpx.HTTPError:
            log.exception("pricing lookup failed", extra={"currency": currency})
            raise HTTPException(status_code=503, detail="pricing unavailable")
    return Rate.model_validate(response.json())
```

Why this works: `httpx.AsyncClient` is awaitable, so the worker yields to other requests while the call is in flight. The timeout comes from typed settings (Rule 6), the upstream failure is logged with context (Rule 5) and mapped to a 503 (Rule 3), and the response is validated through a Pydantic model (Rule 2) before the handler returns it.

---

### Example 2: 200 OK carrying an error

Task: "Add a login endpoint. If the password is wrong, return an error to the client."

**Common AI failure:**

```python
@app.post("/login")
async def login(body: dict) -> dict:
    user = await users.find(body["email"])
    if user is None or not user.verify(body["password"]):
        return {"ok": False, "error": "invalid credentials"}
    return {"ok": True, "token": issue_token(user)}
```

Why this fails: returns HTTP 200 with an error envelope — every client, every load balancer, every monitoring dashboard sees the request as successful. Bad-credential attempts cannot be rate-limited at the edge because they do not look failed. The raw `dict` body skips schema validation, so a missing `password` key raises `KeyError` and produces a 500 instead of a 400. Violates Rules 2 and 3.

**Correct pattern:**

```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: SecretStr

class LoginResponse(BaseModel):
    token: str

@app.post("/login", response_model=LoginResponse)
async def login(body: LoginRequest) -> LoginResponse:
    user = await users.find(body.email)
    if user is None or not user.verify(body.password.get_secret_value()):
        log.info("login rejected", extra={"email": body.email})
        raise HTTPException(status_code=401, detail="invalid credentials")
    return LoginResponse(token=issue_token(user))
```

Why this works: the request is validated through `LoginRequest` (Rule 2) — missing fields produce a 422 automatically, and `SecretStr` keeps the password out of logs and repr output. Bad credentials raise a 401 (Rule 3) so the edge can rate-limit and dashboards count it as failed. The success response is typed (Rule 1) and carries only the token, not a status envelope.

---

### Example 3: POST retry creates duplicates

Task: "Add an endpoint that creates a payment for an order."

**Common AI failure:**

```python
@app.post("/payments")
async def create_payment(body: CreatePaymentRequest) -> Payment:
    payment = await payments.insert(
        order_id=body.order_id,
        amount=body.amount,
    )
    await gateway.charge(payment)
    return payment
```

Why this fails: this is a POST that creates a side effect, and nothing makes it safe to retry. The realistic failure path: the client's request times out after the charge succeeds but before the response is delivered. The client retries with the same body. The handler runs again, inserts a second payment, and charges the card a second time. The user is double-billed; reconciliation is manual. The handler obeys Rule 3's status-code clause but ignores its idempotency clause — POST is the verb where retry can create duplicates, which is exactly why it is the verb where you need an idempotency key.

**Correct pattern:**

```python
@app.post("/payments")
async def create_payment(
    body: CreatePaymentRequest,
    idempotency_key: str = Header(..., alias="Idempotency-Key"),
) -> Payment:
    existing = await payments.find_by_idempotency_key(idempotency_key)
    if existing is not None:
        if existing.request_fingerprint != body.fingerprint():
            raise HTTPException(status_code=409, detail="idempotency key reused with different body")
        return existing

    payment = await payments.insert(
        order_id=body.order_id,
        amount=body.amount,
        idempotency_key=idempotency_key,
        request_fingerprint=body.fingerprint(),
    )
    await gateway.charge(payment)
    return payment
```

Why this works: the client supplies an `Idempotency-Key` header; the handler looks it up before doing any side effect, returns the prior result if it matches, and rejects with 409 if the same key is reused with a different body. A retry with the same key returns the original payment without re-charging. The dedup column is enforced by a unique index on `(idempotency_key)` in the schema so a race between two concurrent retries cannot both insert. POST is now safe to retry, satisfying Rule 3's idempotency clause without changing the verb.
