import re
from dataclasses import asdict
from random import uniform
from time import sleep

import pandas as pd
import undetected_chromedriver as uc
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from urllib3.exceptions import ReadTimeoutError

from models.item import Item
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseParser:
    def __init__(
        self,
        timeout,
        by,
        skipping_tag_locators,
        name_locator,
        price_locator,
        min_delay,
        max_delay,
        city_locator=None,
        city_script=None,
    ):
        self.browser = uc.Chrome(version_main=148)
        self.timeout = timeout
        self.by = by
        self.skipping_tag_locators = skipping_tag_locators
        self.name_locator = name_locator
        self.price_locator = price_locator
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.city_locator = city_locator
        self.city_script = city_script

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
                name, price, city = self._parse_data()
                self.collected_data.append(Item(url, name, price))
            else:
                self.collected_data.append(Item(url, "Нет в продаже", 0))
                logger.info(f"Item is {'Нет в продаже'}\nPrice is {0}")

    def _open_page(self, url, attempt=1):
        try:
            self.browser.get(url)
            self._random_wait()
            return True
        except (TimeoutException, TimeoutError, ReadTimeoutError) as e:
            logger.info(f"Encounter {e} while getting {url}. Attempt - {attempt}")
            if attempt >= self.max_retries:
                return False
            else:
                return self._open_page(url, attempt + 1)
        # if self._check_page_loaded():
        #     self._random_wait()
        #     return True
        # elif attempt < self.max_retries:
        #     return self._open_page(url, attempt + 1)

    # def _check_page_loaded(self):
    #     wait = WebDriverWait(self.browser, self.timeout)
    #     try:
    #         WebDriverWait(self.browser, self.timeout).until(
    #             lambda d: d.execute_script("return document.readyState") == "complete"
    #         )
    #     except TimeoutError:
    #         return False
    #     else:
    #         return True

    def _random_wait(self):
        delay = uniform(self.min_delay, self.max_delay)
        logger.info(f"Waiting for {round(delay, 2)} sec")
        sleep(delay)

    def _check_product_available(self):
        if any(
            self.browser.find_elements(self.by, skipping_tag)
            for skipping_tag in self.skipping_tag_locators
        ):
            logger.info(f"Encountered skip text on page:\n{self.browser.current_url}")
            return False
        try:
            if WebDriverWait(self.browser, self.timeout).until(
                EC.presence_of_element_located((self.by, self.price_locator))
            ):
                logger.info(f"Price found: {self.browser.current_url}")
                return True
        except TimeoutException:
            logger.error(
                f"Parsing failed! Check page parsing settings: {self.browser.current_url}"
            )
            return False

    def _parse_data(self):
        try:
            name = self.browser.find_element(self.by, self.name_locator).text
            price = self._normalize_price(
                self.browser.find_element(self.by, self.price_locator).text
            )
            city = self._parse_city()
            # if self.city_locator:
            #     city = self.browser.find_element(self.by, self.city_locator).text
            #     city_name = self.browser.execute_script(self.city_script)
            #     logger.info(city_name)
            # else:
            #     city = None
            logger.info(f"Item is {name}\nPrice is {price}\nCity is {city}")
            return name, price, city
        except NoSuchElementException as e:
            logger.error(f"Can't find data on the page {self.browser.current_url}: {e}")
            return "", "", ""

    def _parse_city(self):
        if self.city_locator:
            return self.browser.find_element(self.by, self.city_locator).text
        elif self.city_script:
            return self.browser.execute_script(self.city_script)
        else:
            return None

    def _normalize_price(self, price: str):
        try:
            return int(re.sub(r"\s|₽|руб.|р|¤|шт.|/", "", price))  ### |\xa4|
        except Exception as e:
            logger.error(f"Encountered exception {e} while parsing price")
            return 0

    def export_to_df(self):
        return pd.DataFrame([asdict(item) for item in self.collected_data])
