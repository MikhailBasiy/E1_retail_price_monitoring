import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

from parsers.base_parser import BaseParser
from parsers.config import geo_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class LifemebelParser(BaseParser):
    def __init__(self):
        self.start_url = "https://lifemebel.ru/"
        self.set_location_script = """
            fetch("https://lifemebel.ru/?city_c=%D0%9C%D0%BE%D1%81%D0%BA%D0%B2%D0%B0+%D0%B8+%D0%9C%D0%9E&city_ext_id=11530", {
              "headers": {
                "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                "priority": "u=0, i",
                "sec-ch-ua": "\\"Not)A;Brand\\";v=\\"8\\", \\"Chromium\\";v=\\"138\\", \\"Google Chrome\\";v=\\"138\\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\\"Windows\\"",
                "sec-fetch-dest": "document",
                "sec-fetch-mode": "navigate",
                "sec-fetch-site": "same-origin",
                "sec-fetch-user": "?1",
                "upgrade-insecure-requests": "1"
              },
              "referrer": "https://lifemebel.ru/",
              "body": null,
              "method": "GET",
              "mode": "cors",
              "credentials": "include"
            });
        """
        self.browser = uc.Chrome()
        self.timeout = 10
        self.by = By.XPATH
        self.skipping_tag_locators = [
            '//div[@class="new-product-cta-not-available" and text()="Недоступен для продажи"]',
        ]
        self.name_locator = "//h1"
        self.price_locator = '//div[@itemprop="price"]'
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
        logger.info(f"Location {location} is set")
