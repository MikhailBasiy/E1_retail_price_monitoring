import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

from parsers.base_parser import BaseParser
from parsers.config import geo_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class PmParser(BaseParser):
    def __init__(self):
        self.start_url = "https://pm.ru/"
        self.cookies = [
            {
                "name": "user_city",
                "value": "411",
                "domain": ".pm.ru",
                "secure": False,
                "httpOnly": False,
            },
            {
                "name": "user_region",
                "value": "13",
                "domain": ".pm.ru",
                "secure": False,
                "httpOnly": False,
            },
            {
                "name": "user_warehouse",
                "value": "1",
                "domain": ".pm.ru",
                "secure": False,
                "httpOnly": False,
            },
        ]
        self.timeout = 10
        self.by = By.XPATH
        self.skipping_tag_locators = [
            '//div[@class="out-stock-cart__text" and contains(text(), "Временно отсутствует")]',
            '//h1[contains(text(), "Ошибка HTTP 404")]',
        ]
        self.name_locator = '//h1[@id="good-title"]'
        self.price_locator = '//div[@id="current-price"]'
        self.city_locator = '//div[@class="header__top--city"]/span'
        self.min_delay = 4.0
        self.max_delay = 7.0

        super().__init__(
            timeout=self.timeout,
            by=self.by,
            skipping_tag_locators=self.skipping_tag_locators,
            name_locator=self.name_locator,
            price_locator=self.price_locator,
            city_locator=self.city_locator,
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
