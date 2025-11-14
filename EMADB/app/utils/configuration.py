import json
import os
from typing import Any

from EMADB.app.utils.constants import CONFIG_PATH


###############################################################################
class Configuration:
    def __init__(self) -> None:
        self.configuration: dict[str, Any] = {
            "headless": False,
            "ignore_SSL": False,
            "wait_time": 5.0,
        }

    # -------------------------------------------------------------------------
    def get_configuration(self) -> dict[str, Any]:
        return self.configuration

    # -------------------------------------------------------------------------
    def update_value(self, key: str, value: bool) -> None:
        self.configuration[key] = value

    # -------------------------------------------------------------------------
    def save_configuration_to_json(self, name: str) -> None:
        full_path = os.path.join(CONFIG_PATH, f"{name}.json")
        with open(full_path, "w") as f:
            json.dump(self.configuration, f, indent=4)

    # -------------------------------------------------------------------------
    def load_configuration_from_json(self, name: str) -> None:
        full_path = os.path.join(CONFIG_PATH, name)
        with open(full_path) as f:
            self.configuration = json.load(f)
