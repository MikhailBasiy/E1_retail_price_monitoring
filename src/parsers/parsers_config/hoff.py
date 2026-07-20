GEO_SETTINGS = {"Москва": 19, "Новосибирск": 3922}

SET_LOCATION_JS = """
const cityId = arguments[0];

fetch(`https://hoff.ru/vue/city/set/?id=${cityId}`, {
    method: "GET",
    credentials: "include"
}).then(() => location.reload());
"""
