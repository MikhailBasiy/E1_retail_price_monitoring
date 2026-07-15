import uuid

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from parsers.base_parser import BaseParser
from parsers.config import geo_settings
from utils.logger import get_logger

logger = get_logger(__name__)

SET_LOCATION_JS = """
const callback = arguments[arguments.length - 1];
const address = arguments[0];
const lat = arguments[1];
const lng = arguments[2];
const geoSessionId = arguments[3];

const baseURL = "https://ozon.com";
const viewportDelta = 0.002;
const leftBottomLat = lat - viewportDelta;
const rightTopLat   = lat + viewportDelta;
const leftBottomLng = lng - viewportDelta;
const rightTopLng   = lng + viewportDelta;

const mapBlock = {
    viewport: {
        leftBottom: { latitude: leftBottomLat, longitude: leftBottomLng },
        rightTop:   { latitude: rightTopLat,   longitude: rightTopLng }
    },
    zoom: 17,
    previousCoordinates: { latitude: lat, longitude: lng }
};

const mapInfo = {
    geoSessionId: geoSessionId,
    preferredGeoProviders: {
        suggest:     ["maps_v1_courier_vector_v2", "maps_nspd", "maps_fallback_blocker", "yandex"],
        geocode:     ["maps_v1_courier_vector_v2", "yandex"],
        revGeocode:  ["maps_revgeocode_migeo", "maps_nspd", "yandex"]
    }
};

const commonHeaders = {
    "accept":             "application/json",
    "accept-language":    "en-US,en;q=0.9",
    "cache-control":      "no-cache",
    "content-type":       "application/json",
    "pragma":             "no-cache",
    "priority":           "u=1, i",
    "sec-ch-ua":          '"Not;A=Brand";v="8", "Chromium";v="150", "Google Chrome";v="150"',
    "sec-ch-ua-mobile":   "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest":     "empty",
    "sec-fetch-mode":     "cors",
    "sec-fetch-site":     "same-origin",
    "x-o3-app-name":      "dweb_client"
};

async function doPost(path, body) {
    const resp = await fetch(baseURL + path, {
        headers: commonHeaders,
        referrer: baseURL + "/",
        body: JSON.stringify(body),
        method: "POST",
        mode: "cors",
        credentials: "include"
    });
    return resp.json();
}

(async () => {
    try {
        // Step 1 — isGeolocationOnInit
        await doPost(
            "/api/entrypoint-api.bx/page/json/v2"
                + "?url=%2Fmodal%2FcommonDelivery%3Flat%3D" + lat
                + "%26long%3D" + lng + "%26nfr%3Dt%26pid%3D4%26pv%3D2%26tab%3Dc",
            {
                isGeolocationOnInit: false,
                mapInfo: mapInfo,
                form: { addressTail: address },
                geolocation: { coords: {}, isAvailable: false },
                map: mapBlock
            }
        );

        // Step 2 — pid=5
        await doPost(
            "/api/entrypoint-api.bx/page/json/v2"
                + "?url=%2Fmodal%2FcommonDelivery%3Fdt%3D1%26lat%3D" + lat
                + "%26long%3D" + lng + "%26nfr%3Dt%26pid%3D5%26pv%3D2%26tab%3Dc",
            {
                form: { addressTail: address },
                geolocation: { coords: {}, isAvailable: false },
                map: mapBlock,
                mapInfo: mapInfo
            }
        );

        // Step 3 — pid=7 (full form)
        const result = await doPost(
            "/api/entrypoint-api.bx/page/json/v2"
                + "?url=%2Fmodal%2FcommonDelivery%3Fdt%3D1%26lat%3D" + lat
                + "%26long%3D" + lng + "%26nfr%3Dt%26pid%3D7%26pv%3D2%26tab%3Dc",
            {
                form: {
                    addressLabel: "",
                    addressTail: address,
                    apartment: "",
                    entrance: "",
                    floor: "",
                    intercom: "",
                    comment: "",
                    receiverName: "",
                    receiverPhone: ""
                },
                geolocation: { coords: {}, isAvailable: false },
                map: mapBlock,
                mapInfo: mapInfo
            }
        );

        callback(result);
    } catch (err) {
        callback({ error: err.message });
    }
})();
"""


class OzonParser(BaseParser):
    def __init__(self):
        self.start_url = "https://www.ozon.ru/"
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
        self.min_delay = 5.0
        self.max_delay = 8.0

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
        geo = geo_settings[location]
        lat = geo["latitude"]
        lng = geo["longitude"]

        self.browser.execute_cdp_cmd(
            "Browser.grantPermissions",
            {
                "origin": self.start_url,
                "permissions": ["geolocation"],
            },
        )
        self.browser.execute_cdp_cmd("Emulation.setGeolocationOverride", geo)
        self._open_page(self.start_url)
        self._random_wait()

        # Obtain a real address string for the coordinates (reuse the city name
        # or provide a street address via config if needed).
        address = location
        geo_session_id = str(uuid.uuid4())

        result = self.browser.execute_async_script(
            SET_LOCATION_JS, address, lat, lng, geo_session_id
        )
        logger.info(f"Location '{location}' set.")
        super()._random_wait()
