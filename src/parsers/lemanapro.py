from urllib.parse import urlparse, urlunparse

import undetected_chromedriver as uc
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By

from parsers.base_parser import BaseParser
from parsers.config import geo_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class LemanaproParser(BaseParser):
    def __init__(self):
        self.start_url = "https://lemanapro.ru/"
        ### Browser options
        self.browser_options = Options()
        self.browser_options.page_load_strategy = "none"
        self.browser = uc.Chrome(options=self.browser_options)
        self.timeout = 10
        self.by = By.XPATH
        self.skipping_tag_locators = [
            '//span[contains(@class, "static-pages") and text()="Что-то пошло не так"]',
            '//h1[text()="404"]',
        ]
        self.name_locator = '//h1[@data-qa="product-name"]/span'
        self.price_locator = '//div[@data-qa="prices_mf-pdp"]//div[@data-testid="price-block-price"]//span[@data-testid="price-integer"]'
        self.city_script = 'return document.querySelector("button[data-qa=\'region-modal-button\'] span.h4lh9ow_header-footer")?.textContent || "";'
        self.min_delay = 5.0
        self.max_delay = 8.0
        self.geo_prefixes = {
            "Москва": None,  # The site doesn't use geo prefix for Moscow
            "Новосибирск": "novosibirsk",
        }

        super().__init__(
            browser=self.browser,
            timeout=self.timeout,
            by=self.by,
            skipping_tag_locators=self.skipping_tag_locators,
            name_locator=self.name_locator,
            price_locator=self.price_locator,
            city_script=self.city_script,
            min_delay=self.min_delay,
            max_delay=self.max_delay,
        )

    def set_location(self, location: str):
        ### Install not necessary browser geolocation
        self.browser.execute_cdp_cmd(
            "Browser.grantPermissions",
            {
                "origin": f"{self.start_url}",
                "permissions": ["geolocation"],
            },
        )
        self.browser.execute_cdp_cmd(
            "Emulation.setGeolocationOverride", geo_settings[location]
        )

        if self.geo_prefixes[location]:
            parsed_url = urlparse(self.start_url)
            new_netloc = ".".join((self.geo_prefixes[location], parsed_url.netloc))
            self.start_url = urlunparse(parsed_url._replace(netloc=new_netloc))

        self.browser.get(self.start_url)
        super()._random_wait()
        logger.info(f"Location '{location}' is set.")
