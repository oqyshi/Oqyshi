import requests

api_server = "http://geocode-maps.yandex.ru/1.x/"

params = {
    "apikey": '40d1649f-0493-4b70-98ba-98533de7710b',
    "format": 'json',
    "geocode": 'almaty towers'
}
response = requests.get(api_server, params=params)
json_response = response.json()
toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
toponym_address = toponym["metaDataProperty"]["GeocoderMetaData"]["text"]
address_ll = "_".join(toponym["Point"]["pos"].split())
address = toponym_address
print([toponym_address])

map_params = {
    "ll": ",".join(address_ll.split('_')),
    "spn": "0.005,0.005",
    "l": "map",
    'pt': ','.join(address_ll.split() + ['org'])
}

map_api_server = "http://static-maps.yandex.ru/1.x/"
response = requests.get(map_api_server, params=map_params)
map_file = f"static/img/{address_ll}.png"
with open(map_file, "wb") as file:
    file.write(response.content)