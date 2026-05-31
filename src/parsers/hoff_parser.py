import undetected_chromedriver as uc
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from parsers.base_parser import BaseParser
from parsers.config import geo_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class HoffParser(BaseParser):
    def __init__(self):
        self.start_url = "https://www.hoff.ru/"
        self.set_location_script = """
            fetch("https://hoff.ru/vue/city/set/?id=19", {
                method: "GET",
                credentials: "include"
            }).then(() => location.reload());
            """
        self.timeout = 15
        self.by = By.XPATH
        self.skipping_tag_locators = [
            '//div[@class="no-product-text" and text()=" Этот товар закончился :( "]',
            '//span[@class="hoff-button__content" and text()="Нет в наличии"]',
        ]
        self.name_locator = '//h1[@class="product-header"]/span'
        self.price_locator = '//span[@class="price-actual"]'
        self.min_delay = 4.0
        self.max_delay = 7.0

        super().__init__(
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

    def _check_page_loaded(self):
        wait = WebDriverWait(self.browser, self.timeout)
        try:
            wait.until(EC.visibility_of_element_located((self.by, self.name_locator)))
            wait.until(EC.visibility_of_element_located((self.by, self.price_locator)))
        except TimeoutException:
            return False
        else:
            return True
