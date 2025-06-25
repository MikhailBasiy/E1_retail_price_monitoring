import undetected_chromedriver as uc
from selenium.webdriver.common.by import By

from parsers.base_parser import BaseParser

from parsers.config import geo_settings
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils.logger import get_logger

logger = get_logger(__name__)


class OzonParser(BaseParser):
    def __init__(self):
        self.start_url = "https://www.ozon.ru/"
        self.browser = uc.Chrome()
        self.timeout = 10
        self.by = By.XPATH
        self.skipping_text=[
            "Этот товар закончился",
            "Товар не доставляется в ваш регион",
            "Такой страницы не существует",
            "Узнать о поступлении",
        ]
        self.name_locator='//div[@data-widget="webProductHeading"]/h1'
        self.price_locator=(
            '//div[@data-widget="webPrice"]/div/div[2]/div/div/span | '
            '//div[@data-widget="webPrice"]/div/div/div/div/span'
        )
        self.min_delay=3.0
        self.max_delay=7.0

        super().__init__(
            browser=self.browser,
            timeout=self.timeout,
            by=self.by,
            skipping_text=self.skipping_text,
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
            "Emulation.setGeolocationOverride", 
            geo_settings[location]
        )
        self.browser.get(self.start_url)
        super()._random_wait()
        wait = WebDriverWait(self.browser, self.timeout)
        overlay = wait.until(EC.invisibility_of_element_located((self.by, "//button[div[div[text()='Сменить']]]/div[2]")))
        try:
            self.browser.execute_script("arguments[0].remove();", overlay)
        except:
            pass
        button = wait.until(EC.element_to_be_clickable(
            (self.by, "//button/div/div[text()='Сменить']")
        ))
        button.click()
        logger.info(f"Location {location} is set")
        super()._random_wait()
