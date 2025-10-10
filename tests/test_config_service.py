from __future__ import annotations

import os

import pytest

from EMADB.app.configuration import Configuration
from EMADB.app.utils.services.config_service import ConfigurationService


@pytest.fixture()
def temp_config_dir(tmp_path, monkeypatch):
    config_dir = tmp_path / "configs"
    config_dir.mkdir()
    monkeypatch.setattr("EMADB.app.utils.services.config_service.CONFIG_PATH", str(config_dir))
    monkeypatch.setattr("EMADB.app.configuration.CONFIG_PATH", str(config_dir))
    return config_dir


def test_update_and_get_configuration(temp_config_dir):
    service = ConfigurationService(Configuration())
    updated = service.update_value("headless", True)
    assert updated["headless"] is True
    assert service.get_configuration()["headless"] is True


def test_save_and_load_configuration(temp_config_dir):
    service = ConfigurationService(Configuration())
    service.update_value("headless", True)
    saved_name = service.save("test_config")
    assert saved_name == "test_config"
    assert os.path.exists(temp_config_dir / "test_config.json")

    loaded = service.load("test_config.json")
    assert loaded["headless"] is True
    files = service.available_configurations()
    assert files == ["test_config.json"]
