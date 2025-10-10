from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from EMADB.app.constants import RSC_PATH
from EMADB.app.logger import logger
from EMADB.app.utils.components import drug_to_letter_aggregator, file_remover
from EMADB.app.utils.driver.autopilot import EMAWebPilot
from EMADB.app.utils.driver.toolkit import WebDriverToolkit
from EMADB.app.utils.services.config_service import ConfigurationService
from EMADB.app.utils.services.tasks import (
    SearchTask,
    TaskInterrupted,
    TaskRegistry,
    TaskStatus,
    check_thread_status,
)


###############################################################################
class SearchService:
    def __init__(
        self,
        configuration_service: ConfigurationService,
        max_workers: int = 2,
        toolkit_factory: type[WebDriverToolkit] | None = None,
        pilot_factory: type[EMAWebPilot] | None = None,
    ) -> None:
        self.configuration_service = configuration_service
        self.executor = ThreadPoolExecutor(max_workers=max_workers, thread_name_prefix="search")
        self.registry = TaskRegistry()
        self.toolkit_factory = toolkit_factory or WebDriverToolkit
        self.pilot_factory = pilot_factory or EMAWebPilot

    # -------------------------------------------------------------------------
    def _get_drugs_from_file(self) -> list[str]:
        filepath = os.path.join(RSC_PATH, "drugs_to_search.txt")
        if not os.path.exists(filepath):
            logger.error(f"Drugs source file missing: {filepath}")
            return []
        with open(filepath) as file:
            return [x.lower().strip() for x in file.readlines() if x.strip()]

    # -------------------------------------------------------------------------
    def _parse_drug_list(self, raw: str) -> list[str]:
        tokens = [token.strip().lower() for token in raw.replace("\n", ",").split(",")]
        return [token for token in tokens if token]

    # -------------------------------------------------------------------------
    def _execute_search(self, drug_list: list[str] | None, task: SearchTask) -> None:
        cfg = self.configuration_service.get_configuration()
        headless = bool(cfg.get("headless", False))
        ignore_ssl = bool(cfg.get("ignore_SSL", False))
        wait_time = float(cfg.get("wait_time", 5.0))

        task.mark_running()
        file_remover()
        targets = drug_list or self._get_drugs_from_file()
        if not targets:
            logger.warning("No drug targets provided, aborting search")
            task.mark_cancelled()
            return

        toolkit = self.toolkit_factory(headless, ignore_ssl)
        webdriver = toolkit.initialize_webdriver()
        try:
            check_thread_status(task)
            grouped = drug_to_letter_aggregator(targets)
            webscraper = self.pilot_factory(webdriver, int(wait_time))
            webscraper.download_manager(grouped, worker=task)
            if task.is_interrupted():
                task.mark_cancelled()
                return
            task.mark_completed()
            logger.info("Search for drugs is finished, please check your downloads")
        except TaskInterrupted:
            task.mark_cancelled()
        except Exception as exc:
            task.mark_failed(exc)
            logger.error("An error occurred during the operation", exc_info=exc)
            raise
        finally:
            try:
                webdriver.quit()
            except Exception as exc:  # pragma: no cover - defensive
                logger.error(f"Failed to close webdriver: {exc}")

    # -------------------------------------------------------------------------
    def _submit_task(self, drug_list: list[str] | None) -> SearchTask:
        task = self.registry.register(SearchTask())
        future = self.executor.submit(self._safe_execute, drug_list, task)
        task.set_future(future)
        return task

    # -------------------------------------------------------------------------
    def _safe_execute(self, drug_list: list[str] | None, task: SearchTask) -> None:
        try:
            self._execute_search(drug_list, task)
        except TaskInterrupted:
            task.mark_cancelled()
        except Exception as exc:  # pragma: no cover - actual errors logged
            if task.status != TaskStatus.FAILED:
                task.mark_failed(exc)

    # -------------------------------------------------------------------------
    def start_search_from_file(self) -> SearchTask:
        logger.info("Starting search from file")
        return self._submit_task(None)

    # -------------------------------------------------------------------------
    def start_search_from_text(self, query: str) -> SearchTask:
        logger.info("Starting search from text box")
        self.configuration_service.update_value("text_drug_inputs", query)
        drug_list = self._parse_drug_list(query)
        return self._submit_task(drug_list)

    # -------------------------------------------------------------------------
    def stop_task(self, task_id: str) -> bool:
        stopped = self.registry.stop(task_id)
        if stopped:
            logger.info(f"Interrupt requested for task [{task_id}]")
        return stopped

    # -------------------------------------------------------------------------
    def task_status(self, task_id: str) -> dict[str, Any]:
        task = self.registry.get(task_id)
        if task is None:
            return {"task_id": task_id, "status": "not_found"}
        snapshot = task.snapshot()
        if task.future and task.future.done() and snapshot["status"] == TaskStatus.RUNNING.value:
            if task.future.cancelled():
                task.mark_cancelled()
                snapshot = task.snapshot()
        return snapshot

    # -------------------------------------------------------------------------
    def check_driver(self) -> dict[str, str]:
        cfg = self.configuration_service.get_configuration()
        toolkit = self.toolkit_factory(bool(cfg.get("headless", False)), bool(cfg.get("ignore_SSL", False)))
        status = toolkit.is_chromedriver_installed()
        if "Error" in status:
            logger.error(status)
            return {"status": "error", "message": status}
        version = toolkit.check_chrome_version()
        message = f"Chrome driver is installed, current version: {version}"
        logger.info(message)
        return {"status": "ok", "message": message}

    # -------------------------------------------------------------------------
    def shutdown(self) -> None:
        self.executor.shutdown(wait=False, cancel_futures=True)
