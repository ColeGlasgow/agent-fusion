from __future__ import annotations

import logging
from typing import Optional

from fastapi import FastAPI, Header, HTTPException, Response, status

from models import Task, TaskCreate
from settings import settings
from storage import IdempotencyConflictError, TaskConflictError, TaskStore

IDEMPOTENCY_KEY_HEADER = "Idempotency-Key"
MISSING_REQUEST_ID = "missing"
REQUEST_ID_HEADER = "X-Request-ID"

log = logging.getLogger(__name__)
app = FastAPI(title=settings.app_name)
store = TaskStore()


@app.post("/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(
    body: TaskCreate,
    response: Response,
    idempotency_key: Optional[str] = Header(default=None, alias=IDEMPOTENCY_KEY_HEADER),
    request_id: str = Header(default=MISSING_REQUEST_ID, alias=REQUEST_ID_HEADER),
) -> Task:
    try:
        task, created = store.create(body, idempotency_key)
    except IdempotencyConflictError as exc:
        log.info("task idempotency conflict", extra={"request_id": request_id})
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    except TaskConflictError as exc:
        log.info("task conflict", extra={"request_id": request_id})
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc

    if not created:
        response.status_code = status.HTTP_200_OK
    log.info("task persisted", extra={"request_id": request_id, "task_id": task.id})
    return task
