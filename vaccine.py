import pickle
import requests
import googlemaps
from time import sleep
from pytz import UTC
from geopy.geocoders import Nominatim
from geopy import distance
from geopy.extra.rate_limiter import RateLimiter
from datetime import datetime
from dateutil import parser
from geopy.geocoders import GoogleV3

from config import API_KEY


URL = ["https://www.vaccinespotter.org/api/v0/states/", ".json"]
# SEARCH_ADDRESS = 40.355167700374516, -75.04352481198514
# SEARCH_ADDRESS = "480 Linden Ave, Doylestown, PA 18901"
SEARCH_ADDRESS = "2849 Street Rd, Doylestown, PA 18902"
STATE = "PA"
MAX_DISTANCE = 15
TIME_BETWEEN_SCANS = 60

# Geolocator calls that don't need to be called each loop
geolocator = Nominatim(user_agent="scott@scottlarsen.com")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
gmaps = googlemaps.Client(key=API_KEY)


def convert_text_address_to_gps(text_address):
    try:
        sleep(1)
        text_address_geocoded = geocode(text_address)
        text_address_gps = (
            text_address_geocoded.latitude,
            text_address_geocoded.longitude,
        )
        print("Successfully geocoded with Geopy")
        return text_address_gps
    except AttributeError as e:
        print(f"\nQuerying Google for {text_address}")
        clinic_address = gmaps.geocode(text_address)
        return (
            clinic_address[0]["geometry"]["location"]["lat"],
            clinic_address[0]["geometry"]["location"]["lng"],
        )


def find_distance(SEARCH_ADDRESS_GPS, clinic_gps):
    return distance.distance(SEARCH_ADDRESS_GPS, clinic_gps).miles


def main():
    global SEARCH_ADDRESS
    available_last_time = []
    # geolocations = open_json(STATE + "_geolocations.json")
    geolocations = pickle.load(open(STATE + "_geolocations.p", "rb"))
    print("Pickle loaded")
    if isinstance(SEARCH_ADDRESS, str):
        if SEARCH_ADDRESS in geolocations:
            SEARCH_ADDRESS_GPS = geolocations[SEARCH_ADDRESS]
        else:
            SEARCH_ADDRESS_GPS = convert_text_address_to_gps(SEARCH_ADDRESS)
            geolocations[SEARCH_ADDRESS] = SEARCH_ADDRESS_GPS

    print(f"{SEARCH_ADDRESS = }")
    print(f"{SEARCH_ADDRESS_GPS = }")
    while True:
        response = requests.get(URL[0] + STATE + URL[1])
        datetime_UTC = datetime.utcnow().replace(tzinfo=UTC)
        print(f"\n{str(datetime.now())}")
        json_ = response.json()
        locations = json_["features"]
        for location in locations:
            location_properties = location["properties"]
            if location_properties["appointments_available"]:
                street_address = location_properties["address"]
                if not isinstance(street_address, str):
                    address = (
                        f"{location_properties['city']}, {location_properties['state']}"
                    )
                else:
                    address = f"{street_address} {location_properties['city']}, {location_properties['state']} {location_properties['postal_code']}"
                if location_properties["id"] in geolocations:
                    gps_address = geolocations[location_properties["id"]]
                else:
                    gps_address = convert_text_address_to_gps(address)
                    geolocations[location_properties["id"]] = gps_address
                distance_ = int(find_distance(SEARCH_ADDRESS_GPS, gps_address))
                if (
                    distance_ < MAX_DISTANCE
                    and location_properties["id"] not in available_last_time
                ):
                    available_last_time.append(location_properties["id"])

                    print(
                        f"""
                        {location_properties["name"]}
                        {location_properties["address"]}
                        {location_properties["city"]}, PA {location_properties["postal_code"]}
                        {distance_} miles away
                        {location_properties["url"]}
                        Updated {int((datetime_UTC - parser.parse(location_properties["appointments_last_modified"])).total_seconds()//60)} minutes ago
                        """
                    )
        pickle.dump(geolocations, open(STATE + "_geolocations.p", "wb"))
        print("Pickle updated")
        sleep(TIME_BETWEEN_SCANS)


if __name__ == "__main__":
    main()
