import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from parsers.base_parser import BaseParser
from parsers.parsers_config.nonton import SUBDOMAINS
from utils.logger import get_logger

logger = get_logger(__name__)


class NontonParser(BaseParser):
    def __init__(self, location: str):
        self.location = location
        self.start_url = "https://www.nonton.ru/"
        self.timeout = 10
        self.by = By.XPATH
        self.skipping_tag_locators = ['//div[@class="e-404"]']
        self.name_locator = '//div[@data-title=""] | //h1[@data-title=""]'
        self.price_locator = (
            '//div[contains(@class, "price ") and @style="display: ;"]/span'
        )
        self.city_locator = '//a[@class="h__city h__city-select"]/span'
        self.min_delay = 3.0
        self.max_delay = 5.0

        super().__init__(
            location=self.location,
            timeout=self.timeout,
            by=self.by,
            skipping_tag_locators=self.skipping_tag_locators,
            name_locator=self.name_locator,
            price_locator=self.price_locator,
            city_locator=self.city_locator,
            min_delay=self.min_delay,
            max_delay=self.max_delay,
        )

    def set_location(self) -> None:
        self.subdomain = SUBDOMAINS[self.location]
