import uuid

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from parsers.base_parser import BaseParser
from parsers.config import geo_settings
from parsers.parsers_config.ozon import SET_LOCATION_JS
from utils.logger import get_logger

logger = get_logger(__name__)


class OzonParser(BaseParser):
    def __init__(self, location: str):
        self.location = location
        self.start_url = "https://www.ozon.ru/"
        self.timeout = 10
        self.by = By.XPATH
        self.skipping_tag_locators = [
            '//h2[contains(text(), "Этот товар закончился")]',
            '//h2[contains(text(), "Товар не доставляется в ваш регион")]',
            '//h2[contains(text(), "Такой страницы не существует")]',
        ]
        self.name_locator = '//div[@data-widget="webProductHeading"]/h1'
        self.price_locator = (
            '//div[@data-widget="webPrice"]/div/div[2]/div/div/span | '
            '//div[@data-widget="webPrice"]/div/div/div/div/span'
        )
        self.city_script = """
            return window.__NUXT__.state.location.current.city;
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
        )

    def set_location(self):
        geo = geo_settings[self.location]
        lat = geo["latitude"]
        lng = geo["longitude"]

        # self.browser.execute_cdp_cmd(
        #     "Browser.grantPermissions",
        #     {
        #         "origin": self.start_url,
        #         "permissions": ["geolocation"],
        #     },
        # )
        # self.browser.execute_cdp_cmd("Emulation.setGeolocationOverride", geo)
        self._open_page(self.start_url)
        self._random_wait()

        address = self.location
        geo_session_id = str(uuid.uuid4())

        result = self.browser.execute_async_script(
            SET_LOCATION_JS, address, lat, lng, geo_session_id
        )
        logger.info(f"Location '{self.location}' set")
