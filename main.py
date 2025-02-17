import json
import os
from dotenv import load_dotenv

import folium
import requests
from geopy.distance import geodesic


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(
        base_url,
        params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        }
    )
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']
    if not found_places:
        return None
    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split()
    return lat, lon


def get_distance(shop):
    return shop["distance"]


def get_coffee_shops(user_coords):
    with open("coffee.json", "r", encoding="cp1251") as file:
        coffee_data = json.load(file)

    coffee_shops = []
    for shop in coffee_data:
        shop_coords = (shop["Latitude_WGS84"], shop["Longitude_WGS84"])
        distance = geodesic(user_coords, shop_coords).kilometers
        coffee_shops.append({
            "title": shop['Name'],
            "distance": distance,
            "latitude": shop["Latitude_WGS84"],
            "longitude": shop["Longitude_WGS84"]
        })

    coffee_shops.sort(key=get_distance)
    return coffee_shops[:5]


def create_map(user_coords, coffee_shops):
    map_object = folium.Map(
        location=[float(user_coords[0]), float(user_coords[1])],
        zoom_start=15
    )

    folium.Marker(
        location=[float(user_coords[0]), float(user_coords[1])],
        tooltip="Вы здесь",
        popup="Ваше местоположение",
        icon=folium.Icon(color="red", icon="home")
    ).add_to(map_object)

    for shop in coffee_shops:
        folium.Marker(
            location=[shop["latitude"], shop["longitude"]],
            tooltip=f"{shop['title']} - {shop['distance']:.2f} км",
            popup=shop['title'],
            icon=folium.Icon(color="blue", icon="coffee")
        ).add_to(map_object)

    return map_object


def main():
    load_dotenv()
    apikey = os.getenv("apikey")

    user_location = input("Где вы находитесь? ")
    user_coords = fetch_coordinates(apikey, user_location)

    nearest_shops = get_coffee_shops(user_coords)

    for shop in nearest_shops:
        print(shop['title'])

    coffee_map = create_map(user_coords, nearest_shops)
    coffee_map.save("coffee_map.html")


if __name__ == "__main__":
    main()
