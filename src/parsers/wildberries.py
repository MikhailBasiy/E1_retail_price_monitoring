import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from parsers.base_parser import BaseParser
from parsers.config import geo_settings
from parsers.js_scripts.wildberries import GEO_SETTINGS, SET_LOCATION_JS
from utils.logger import get_logger

logger = get_logger(__name__)


class WildberriesParser(BaseParser):
    def __init__(self, location: str):
        self.location = location
        self.start_url = "https://www.wildberries.ru/"
        self.timeout = 10
        self.by = By.XPATH
        self.skipping_tag_locators = [
            '//h1[@class="content404__title"]',
            '//span[contains(@class, "soldOutProductText")]',
        ]
        self.name_locator = '//h2[contains(@class, "productTitle")]'
        self.price_locator = '//*[contains(@class, "priceBlockFinalPrice")]'
        self.city_script = """
            const el = document.evaluate(
                "//span[@data-wba-header-name='DLV_Adress']",
                document,
                null,
                XPathResult.FIRST_ORDERED_NODE_TYPE,
                null
            ).singleNodeValue;

            return el ? el.textContent.split(",")[0].trim() : null;
            """

        self.min_delay = 4.0
        self.max_delay = 7.0

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
        self.browser.execute_cdp_cmd(
            "Browser.grantPermissions",
            {
                "origin": f"{self.start_url}",
                "permissions": ["geolocation"],
            },
        )
        self.browser.execute_cdp_cmd(
            "Emulation.setGeolocationOverride", geo_settings[self.location]
        )
        self._open_page(self.start_url)
        super()._random_wait()
        result = self.browser.execute_script(
            SET_LOCATION_JS, GEO_SETTINGS[self.location]
        )

        self.browser.refresh()
        logger.info(f"result: {result}")
        logger.info(f"Location '{self.location}' set")
