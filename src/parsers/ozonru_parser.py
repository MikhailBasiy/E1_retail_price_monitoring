import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

from parsers.base_parser import BaseParser


class OzonParser(BaseParser):
    def __init__(self):
        browser = uc.Chrome()
        super().__init__(
            browser,
            timeout=10,
            by=By.XPATH,
            name_locator='//div[@data-widget="webProductHeading"]/h1',
            price_locator=(
                '//div[@data-widget="webPrice"]/div/div[2]/div/div/span | '
                '//div[@data-widget="webPrice"]/div/div/div/div/span'
            ),
            min_delay=3.0,
            max_delay=7.0,
        )
