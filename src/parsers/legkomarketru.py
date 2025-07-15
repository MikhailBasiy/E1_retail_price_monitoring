import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

from parsers.base_parser import BaseParser
from parsers.config import geo_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class LegkomarketParser(BaseParser):
    def __init__(self):
        self.start_url = "https://www.legkomarket.ru/"
        self.set_location_script = """
            fetch("https://legkomarket.ru/ajax/select_city.php", {
              "headers": {
                "accept": "*/*",
                "accept-language": "en-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7",
                "cache-control": "no-cache",
                "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "sec-ch-ua": "\\"Not)A;Brand\\";v=\\"8\\", \\"Chromium\\";v=\\"138\\", \\"Google Chrome\\";v=\\"138\\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\\"Windows\\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "x-requested-with": "XMLHttpRequest"
              },
              "referrer": "https://legkomarket.ru/",
              "body": "SET_CITY=Y&CITY_ID=15162&URL=%2F",
              "method": "POST",
              "mode": "cors",
              "credentials": "include"
            });
        """
        self.browser = uc.Chrome()
        self.timeout = 10
        self.by = By.XPATH
        self.skipping_tag_locators = [
            '//div[@class="text text404" and contains(text(), "Страница не существует или неправильно набран адрес.")]',
        ]
        self.name_locator = "//h1"
        self.price_locator = '//span[@class="_price"]'
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
        self.browser.execute_script(self.set_location_script)
        super()._random_wait()
