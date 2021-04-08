import json
import requests
import webbrowser
import googlemaps
from time import sleep
from pytz import UTC
from geopy.geocoders import Nominatim
from geopy import distance
from geopy.extra.rate_limiter import RateLimiter
from datetime import datetime
from pprint import pprint
from geopy.geocoders import GoogleV3

from config import API_KEY


URL = ["https://www.vaccinespotter.org/api/v0/states/", ".json"]
# SEARCH_ADDRESS = 40.355167700374516, -75.04352481198514
# SEARCH_ADDRESS = "480 Linden Ave, Doylestown, PA 18901"
SEARCH_ADDRESS = "2849 Street Rd, Doylestown, PA 18902"
STATE = "PA"
MAX_DISTANCE = 100
TIME_BETWEEN_SCANS = 60

# Geolocator calls that don't need to be called each loop
geolocator = Nominatim(user_agent="junk@scottlarsen.com")
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)
gmaps = googlemaps.Client(key=API_KEY)


def open_json(file_):
    """Open json cache of address conversions to GPS lat/ long"""
    with open(file_) as f:
        return json.load(f)
    # return geolocations


def write_json(dict_, filename_):
    """Save json cache of address conversions to GPS lat/ long"""
    with open(filename_, "w") as json_file:
        json.dump(dict_, json_file)


def convert_text_address_to_gps(text_address):
    try:
        sleep(1)
        text_address_geocoded = geocode(text_address)
        return (text_address_geocoded.latitude, text_address_geocoded.longitude)
    except AttributeError as e:
        print("\nQuerying Google\n")
        print(f"{text_address = }")
        clinic_address = gmaps.geocode(text_address)
        return (
            clinic_address[0]["geometry"]["location"]["lat"],
            clinic_address[0]["geometry"]["location"]["lng"],
        )


def find_distance(SEARCH_ADDRESS, clinic_gps):
    return distance.distance(SEARCH_ADDRESS, clinic_gps).miles


# def find_distance(SEARCH_ADDRESS, clinic_location):
#     try:
#         clinic_address = geolocator.geocode(clinic_location)
#         clinic_gps = (clinic_address.raw["lat"], clinic_address.raw["lon"])
#     except AttributeError as e:
#         clinic_address = gmaps.geocode(clinic_location)
#         clinic_gps = (
#             clinic_address[0]["geometry"]["location"]["lat"],
#             clinic_address[0]["geometry"]["location"]["lng"],
#         )

#     return distance(SEARCH_ADDRESS, clinic_gps).miles

# def find_distance(SEARCH_ADDRESS, clinic_gps):
#     return distance(SEARCH_ADDRESS, clinic_gps).miles

# # def find_distance(SEARCH_ADDRESS, clinic_location):
# #     try:
# #         clinic_address = geolocator.geocode(clinic_location)
# #         clinic_gps = (clinic_address.raw["lat"], clinic_address.raw["lon"])
# #     except AttributeError as e:
# #         clinic_address = gmaps.geocode(clinic_location)
# #         clinic_gps = (
# #             clinic_address[0]["geometry"]["location"]["lat"],
# #             clinic_address[0]["geometry"]["location"]["lng"],
# #         )

# #     return distance(SEARCH_ADDRESS, clinic_gps).miles

#     # clinic_address = geolocator.geocode((clinic_location))
#     # clinic_gps = (clinic_address.raw["lat"], clinic_address.raw["lon"])
#     # return distance(SEARCH_ADDRESS, clinic_gps).miles


# addy = "4960 William Flynn Hwy Ste 10 Allison Park, PA 15101"
# addy = "5990 University Blvd Ste30 Moon Township, PA 15108"
# print(find_distance(addy))
# geolocator = GoogleV3()
# gmaps = googlemaps.Client(key=API_KEY)
# clinic_address = gmaps.geocode(addy)
# clinic_gps = (
#     clinic_address[0]["geometry"]["location"]["lat"],
#     clinic_address[0]["geometry"]["location"]["lng"],
# )
# print(clinic_gps)

