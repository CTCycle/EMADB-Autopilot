from __future__ import annotations

import os
from typing import Any

from EMADB.app.client.workers import Worker, check_thread_status
from EMADB.app.utils.components import drug_to_letter_aggregator, file_remover
from EMADB.app.utils.constants import RSC_PATH
from EMADB.app.utils.logger import logger
from EMADB.app.utils.services.autopilot import EMAWebPilot
from EMADB.app.utils.services.toolkit import WebDriverToolkit


###############################################################################
class SearchEvents:
    def __init__(self, configuration: dict[str, Any]) -> None:
        self.configuration = configuration
        self.headless = configuration.get("headless", False)
        self.ignore_SSL = configuration.get("ignore_SSL", False)
        self.wait_time = configuration.get("wait_time", 0)

    # -------------------------------------------------------------------------
    def get_drugs_from_file(self) -> list[str]:
        filepath = os.path.join(RSC_PATH, "drugs_to_search.txt")
        with open(filepath) as file:
            drug_list = [x.lower().strip() for x in file.readlines()]

        return drug_list

    # -------------------------------------------------------------------------
    def search_using_webdriver(
        self, drug_list: list[str] | None = None, worker: Worker | None = None
    ) -> None:
        """
        Execute the end-to-end scraping pipeline for the provided drug list.

        Keyword arguments:
            drug_list: Optional custom list of drug identifiers to query.
            worker: Running worker instance used for interruption signaling.
        Return value:
            None
        """
        # check if files downloaded in the past are still present, then remove them
        # create a dictionary of drug names with their initial letter as key
        file_remover()
        if drug_list is None:
            logger.info("No drug targets provided, reading from source file directly")
            drug_list = self.get_drugs_from_file()

        # initialize webdriver and webscraper
        self.toolkit = WebDriverToolkit(self.headless, self.ignore_SSL)
        webdriver = self.toolkit.initialize_webdriver()

        # check for thread status and eventually stop it
        check_thread_status(worker)
        # click on letter page (based on first letter of names group) and then iterate over
        # all drugs in that page (from the list). Download excel reports and rename them automatically
        grouped_drugs = drug_to_letter_aggregator(drug_list)

        webscraper = EMAWebPilot(webdriver, self.wait_time)
        webscraper.download_manager(grouped_drugs, worker=worker)
