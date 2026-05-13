# Assumptions

- A conflict means an existing task has the same `title` and `due_date`.
- `Idempotency-Key` is optional. When present, retrying the same body returns the existing task; reusing the same key with a different body returns 409.
