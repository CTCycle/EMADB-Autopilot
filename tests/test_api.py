from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from EMADB.app.app import create_app
from EMADB.app.configuration import Configuration
from EMADB.app import dependencies
from EMADB.app.dependencies import get_config_service, get_search_service
from EMADB.app.utils.services.config_service import ConfigurationService
from EMADB.app.utils.services.tasks import SearchTask, TaskStatus


class StubSearchService:
    def __init__(self) -> None:
        self.tasks: dict[str, SearchTask] = {}

    def _create_task(self) -> SearchTask:
        task = SearchTask()
        task.mark_running()
        self.tasks[task.task_id] = task
        return task

    def start_search_from_file(self) -> SearchTask:
        task = self._create_task()
        task.mark_completed()
        return task

    def start_search_from_text(self, query: str) -> SearchTask:
        task = self._create_task()
        if query.strip():
            task.mark_completed()
        else:
            task.mark_cancelled()
        return task

    def stop_task(self, task_id: str) -> bool:
        task = self.tasks.get(task_id)
        if not task:
            return False
        task.mark_cancelled()
        return True

    def task_status(self, task_id: str) -> dict[str, object]:
        task = self.tasks.get(task_id)
        if task is None:
            return {"task_id": task_id, "status": "not_found"}
        return task.snapshot()

    def check_driver(self) -> dict[str, str]:
        return {"status": "ok", "message": "Chrome driver is installed, current version: 120.0"}


@pytest.fixture()
def api_client(tmp_path, monkeypatch):
    monkeypatch.setattr("EMADB.app.utils.services.config_service.CONFIG_PATH", str(tmp_path))
    monkeypatch.setattr("EMADB.app.configuration.CONFIG_PATH", str(tmp_path))
    config_service = ConfigurationService(Configuration())
    search_service = StubSearchService()

    dependencies.config_service = config_service
    dependencies.search_service = search_service

    app = create_app()
    app.dependency_overrides[get_config_service] = lambda: config_service
    app.dependency_overrides[get_search_service] = lambda: search_service

    client = TestClient(app)
    yield client
    client.close()


def test_configuration_endpoints(api_client, tmp_path):
    response = api_client.get("/api/configuration/")
    assert response.status_code == 200
    assert response.json()["wait_time"] == 5.0

    update = api_client.put("/api/configuration/", json={"key": "wait_time", "value": 7.5})
    assert update.status_code == 200
    assert update.json()["wait_time"] == 7.5

    save = api_client.post("/api/configuration/save", json={"name": "sample"})
    assert save.status_code == 200
    saved_file = tmp_path / "sample.json"
    assert saved_file.exists()

    load = api_client.post("/api/configuration/load", json={"name": "sample.json"})
    assert load.status_code == 200
    assert load.json()["wait_time"] == 7.5

    listing = api_client.get("/api/configuration/available")
    assert listing.status_code == 200
    assert listing.json()["files"] == ["sample.json"]


def test_search_endpoints(api_client):
    start = api_client.post("/api/search/text", json={"query": "aspirin"})
    assert start.status_code == 200
    data = start.json()
    assert data["status"] in {TaskStatus.RUNNING.value, TaskStatus.COMPLETED.value}
    task_id = data["task_id"]

    status_response = api_client.get(f"/api/search/{task_id}")
    assert status_response.status_code == 200
    assert status_response.json()["task_id"] == task_id

    stop_response = api_client.post("/api/search/stop", json={"task_id": str(uuid.uuid4())})
    assert stop_response.status_code == 404

    check_driver = api_client.get("/api/search/check/driver")
    assert check_driver.status_code == 200
    assert "Chrome driver" in check_driver.json()["message"]
