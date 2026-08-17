GEO_SETTINGS = {
    "Москва": {"city": 693, "region": 3366},
    "Новосибирск": {"city": 2636, "region": 1056},
}

SET_LOCATION_JS = """
const city = arguments[0];
const region = arguments[1];

return fetch("/ajax/choice-city.php", {
    method: "POST",
    credentials: "include",
    headers: {
        "Content-Type": "application/x-www-form-urlencoded",
        "X-Requested-With": "XMLHttpRequest"
    },
    body: `ajax=true&set=true&city=${city}&region=${region}`
});
"""
