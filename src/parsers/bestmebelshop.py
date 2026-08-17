import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

from parsers.base_parser import BaseParser
from parsers.config import geo_settings
from parsers.parsers_config.bestmebelshop import SUBDOMAINS
from utils.logger import get_logger

logger = get_logger(__name__)


class BestmebelshopParser(BaseParser):
    def __init__(self, location: str):
        self.location = location
        self.start_url = "https://bestmebelshop.ru/"
        self.timeout = 10
        self.by = By.XPATH
        self.skipping_tag_locators = ['h1[text()="Данная страница не найдена!"]']
        self.name_locator = "//h1"
        self.price_locator = (
            '//div[@class="price_main_cont"]/span[@class="catalog-price"]'
        )
        self.city_locator = '//div[@class="nbCitySelect_city_name"]'
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

    def set_location(self) -> None:
        self.subdomain = SUBDOMAINS[self.location]
