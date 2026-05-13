from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from models import Task, TaskCreate


class TaskConflictError(ValueError):
    pass


class IdempotencyConflictError(ValueError):
    pass


@dataclass
class TaskStore:
    tasks: dict[str, Task] = field(default_factory=dict)
    idempotency_keys: dict[str, tuple[TaskCreate, str]] = field(default_factory=dict)

    def clear(self) -> None:
        self.tasks.clear()
        self.idempotency_keys.clear()

    def create(self, request: TaskCreate, idempotency_key: str | None) -> tuple[Task, bool]:
        if idempotency_key in self.idempotency_keys:
            previous_request, task_id = self.idempotency_keys[idempotency_key]
            if previous_request != request:
                raise IdempotencyConflictError("idempotency key reused with different body")
            return self.tasks[task_id], False

        if self._task_exists(request):
            raise TaskConflictError("task already exists")

        task = Task(id=str(uuid4()), title=request.title, due_date=request.due_date)
        self.tasks[task.id] = task
        if idempotency_key is not None:
            self.idempotency_keys[idempotency_key] = (request, task.id)
        return task, True

    def _task_exists(self, request: TaskCreate) -> bool:
        return any(
            task.title == request.title and task.due_date == request.due_date
            for task in self.tasks.values()
        )
