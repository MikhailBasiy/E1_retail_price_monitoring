import re
from dataclasses import asdict
from random import uniform
from time import sleep

import pandas as pd
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

from models.item import Item
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseParser:
    def __init__(
        self,
        browser,
        timeout,
        by,
        skipping_tag_locators,
        name_locator,
        price_locator,
        min_delay,
        max_delay,
    ):
        self.browser = browser
        self.timeout = timeout
        self.by = by
        self.skipping_tag_locators = skipping_tag_locators
        self.name_locator = name_locator
        self.price_locator = price_locator
        self.min_delay = min_delay
        self.max_delay = max_delay

        self.max_retries = 3
        self.collected_data: list[Item] = []
        logger.info(f"{type(self).__name__} initialized")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.browser.quit()

    def collect_data(self, urls: list[str]):
        for url in urls:
            if not self._open_page(url):
                logger.error(f"Page {url} was NOT downloaded")
                continue
            elif self._check_product_available():
                name, price = self._parse_data()
                self.collected_data.append(Item(url, name, price))
            else:
                self.collected_data.append(Item(url, "Нет в продаже", 0))
                logger.info(f"Item is {'Нет в продаже'}\nPrice is {0}")

    def _open_page(self, url, attempt=1):
        self.browser.get(url)
        if self._check_page_loaded():
            self._random_wait()
            return True
        elif attempt < self.max_retries:
            return self._open_page(url, attempt + 1)

    def _check_page_loaded(self):
        wait = WebDriverWait(self.browser, self.timeout)
        try:
            WebDriverWait(self.browser, self.timeout).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
        except TimeoutException:
            return False
        else:
            return True

    def _random_wait(self):
        delay = uniform(self.min_delay, self.max_delay)
        logger.info(f"Waiting for {delay} sec")
        sleep(delay)

    def _check_product_available(self):
        if any(
            self.browser.find_elements(self.by, skipping_tag)
            for skipping_tag in self.skipping_tag_locators
        ):
            logger.info(f"Encountered skip text on page:\n{self.browser.current_url}")
            return False
        elif WebDriverWait(self.browser, self.timeout).until(
            EC.presence_of_element_located((self.by, self.price_locator))
        ):
            logger.info(f"Price found: {self.browser.current_url}")
            return True
        else:
            logger.error(
                f"Parsing failed! Check page parsing settings: {self.browser.current_url}"
            )

    def _parse_data(self):
        name = self.browser.find_element(self.by, self.name_locator).text
        price = self._normalize_price(
            self.browser.find_element(self.by, self.price_locator).text
        )
        logger.info(f"Item is {name}\nPrice is {price}")
        return name, price

    def _normalize_price(self, price: str):
        return int(re.sub(r"\s|₽|руб.", "", price))

    def export_to_df(self):
        return pd.DataFrame([asdict(item) for item in self.collected_data])
