import os
import time
from typing import Any

from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from EMADB.app.client.workers import check_thread_status
from EMADB.app.constants import DOWNLOAD_PATH
from EMADB.app.logger import logger


# [SCRAPER]
###############################################################################
class EMAWebPilot:
    def __init__(self, driver: Chrome, wait_time: int = 10) -> None:
        self.driver = driver
        self.wait_time = wait_time
        self.data_URL = "https://www.adrreports.eu/en/search_subst.html"
        self.alphabet = []

    # -------------------------------------------------------------------------
    def autoclick(self, string: str, mode: str = "XPATH") -> None:
        wait = WebDriverWait(self.driver, self.wait_time)
        by_elem = By.CSS_SELECTOR if mode == "CSS" else By.XPATH
        page = wait.until(EC.visibility_of_element_located((by_elem, string)))
        page.click()

    # -------------------------------------------------------------------------
    def drug_finder(self, name: str) -> None:
        wait = WebDriverWait(self.driver, self.wait_time)
        item = wait.until(
            EC.visibility_of_element_located((By.PARTIAL_LINK_TEXT, name.upper()))
        )
        item.click()
        _ = self.driver.current_window_handle
        WebDriverWait(self.driver, self.wait_time).until(EC.number_of_windows_to_be(2))
        self.driver.switch_to.window(self.driver.window_handles[1])

    # -------------------------------------------------------------------------
    def close_and_switch_window(self):
        self.driver.switch_to.window(self.driver.window_handles[1])
        self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    # -------------------------------------------------------------------------
    def click_and_download(self, current_page: bool = True) -> None:
        flag = 1 if current_page else 2
        wait = WebDriverWait(self.driver, self.wait_time)
        xpath = '//*[@id="uberBar_dashboardpageoptions_image"]'
        item = wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
        item.click()
        xpath = '//*[@id="idPageExportToExcel"]/table/tbody/tr/td[2]'
        item = wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
        item.click()
        xpath = f'//*[@id="idDashboardExportToExcelMenu"]/table/tbody/tr[1]/td[1]/a[{flag}]/table/tbody/tr/td[2]'
        item = wait.until(EC.visibility_of_element_located((By.XPATH, xpath)))
        item.click()

    # -------------------------------------------------------------------------
    def check_DAP_filenames(self) -> None:
        while True:
            current_files = os.listdir(DOWNLOAD_PATH)
            DAP_files = [x for x in current_files if "DAP" in x]
            if len(DAP_files) > 0:
                break
            else:
                time.sleep(0.5)
                continue

    # -------------------------------------------------------------------------
    def download_manager(
        self, grouped_drugs: dict[str, list[str]], **kwargs: Any
    ) -> None:
        for letter, drugs in grouped_drugs.items():
            self.driver.get(self.data_URL)
            letter_css = f"a[onclick=\"showSubstanceTable('{letter.lower()}')\"]"
            self.autoclick(letter_css, mode="CSS")
            for d in drugs:
                # check for thread status and eventually stop it
                check_thread_status(kwargs.get("worker", None))
                logger.info(f"Collecting data for drug: {d}")
                try:
                    self.drug_finder(d)
                    self.click_and_download(current_page=False)
                    self.check_DAP_filenames()
                    self.close_and_switch_window()
                    DAP_path = os.path.join(DOWNLOAD_PATH, "DAP.xlsx")
                    rename_path = os.path.join(DOWNLOAD_PATH, f"{d}.xlsx")
                    os.rename(DAP_path, rename_path)
                    logger.debug(f"Succesfully downloaded file {rename_path}")
                except Exception:
                    logger.error(
                        f"An error has been encountered while fetching {d} data. Skipping this drug."
                    )
