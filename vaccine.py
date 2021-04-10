import os
import logging
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
from config import GOOGLE_MAPS_API_KEY


# A street address or latitude, longitude around which to search.
SEARCH_ADDRESS = "2849 Street Rd, Doylestown, PA 18902"
STATE = "PA"

# How far you're willing to travel to be vaccinated (in miles)
MAX_DISTANCE = 15

SECONDS_BETWEEN_SCANS = 60
URL = ["https://www.vaccinespotter.org/api/v0/states/", ".json"]

logging.basicConfig(
    filename="vaccine.log", encoding="utf-8", filemode="w", level=logging.INFO
)

# Geolocator settings that don't need to be called each loop
geolocator = Nominatim(user_agent="scott@scottlarsen.com")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)


def convert_text_address_to_gps(text_address, geolocations):
    """Converts plain-text street address to (lat, long) tuple."""

    if text_address not in geolocations:
        try:  # Try's the free geopy Nominatum geocoder.
            sleep(1)
            text_address_geocoded = geocode(text_address)
            geolocations[text_address] = (
                text_address_geocoded.latitude,
                text_address_geocoded.longitude,
            )
            logging.info(f"Geopy: {text_address}")

        except AttributeError as e:  # Resorts to the Google Maps geocoder on failure
            logging.info(f"Google: {text_address}")
            clinic_address = gmaps.geocode(text_address)
            geolocations[text_address] = (
                clinic_address[0]["geometry"]["location"]["lat"],
                clinic_address[0]["geometry"]["location"]["lng"],
            )
    else:
        logging.info(f"Geolocations: {text_address}")
    return geolocations[text_address]


def find_distance(SEARCH_ADDRESS_GPS, clinic_gps):
    """Finds the distance in miles between the search point and each clinic GPS"""
    return distance.distance(SEARCH_ADDRESS_GPS, clinic_gps).miles


def query_vaccinespotter():
    """Queries the VaccineSpotter API for available appointments"""
    response = requests.get(URL[0] + STATE + URL[1])
    json_response = response.json()
    return json_response["features"]


def main():

    # Load or create the pickle to save the dictionary of geolocated addresses.
    pickle_filename = STATE + "_geolocations.p"
    if os.path.isfile(pickle_filename):
        geolocations = pickle.load(open(pickle_filename, "rb"))
    else:
        geolocations = {}

    available_last_time = []

    # Resolve SEARCH_ADDRESS to GPS tuple SEARCH_ADDRESS_GPS
    global SEARCH_ADDRESS
    if isinstance(SEARCH_ADDRESS, str):
        SEARCH_ADDRESS_GPS = convert_text_address_to_gps(SEARCH_ADDRESS, geolocations)
    elif isinstance(SEARCH_ADDRESS, tuple):
        SEARCH_ADDRESS_GPS = SEARCH_ADDRESS

    while True:

        datetime_UTC = datetime.utcnow().replace(tzinfo=UTC)
        print(f"\nRunning at {str(datetime.now())}\n")

        locations = query_vaccinespotter()
        available_now = []

        # Check each clinic location from the API
        for location in locations:
            location_properties = location["properties"]
            if location_properties["appointments_available"]:
                street_address = location_properties["address"]

                # If the location doesn't have a street address, swap in City & State.
                if not isinstance(street_address, str):
                    address = (
                        f"{location_properties['city']}, {location_properties['state']}"
                    )
                else:
                    address = (
                        f"{street_address} "
                        + f"{location_properties['city'].strip()}, "
                        + f"{location_properties['state'].strip()} "
                        + f"{location_properties['postal_code']}"
                    )

                # If we've already geolocated the address, pull GPS coords from pickle.
                gps_address = convert_text_address_to_gps(address, geolocations)

                # Check the distance between search point and clinic GPS.
                # Add to available_last_time so we don't notify multiple times
                # for same location.
                distance_ = int(find_distance(SEARCH_ADDRESS_GPS, gps_address))
                if (
                    distance_ < MAX_DISTANCE
                    and location_properties["id"] not in available_last_time
                ):
                    available_last_time.append(location_properties["id"])

                    last_updated = location_properties["appointments_last_modified"]
                    time_diff_in_minutes = int(
                        (datetime_UTC - parser.parse(last_updated)).total_seconds()
                        // 60
                    )

                    available_now.append(
                        [
                            distance_,
                            f"{location_properties['name']}\n"
                            + f"{location_properties['address']}\n"
                            + f"{location_properties['city']}, {STATE}"
                            + f"{(location_properties['postal_code']).strip()}\n"
                            + f"{distance_} miles away\n"
                            + f"{location_properties['url']}\n"
                            + f"Updated {time_diff_in_minutes} minutes ago\n",
                        ]
                    )

        available_now.sort()
        for site in available_now:
            print(site[1])

        # Cache street address -> GPS translations to pickle file.
        pickle.dump(geolocations, open(pickle_filename, "wb"))

        sleep(SECONDS_BETWEEN_SCANS)


if __name__ == "__main__":
    main()
