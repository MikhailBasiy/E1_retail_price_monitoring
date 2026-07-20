import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from parsers.base_parser import BaseParser
from parsers.config import geo_settings
from parsers.parsers_config.hoff import GEO_SETTINGS, SET_LOCATION_JS
from utils.logger import get_logger

logger = get_logger(__name__)


class HoffParser(BaseParser):
    def __init__(self, location: str):
        self.location = location
        self.start_url = "https://www.hoff.ru/"
        self.timeout = 15
        self.by = By.XPATH
        self.skipping_tag_locators = [
            '//div[@class="no-product-text" and text()=" Этот товар закончился :( "]',
            '//span[@class="hoff-button__content" and text()="Нет в наличии"]',
        ]
        self.name_locator = '//h1[@class="product-header"]/span'
        self.price_locator = '//span[@class="price-actual"]'
        self.city_locator = (
            '//div[contains(@class, "c-city-picker city-picker-header")]'
        )
        # self.city_script = (
        #     "document.cookie.match(/(?:^|;\s*)current_city_name=([^;]+)/)?.[1]"
        # )
        self.min_delay = 4.0
        self.max_delay = 7.0

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

    def set_location(self):
        # self.browser.execute_cdp_cmd(
        #     "Browser.grantPermissions",
        #     {
        #         "origin": f"{self.start_url}",
        #         "permissions": ["geolocation"],
        #     },
        # )
        # self.browser.execute_cdp_cmd(
        #     "Emulation.setGeolocationOverride", geo_settings[self.location]
        # )
        self._open_page(self.start_url)
        # super()._random_wait()
        self.browser.execute_script(SET_LOCATION_JS, GEO_SETTINGS[self.location])
        self._random_wait()
        self._open_page(self.start_url)
        # super()._random_wait()

    def _check_page_loaded(self):
        wait = WebDriverWait(self.browser, self.timeout)
        try:
            wait.until(EC.visibility_of_element_located((self.by, self.name_locator)))
            wait.until(EC.visibility_of_element_located((self.by, self.price_locator)))
        except TimeoutException:
            return False
        else:
            return True
