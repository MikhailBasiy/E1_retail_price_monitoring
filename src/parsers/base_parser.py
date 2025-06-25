import re
from dataclasses import asdict
from random import uniform
from time import sleep

import pandas as pd
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from models.item import Item
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseParser:
    def __init__(
        self, browser, timeout, by, name_locator, price_locator, min_delay, max_delay
    ):
        self.browser = browser
        self.timeout = timeout
        self.by = by
        self.name_locator = name_locator
        self.price_locator = price_locator
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.parsed_data: list[Item] = []
        logger.info(f"{type(self).__name__} initialized")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.browser.quit()

    def get_item_data(self, url):
        self.open_page(url)
        self.parse_data(url)

    def _random_wait(self):
        delay = uniform(self.min_delay, self.max_delay)
        logger.info(f"Waiting for {delay} sec")
        sleep(delay)

    def open_page(self, url):
        self.browser.get(url)
        WebDriverWait(self.browser, self.timeout).until(
            EC.presence_of_element_located((self.by, self.price_locator))
        )
        logger.info(f"Page {url} successfully downloaded")
        self._random_wait()

    def _normalize_price(self, price: str):
        return int(re.sub(r"[\s₽]", "", price))

    def parse_data(self, url):
        name = self.browser.find_element(self.by, self.name_locator).text
        price = self._normalize_price(
            self.browser.find_element(self.by, self.price_locator).text
        )
        logger.info(f"Item is {name}\nPrice is {price}")
        self.parsed_data.append(Item(url, name, price))

    def export_to_df(self):
        return pd.DataFrame([asdict(item) for item in self.parsed_data])
