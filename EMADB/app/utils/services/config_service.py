from __future__ import annotations

import os
import threading
from typing import Any

from EMADB.app.configuration import Configuration
from EMADB.app.constants import CONFIG_PATH
from EMADB.app.logger import logger


###############################################################################
class ConfigurationService:
    def __init__(self, configuration: Configuration | None = None) -> None:
        self.configuration = configuration or Configuration()
        self.lock = threading.Lock()

    # -------------------------------------------------------------------------
    def get_configuration(self) -> dict[str, Any]:
        with self.lock:
            return self.configuration.get_configuration()

    # -------------------------------------------------------------------------
    def update_value(self, key: str, value: Any) -> dict[str, Any]:
        with self.lock:
            self.configuration.update_value(key, value)
            cfg = self.configuration.get_configuration()
        logger.debug(f"Updated configuration key '{key}' to '{value}'")
        return cfg

    # -------------------------------------------------------------------------
    def save(self, name: str) -> str:
        cleaned = name.strip() or "default_config"
        with self.lock:
            self.configuration.save_configuration_to_json(cleaned)
        logger.info(f"Configuration [{cleaned}] has been saved")
        return cleaned

    # -------------------------------------------------------------------------
    def load(self, name: str) -> dict[str, Any]:
        with self.lock:
            self.configuration.load_configuration_from_json(name)
            cfg = self.configuration.get_configuration()
        logger.info(f"Loaded configuration [{name}]")
        return cfg

    # -------------------------------------------------------------------------
    def available_configurations(self) -> list[str]:
        if not os.path.isdir(CONFIG_PATH):
            return []
        return sorted([f for f in os.listdir(CONFIG_PATH) if f.endswith(".json")])
