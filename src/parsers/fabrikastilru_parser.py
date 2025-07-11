import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

from parsers.base_parser import BaseParser
from parsers.config import geo_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class FabrikaStilParser(BaseParser):
    def __init__(self):
        self.start_url = "https://fabrika-stil.ru/"
        self.browser = uc.Chrome()
        self.timeout = 10
        self.by = By.XPATH
        self.skipping_tag_locators = [
            '//div[@class="h" and contains(text(), "Ошибка 404: ")]',
        ]
        self.name_locator = '//h1[@class="h3 js_name"]'
        self.price_locator = '//div[@class="cost js_cost_e ModelPrice"]'
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
        pass
