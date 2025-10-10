from __future__ import annotations

import time

import pytest

from EMADB.app.configuration import Configuration
from EMADB.app.utils.services.config_service import ConfigurationService
from EMADB.app.utils.services.search_service import SearchService
from EMADB.app.utils.services.tasks import TaskStatus


class DummyDriver:
    def __init__(self) -> None:
        self.closed = False

    def quit(self) -> None:
        self.closed = True


class DummyToolkit:
    def __init__(self, headless: bool, ignore_ssl: bool) -> None:
        self.headless = headless
        self.ignore_ssl = ignore_ssl
        self.driver = DummyDriver()

    def initialize_webdriver(self) -> DummyDriver:
        return self.driver

    def is_chromedriver_installed(self) -> str:
        return "Chrome driver is installed"

    def check_chrome_version(self) -> str:
        return "120.0"


class DummyPilot:
    calls: list[dict[str, list[str]]] = []

    def __init__(self, driver: DummyDriver, wait_time: int) -> None:
        self.driver = driver
        self.wait_time = wait_time

    def download_manager(self, grouped_drugs, **kwargs) -> None:
        DummyPilot.calls.append(grouped_drugs)


class SlowPilot(DummyPilot):
    def download_manager(self, grouped_drugs, **kwargs) -> None:
        DummyPilot.calls.append(grouped_drugs)
        worker = kwargs.get("worker")
        for _ in range(10):
            if worker and worker.is_interrupted():
                return
            time.sleep(0.01)


@pytest.fixture(autouse=True)
def clear_calls():
    DummyPilot.calls.clear()
    yield
    DummyPilot.calls.clear()


@pytest.fixture()
def config_service():
    configuration = Configuration()
    return ConfigurationService(configuration)


@pytest.fixture()
def search_service(config_service, monkeypatch):
    monkeypatch.setattr("EMADB.app.utils.services.search_service.file_remover", lambda: None)
    service = SearchService(
        configuration_service=config_service,
        toolkit_factory=DummyToolkit,
        pilot_factory=DummyPilot,
        max_workers=1,
    )
    yield service
    service.shutdown()


def test_search_from_text_completes(search_service):
    task = search_service.start_search_from_text("drug_a, drug_b")
    task.future.result(timeout=1)
    assert task.status is TaskStatus.COMPLETED
    assert DummyPilot.calls
    grouped = DummyPilot.calls[0]
    assert set(grouped.keys()) == {"d"}
    assert task.result is None


def test_stop_task_cancels(search_service, monkeypatch):
    monkeypatch.setattr(search_service, "pilot_factory", SlowPilot)
    task = search_service.start_search_from_text("drug_c")
    time.sleep(0.05)
    assert search_service.stop_task(task.task_id) is True
    task.future.result(timeout=2)
    assert task.status is TaskStatus.CANCELLED


def test_check_driver(search_service):
    result = search_service.check_driver()
    assert result["status"] == "ok"
    assert "current version" in result["message"]
