import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from parsers.base_parser import BaseParser
from parsers.config import geo_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class WildberriesParser(BaseParser):
    def __init__(self):
        self.start_url = "https://www.wildberries.ru/"
        self.browser = uc.Chrome()
        self.timeout = 10
        self.by = By.XPATH
        self.skipping_tag_locators = [
            '//h1[@class="content404__title"]',
            '//span[contains(@class, "soldOutProductText")]'
        ]
        self.name_locator = '//h3[contains(@class, "productTitle")]'
        self.price_locator = '//*[contains(@class, "priceBlockFinalPrice")]'
        self.city_locator = '//span[contains(@class, "simple-menu__link--address")]'
        self.min_delay = 4.0
        self.max_delay = 7.0

        super().__init__(
            browser=self.browser,
            timeout=self.timeout,
            by=self.by,
            skipping_tag_locators=self.skipping_tag_locators,
            name_locator=self.name_locator,
            price_locator=self.price_locator,
            min_delay=self.min_delay,
            max_delay=self.max_delay,
        )

    def set_location(self, location: str):
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
        self.browser.get(self.start_url)
        super()._random_wait()
