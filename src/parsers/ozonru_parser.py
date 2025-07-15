import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from parsers.base_parser import BaseParser
from parsers.config import geo_settings
from utils.logger import get_logger

logger = get_logger(__name__)


class OzonParser(BaseParser):
    def __init__(self):
        self.start_url = "https://www.ozon.ru/"
        self.set_location_script = """
            fetch("https://www.ozon.ru/api/entrypoint-api.bx/page/json/v2?url=%2Fmodal%2FcommonDelivery%3Fazimuth%3D0.130473684379%26dt%3D1%26lat%3D55.7636337%26long%3D37.5963307%26msid%3De9e10a70-9402-4004-996c-010096328bcf%26nfr%3Dt%26pid%3D7%26pv%3D2%26pxlw%3D109.390625%26src_main%3D%252F%253Fundefinedrr%25253D1%252526abt_att%25253D1%26tab%3Dc", {
              "headers": {
                "accept": "application/json",
                "accept-language": "en-US,en;q=0.9",
                "cache-control": "no-cache",
                "content-type": "application/json",
                "pragma": "no-cache",
                "priority": "u=1, i",
                "sec-ch-ua": "\\"Not)A;Brand\\";v=\\"8\\", \\"Chromium\\";v=\\"138\\", \\"Google Chrome\\";v=\\"138\\"",
                "sec-ch-ua-mobile": "?0",
                "sec-ch-ua-platform": "\\"Windows\\"",
                "sec-fetch-dest": "empty",
                "sec-fetch-mode": "cors",
                "sec-fetch-site": "same-origin",
                "x-o3-app-name": "dweb_client",
                "x-o3-app-version": "release_14-6-2025_400d776f",
                "x-o3-manifest-version": "frontend-ozon-ru:400d776fe68f400fa36e7161a52673bc0fffb2d5,sf-render-api:6f19f23dcf46690966a6aed7a4773f60adddc7d0,rtb-render-api:ce8bfc5d972a18baed949deced0b05ed178f1075",
                "x-o3-parent-requestid": "dad467cf798ca2f6f8b18f11207bacdb",
                "x-page-view-id": "45738a9a-3b3e-47d0-dfe7-cb7a3e453d63"
              },
              "referrer": "https://www.ozon.ru/?__rr=1&abt_att=1",
              "body": "{\\"mapInfo\\":{\\"geoSessionId\\":\\"5979ebb3-1565-4502-93fc-4b81012eaec6\\",\\"preferredGeoProviders\\":{\\"suggest\\":[\\"maps_selfsuggest_vector_misspell\\",\\"yandex\\"],\\"geocode\\":[\\"maps_selfsuggest_vector_misspell\\",\\"yandex\\"],\\"revGeocode\\":[\\"maps_selfsuggest_vector_misspell\\",\\"yandex\\"]}},\\"form\\":{\\"addressLabel\\":\\"\\",\\"addressTail\\":\\"Москва, Большой Козихинский переулок, 14 строение 2\\",\\"apartment\\":\\"\\",\\"entrance\\":\\"\\",\\"floor\\":\\"\\",\\"intercom\\":\\"\\",\\"comment\\":\\"\\",\\"receiverName\\":\\"\\",\\"receiverPhone\\":\\"\\"},\\"geolocation\\":{\\"coords\\":{},\\"isAvailable\\":false},\\"map\\":{\\"viewport\\":{\\"leftBottom\\":{\\"latitude\\":55.76111777646078,\\"longitude\\":37.59574384919354},\\"rightTop\\":{\\"latitude\\":55.76614945785769,\\"longitude\\":37.59691748327561}},\\"zoom\\":17,\\"previousCoordinates\\":{\\"latitude\\":55.76363369832409,\\"longitude\\":37.59633066623457}}}",
              "method": "POST",
              "mode": "cors",
              "credentials": "include"
            });
        """
        self.browser = uc.Chrome()
        self.timeout = 10
        self.by = By.XPATH
        self.skipping_tag_locators = [
            '//h2[contains(text(), "Этот товар закончился")]',
            '//h2[contains(text(), "Товар не доставляется в ваш регион")]',
            '//h2[contains(text(), "Такой страницы не существует")]',
        ]
        self.name_locator = '//div[@data-widget="webProductHeading"]/h1'
        self.price_locator = (
            '//div[@data-widget="webPrice"]/div/div[2]/div/div/span | '
            '//div[@data-widget="webPrice"]/div/div/div/div/span'
        )
        self.min_delay = 3.0
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
        self.browser.execute_script(self.set_location_script)
        super()._random_wait()

    # def set_location(self, location: str):
    #     self.browser.execute_cdp_cmd(
    #         "Browser.grantPermissions",
    #         {
    #             "origin": f"{self.start_url}",
    #             "permissions": ["geolocation"],
    #         },
    #     )
    #     self.browser.execute_cdp_cmd(
    #         "Emulation.setGeolocationOverride", geo_settings[location]
    #     )
    #     self.browser.get(self.start_url)
    #     super()._random_wait()
    #     wait = WebDriverWait(self.browser, self.timeout)
    #     overlay = wait.until(
    #         EC.invisibility_of_element_located(
    #             (self.by, "//button[div[div[text()='Сменить']]]/div[2]")
    #         )
    #     )
    #     try:
    #         self.browser.execute_script("arguments[0].remove();", overlay)
    #     except:
    #         pass
    #     button = wait.until(
    #         EC.element_to_be_clickable((self.by, "//button/div/div[text()='Сменить']"))
    #     )
    #     button.click()
    #     logger.info(f"Location {location} is set")
    #     super()._random_wait()
