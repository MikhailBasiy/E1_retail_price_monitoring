GEO_SETTINGS = {
    "Москва": {
        "address": "Москва, Тверская улица, д. 6 с6, кв. 1",
        "addressId": "bNxz5HpA8Xpo-f3c4eu2W47HkODd",
        "officeId": 373796,
        "dest": 1259571048,
        "sign": "EE5peD27CJM=",
        "latitude": 55.760591,
        "longitude": 37.611904,
        "currency": "RUB",
        "locale": "ru",
        "destinations": [-1029256, 0, -2162196, 1259571048],
    },
    "Новосибирск": {
        "address": "Новосибирск, улица Достоевского, д. 16, кв. 26",
        "addressId": "QdefdT1rYitChV-1l-qd-vyxahi5",
        "officeId": 103597,
        "dest": -364763,
        "sign": "+bvUmH/5wxU=",
        "latitude": 55.04547,
        "longitude": 82.917869,
        "currency": "RUB",
        "locale": "ru",
        "destinations": [-1029256, 0, -1751445, -364763],
    },
}

SET_LOCATION_JS = """
const location = arguments[0];

const geo = {
    time: Date.now(),
    data: {
        xinfo:
            `appType=1&curr=${location.currency.toLowerCase()}&dest=${location.dest}` +
            `&spp=30&hide_vflags=4294967296&hide_dtype=15&ab_testing=false`,

        address: location.address,
        addressKey: "userAddress.fallback.ru",

        latitude: location.latitude,
        longitude: location.longitude,

        currency: location.currency,
        locale: location.locale,

        destinations: location.destinations,

        addressDataSign:
            `officeId=${location.officeId}` +
            `&dest=${location.dest}` +
            `&sign=${location.sign}` +
            `&lat=${location.latitude}` +
            `&lng=${location.longitude}`,

        addressType: "courier",
        addressId: location.addressId,

        dt: Math.floor(Date.now() / 1000),
        shard: 0,
        ip: "",
        userDataSign: ""
    }
};

localStorage.setItem("geo-data-v1-0", JSON.stringify(geo));

return true;
"""
# const callback = arguments[arguments.length - 1];

# const geo = {
#     time: Date.now(),
#     data: {
#         xinfo: "appType=1&curr=rub&dest=-364763&spp=30&hide_vflags=4294967296&hide_dtype=15&ab_testing=false",
#         address: "Новосибирск, улица Достоевского, д. 16, кв. 26",
#         addressKey: "userAddress.fallback.ru",
#         latitude: 55.04547,
#         longitude: 82.917869,
#         currency: "RUB",
#         locale: "ru",
#         destinations: [-1029256, 0, -1751445, -364763],
#         addressDataSign: "officeId=103597&dest=-364763&sign=+bvUmH/5wxU=&lat=55.04547&lng=82.917869",
#         addressType: "courier",
#         addressId: "QdefdT1rYitChV-1l-qd-vyxahi5",
#         dt: Math.floor(Date.now() / 1000),
#         shard: 0,
#         ip: "",
#         userDataSign: ""
#     }
# };

# localStorage.setItem("geo-data-v1-0", JSON.stringify(geo));
# """