# clinic_location = "916, State Street, Erie, Pennsylvania, 16501"
# # clinic_location = "2849 Street Rd, Doylestown, PA 18902"
# clinic_address = geolocator.geocode((clinic_location))
# clinic_gps = (clinic_address.longitude, clinic_address.latitude)

# pprint(clinic_address.raw["lat"])
# print(find_distance(clinic_location))


# errors = []


# def write_json(filename):
#     with open("locations.json", "w") as locations_json:
#         locations_json.write(json.dumps(filename))


# pprint(locations)
# print(locations[0]["properties"])
# errors = []
def main():
    global SEARCH_ADDRESS
    geolocations = open_json("geolocations.json")
    if isinstance(SEARCH_ADDRESS, str):
        SEARCH_ADDRESS = convert_text_address_to_gps(SEARCH_ADDRESS)
    print(f"{SEARCH_ADDRESS = }")
    while True:
        response = requests.get(URL[0] + STATE + URL[1])
        datetime_ = datetime.utcnow().replace(tzinfo=UTC)
        print(datetime_)
        json_ = response.json()
        locations = json_["features"]
        time_at_start = datetime.now()
        print(f"{time_at_start = }")
        # for key in geolocations.keys():
        #     print(f"{key = }\n{type(key)}")
        # print(f"{geolocations = }")
        for location in locations:
            location_properties = location["properties"]
            if location_properties["appointments_available"]:
                street_address = location_properties["address"]
                if not isinstance(street_address, str):
                    address = (
                        f"{location_properties['city']}, {location_properties['state']}"
                    )
                    # print(address, "\n", location_properties, "\n\n")
                else:
                    address = f"{street_address} {location_properties['city']}, {location_properties['state']} {location_properties['postal_code']}"
                # try:
                #     print(f"{location_properties['id'] = }")
                #     print(f"{type(location_properties['id']) = }")
                #     # print(f"{geolocations[location_properties['id']] = }")
                #     print(f"{geolocations[str(location_properties['id'])] = }")
                # except:
                #     pass
                if str(location_properties["id"]) in geolocations:
                    # print("Looking for GPS address in dictionary")
                    gps_address = geolocations[str(location_properties["id"])]
                    # print("Found GPS coordinates in the dictionary")
                else:
                    print(f"GPS address dictionary lookup failed on {gps_address}")
                    gps_address = convert_text_address_to_gps(address)
                    geolocations[location_properties["id"]] = gps_address
                    # print(find_distance(address))
                    # print(type(find_distance(address)))
                distance_ = int(find_distance(SEARCH_ADDRESS, gps_address))
                if distance_ < MAX_DISTANCE:
                    # pprint(location_properties)
                    # if location_properties["address"] is None or location_properties["address"] == "None":

                    print(
                        f"""
                        {location_properties["name"]}
                        {location_properties["address"]}
                        {location_properties["city"]}, PA {location_properties["postal_code"]}
                        {distance_} miles away
                        {location_properties["url"]}
                        {location_properties["appointments_last_fetched"]}
                        {location_properties["appointments_last_modified"]}
                        """
                    )
                # except AttributeError as e:
                #     # errors.append(
                #     #     [
                #     #         f"{location_properties['address']} {location_properties['city']}, PA {location_properties['postal_code']}",
                #     #         location_properties,
                #     #     ]
                #     # )
                #     print("Error on:", e)
                #     print(address)
                #     print(location_properties, "\n")
        write_json(geolocations, "geolocations.json")
        sleep(TIME_BETWEEN_SCANS)
    #         # pprint(location_properties["address"])
    # #         # print("\n")
    # #         # pprint(location_properties)
    # #         # print("\n\n")
    # #         # else:
    # #     print(f"{location_properties['address']}", location_properties["appointments_available"], "\n")
    # # # json_[:10]

    # # # pprint(json_)
    # print("Errors")
    # for error in errors:
    #     print(error[0], "\n", error[1], "\n")


if __name__ == "__main__":
    main()

# errors.append(location_properties)

# write_json(errors)
#         if (
#             None
#             in [street_address, location_properties["city"], location_properties["postal_code"]]
#             # and location_properties["address"]
#         ):
#             # print(["\n", location_properties["address"], location_properties["city"], location_properties["postal_code"], "\n"])
