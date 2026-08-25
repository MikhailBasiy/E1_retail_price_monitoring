import re
import threading
from dataclasses import asdict
from io import BytesIO
from pathlib import Path
from random import uniform
from time import sleep
from urllib.parse import urlparse, urlunparse

import pandas as pd
import pendulum
import tldextract
import undetected_chromedriver as uc
from PIL import Image
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from slugify import slugify
from urllib3.exceptions import ReadTimeoutError

from models.item import Item
from settings import data_dir as DEFAULT_DIRECTORY
from settings import screenshots_format as DEFAULT_FORMAT
from settings import screenshots_quality as DEFAULT_QUALITY
from utils.logger import get_logger

logger = get_logger(__name__)


class BaseParser:
    _driver_lock = threading.Lock()

    def __init__(
        self,
        location,
        timeout,
        by,
        skipping_tag_locators,
        name_locator,
        price_locator,
        min_delay,
        max_delay,
        city_locator=None,
        city_script=None,
        # via_proxy=False,
    ):
        options = uc.ChromeOptions()
        options.add_argument("--force-device-scale-factor=0.75")
        # if via_proxy:
        #     options.add_argument(f"--proxy-server={PROXY}")
        with self._driver_lock:
            self.browser = uc.Chrome(version_main=150, options=options)
            self.browser.maximize_window()
        self.location = location
        self.subdomain = None
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

    def collect_data(self, urls: list[str]) -> None:
        for url in urls:
            if not self._open_page(url):
                logger.error(f"Page {url} was NOT downloaded")
                continue
            name = self._parse_name()
            price = self._parse_price()
            city = self._parse_city()
            product_available = self._product_available()
            logger.info(
                f"Item is {name}, Price is {price}, City is {city}, Available {product_available}"
            )
            self.collected_data.append(Item(url, name, price, city, product_available))

    def _open_page(self, url, attempt=1):
        try:
            prepared_url = self._prepare_url(url)
            self.browser.get(prepared_url)
            self._random_wait()
            self._save_screenshot(requested_url=url)
            return True
        except (TimeoutException, TimeoutError, ReadTimeoutError) as e:
            logger.info(f"Encounter {e} while getting {url}. Attempt - {attempt}")
            if attempt >= self.max_retries:
                return False
            else:
                return self._open_page(url, attempt + 1)

    def _prepare_url(self, url: str) -> str:
        if not self.subdomain:
            return url
        parsed = urlparse(url)
        ext = tldextract.extract(parsed.netloc)
        host = f"{self.subdomain}.{ext.domain}.{ext.suffix}"
        return urlunparse(parsed._replace(netloc=host))

    def _random_wait(self):
        delay = round(uniform(self.min_delay, self.max_delay), 2)
        logger.info(f"Waiting for {delay} sec")
        sleep(delay)

    def _product_available(self):
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
                return True
        except TimeoutException:
            logger.error(
                f"Parsing failed! Check page parsing settings: {self.browser.current_url}"
            )
            return False

    def _parse_name(self) -> str:
        try:
            return self.browser.find_element(self.by, self.name_locator).text
        except NoSuchElementException as e:
            logger.error(
                f"Can't find product name on the page {self.browser.current_url}: {e}"
            )
            return ""

    def _parse_price(self) -> str:
        try:
            return self._normalize_price(
                self.browser.find_element(self.by, self.price_locator).text
            )
        except NoSuchElementException as e:
            logger.error(
                f"Can't find price on the page {self.browser.current_url}: {e}"
            )
            return ""

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

    def _save_screenshot(self, requested_url: str):
        try:
            # Prepare foldername
            folder_name = pendulum.today().to_date_string()
            folder_path = Path(DEFAULT_DIRECTORY) / folder_name
            folder_path.mkdir(parents=True, exist_ok=True)
            # Prepare filename
            requested_url = (
                requested_url.replace("https://", "")
                .replace("http://", "")
                .replace("www", "")
            )
            url_parts = requested_url.split("/")
            screenshot_name = "_".join([url_parts[0], *url_parts[-2:], self.location])
            screenshot_name_slugified = slugify(screenshot_name)

            screenshot_path = (folder_path / screenshot_name_slugified).with_suffix(
                f".{DEFAULT_FORMAT}"
            )
            img = Image.open(BytesIO(self.browser.get_screenshot_as_png()))
            img.save(screenshot_path, quality=DEFAULT_QUALITY)

            logger.info(f"Screenshot saved: {screenshot_path}")
        except Exception as e:
            logger.exception(f"Screenshot NOT saved!")

    def export_to_df(self):
        return pd.DataFrame([asdict(item) for item in self.collected_data])
