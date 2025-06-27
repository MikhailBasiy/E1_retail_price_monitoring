import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

from parsers.base_parser import BaseParser
from parsers.config import geo_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class StolplitParser(BaseParser):
    def __init__(self):
        self.start_url = "https://www.stolplit.ru/"
        self.cookies = [
            {
                "name": "BITRIX_SM_REGION_ID",
                "value": "1",
                "domain": ".stolplit.ru",
                "secure": False,
                "httpOnly": False,
            }
        ]
        self.browser = uc.Chrome()
        self.timeout = 10
        self.by = By.XPATH
        self.skipping_tag_locators = [
            '//span[text()="Сообщить о наличии"]',
            '//p[@class="text_404" and text()="Ошибка 404. Нет такой страницы"]',
        ]
        self.name_locator = '//span[@class="h1"]'
        self.price_locator = (
            '//div[@class="product-menu__price"]/div[@class="price--current"]'
        )
        self.min_delay = 2.0
        self.max_delay = 4.0

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
