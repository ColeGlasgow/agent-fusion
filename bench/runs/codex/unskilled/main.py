from datetime import date
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from settings import settings

app = FastAPI(title=settings.app_name)
tasks = {}


class TaskCreate(BaseModel):
    title: str
    due_date: date


class Task(TaskCreate):
    id: str


@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task: TaskCreate):
    for existing in tasks.values():
        if existing["title"] == task.title and existing["due_date"] == task.due_date:
            raise HTTPException(status_code=409, detail="task already exists")

    task_id = str(uuid4())
    saved = {"id": task_id, "title": task.title, "due_date": task.due_date}
    tasks[task_id] = saved
    return saved
