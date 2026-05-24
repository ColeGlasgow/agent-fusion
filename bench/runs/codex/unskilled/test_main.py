from fastapi.testclient import TestClient

from main import app, tasks

client = TestClient(app)


def setup_function():
    tasks.clear()


def test_create_task_success():
    response = client.post(
        "/tasks",
        json={"title": "File report", "due_date": "2026-06-01"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["title"] == "File report"
    assert body["due_date"] == "2026-06-01"


def test_create_task_validation_failure():
    response = client.post(
        "/tasks",
        json={"title": "File report", "due_date": "not-a-date"},
    )

    assert response.status_code == 422
