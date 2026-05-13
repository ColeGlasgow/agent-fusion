from fastapi.testclient import TestClient

from main import app, store

client = TestClient(app)


def setup_function() -> None:
    store.clear()


def test_create_task_success() -> None:
    response = client.post(
        "/tasks",
        headers={"X-Request-ID": "req-1", "Idempotency-Key": "create-report"},
        json={"title": "File report", "due_date": "2026-06-01"},
    )

    assert response.status_code == 201
    body = response.json()
    assert body["id"]
    assert body["title"] == "File report"
    assert body["due_date"] == "2026-06-01"


def test_create_task_validation_failure() -> None:
    response = client.post(
        "/tasks",
        json={"title": "", "due_date": "not-a-date"},
    )

    assert response.status_code == 422


def test_create_task_conflict() -> None:
    payload = {"title": "File report", "due_date": "2026-06-01"}
    first = client.post("/tasks", json=payload)
    second = client.post("/tasks", json=payload)

    assert first.status_code == 201
    assert second.status_code == 409
    assert second.json()["detail"] == "task already exists"


def test_create_task_idempotency_key_reuses_existing_task() -> None:
    payload = {"title": "File report", "due_date": "2026-06-01"}
    headers = {"Idempotency-Key": "create-report"}
    first = client.post("/tasks", headers=headers, json=payload)
    second = client.post("/tasks", headers=headers, json=payload)

    assert first.status_code == 201
    assert second.status_code == 200
    assert second.json()["id"] == first.json()["id"]
