from urllib.parse import urlparse, urlunparse

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from parsers.base_parser import BaseParser
from parsers.parsers_config.lemanapro import SUBDOMAINS
from utils.logger import get_logger

logger = get_logger(__name__)


class LemanaproParser(BaseParser):
    def __init__(self, location: str):
        self.location = location
        self.start_url = "https://lemanapro.ru/"
        ### Browser options
        self.browser_options = Options()
        self.browser_options.page_load_strategy = "none"
        self.timeout = 10
        self.by = By.XPATH
        self.skipping_tag_locators = [
            '//span[contains(@class, "static-pages") and text()="Что-то пошло не так"]',
            '//h1[text()="404"]',
            '//div[@data-qa="out-of-stock-label"]/span[text()="Товар закончился"]',
        ]
        self.name_locator = '//h1[@data-qa="product-name"]'
        self.price_locator = '//div[@data-qa="prices_mf-pdp"]//div[@data-testid="price-block-price"]//span[@data-testid="price-integer"]'
        self.city_script = """
        const spans = document.querySelectorAll(
            'button[data-qa="region-modal-button"] span'
        );
        return spans.length > 1 ? spans[1].textContent.trim() : "";
        """
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
            via_proxy=True,
        )

    def set_location(self) -> None:
        self.subdomain = SUBDOMAINS[self.location]
