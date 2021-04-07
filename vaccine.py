import json
import requests
import webbrowser
from time import sleep
from geopy.geocoders import Nominatim
from geopy.distance import distance
from datetime import datetime
from pprint import pprint

URL = ["https://www.vaccinespotter.org/api/v0/states/", ".json"]


# SEARCH_ADDRESS = 40.355167700374516, -75.04352481198514
SEARCH_ADDRESS = "480 Linden Ave, Doylestown, PA 18901"
STATE = "PA"
MAX_DISTANCE = 100


geolocator = Nominatim(user_agent="covid")
if isinstance(SEARCH_ADDRESS, str):
    SEARCH_ADDRESS = geolocator.geocode(SEARCH_ADDRESS)
    SEARCH_ADDRESS = (SEARCH_ADDRESS.latitude, SEARCH_ADDRESS.longitude)


def find_distance(clinic_location):
    clinic_address = geolocator.geocode(clinic_location)
    clinic_gps = (clinic_address.raw["lat"], clinic_address.raw["lon"])
    # return geodesic(SEARCH_ADDRESS, clinic_gps).miles
    # _distance = distance(SEARCH_ADDRESS, clinic_gps)
    return distance(SEARCH_ADDRESS, clinic_gps).miles

    clinic_address = geolocator.geocode((clinic_location))
    clinic_gps = (clinic_address.raw["lat"], clinic_address.raw["lon"])
    return distance(SEARCH_ADDRESS, clinic_gps).miles


addy = "4960 William Flynn Hwy Ste 10 Allison Park, PA 15101"
addy = "5990 University Blvd Ste30 Moon Township, PA 15108"
clinic_address = geolocator.geocode((addy))
print(clinic_address)

print(clinic_address)

# # clinic_location = "916, State Street, Erie, Pennsylvania, 16501"
# # # clinic_location = "2849 Street Rd, Doylestown, PA 18902"
# # clinic_address = geolocator.geocode((clinic_location))
# # clinic_gps = (clinic_address.longitude, clinic_address.latitude)

# # pprint(clinic_address.raw["lat"])
# # print(find_distance(clinic_location))


# response = requests.get(URL[0] + STATE + URL[1])
# # json_ = json.loads(response.text)

# datetime_ = datetime.now()
# json_ = response.json()
# locations = json_["features"]
# errors = []


# # def write_json(filename):
# #     with open("locations.json", "w") as locations_json:
# #         locations_json.write(json.dumps(filename))


# # pprint(locations)
# # print(locations[0]["properties"])
# # errors = []
# while True:
#     for location in locations:
#         props = location["properties"]
#         street_address = props["address"]
#         if props["appointments_available"]:
#             if not isinstance(street_address, str):
#                 # errors.append(props)

#                 # write_json(errors)
#                 #         if (
#                 #             None
#                 #             in [street_address, props["city"], props["postal_code"]]
#                 #             # and props["address"]
#                 #         ):
#                 #             # print(["\n", props["address"], props["city"], props["postal_code"], "\n"])
#                 address = f"{props['city']}, {props['state']}"
#                 # print(address, "\n", props, "\n\n")
#             else:
#                 address = f"{street_address} {props['city']}, {props['state']} {props['postal_code']}"
#             try:
#                 # print(find_distance(address))
#                 # print(type(find_distance(address)))
#                 distance_ = find_distance(address)
#                 if distance_ < MAX_DISTANCE:
#                     # pprint(props)
#                     # if props["address"] is None or props["address"] == "None":
#                     print(
#                         f"""
#                         {props["name"]}
#                         {props["address"]}
#                         {props["city"]}, PA {props["postal_code"]}
#                         {props["url"]}
#                         {props["appointments_last_fetched"]}
#                         """
#                     )
#             except AttributeError as e:
#                 # errors.append(
#                 #     [
#                 #         f"{props['address']} {props['city']}, PA {props['postal_code']}",
#                 #         props,
#                 #     ]
#                 # )
#                 print("Error on:", e)
#                 print(address)
#                 print(props, "\n")

#     sleep(600)
# #         # pprint(props["address"])
# # #         # print("\n")
# # #         # pprint(props)
# # #         # print("\n\n")
# # #         # else:
# # #     print(f"{props['address']}", props["appointments_available"], "\n")
# # # # json_[:10]

# # # # pprint(json_)
# # print("Errors")
# # for error in errors:
# #     print(error[0], "\n", error[1], "\n")
