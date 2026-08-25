from urllib.parse import urlparse, urlunparse

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from parsers.base_parser import BaseParser
from parsers.parsers_config.pushe import SUBDOMAINS
from utils.logger import get_logger

logger = get_logger(__name__)


class PusheParser(BaseParser):
    def __init__(self, location: str):
        self.location = location
        self.start_url = "https://pushe.ru/"
        ### Browser options
        self.browser_options = Options()
        self.browser_options.page_load_strategy = "none"
        self.timeout = 10
        self.by = By.XPATH
        self.skipping_tag_locators = [
            '//h1[text()="Такая страница не найдена"]',
        ]
        self.name_locator = '//div[@class="product-card__title"]/h1'
        self.price_locator = (
            '//div[@class="product-card__price"]/span[@class="price-current"]'
        )
        self.city_locator = '//div[@class="header-city__selected"]/span'
        self.city_script = (
            'return document.querySelector(".header-city__selected span").textContent;'
        )
        self.min_delay = 5.0
        self.max_delay = 8.0

        super().__init__(
            location=self.location,
            timeout=self.timeout,
            by=self.by,
            skipping_tag_locators=self.skipping_tag_locators,
            name_locator=self.name_locator,
            price_locator=self.price_locator,
            city_script=self.city_script,
            min_delay=self.min_delay,
            max_delay=self.max_delay,
            # via_proxy=True,
        )

    def set_location(self) -> None:
        self.subdomain = SUBDOMAINS[self.location]
