import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

from parsers.base_parser import BaseParser
from parsers.config import geo_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class MnogomebeliParser(BaseParser):
    def __init__(self):
        self.start_url = "https://mnogomebeli.com/"
        self.cookies = [
            {
                "name": "BITRIX_SM_2021_IPLOCATION_MM",
                "value": "%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0",
                "domain": ".mnogomebeli.com",
                "secure": False,
                "httpOnly": False,
            },
            {
                "name": "BITRIX_SM_2021_this-city-info",
                "value": "%7B%22is_city%22%3A%22%5Cu041c%5Cu043e%5Cu0441%5Cu043a%5Cu0432%5Cu0430%22%2C%22is_city_code%22%3A%22moskva%22%2C%22is_price%22%3A%221%22%2C%22is_phone_number%22%3A%2289301651604%22%2C%22is_phone%22%3A%228%20%3Cspan%3E%28%3C%5C%2Fspan%3E930%3Cspan%3E%29%3C%5C%2Fspan%3E%20165-16-04%22%7D",
                "domain": ".mnogomebeli.com",
                "secure": False,
                "httpOnly": True,
            },
            {
                "name": "BITRIX_SM_2021_this-has_city",
                "value": "%22Y%22",
                "domain": ".mnogomebeli.com",
                "secure": False,
                "httpOnly": True,
            },
        ]
        self.browser = uc.Chrome()
        self.timeout = 10
        self.by = By.XPATH
        self.skipping_tag_locators = [
            '//h1[@class="notfound__title" and text()="Страница не существует"]'
        ]
        self.name_locator = '//h1[@class="item-header__title t-h1"]'
        self.price_locator = '//span[@id="product_price_sale"]'
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
        for cookie in self.cookies:
            self.browser.delete_cookie(cookie["name"])
            self.browser.add_cookie(cookie)
        self.browser.get(self.start_url)
        logger.info(f"Location {location} is set")
        super()._random_wait()
