# Vaccine Finder

A Python script to query [VaccineSpotter]("https://www.vaccinespotter.org/")'s API to find local clinics with available vaccine appointments. You will need to sign up for a [Google Maps]("https://console.cloud.google.com") API token to geolocate the text addresses.

1. Rename `configEXAMPLE.py` to `config.py` and enter your Google Maps API Key for geolocation.
2. Change the ALL_CAPS variables at the top of vaccine.py to suit your search preferences.
3. Install requirements.txt `python3 -m pip install -r requirements.txt`
   Run from the terminal using:

`python3 vaccine.py`

_A warning that Rite-Aid's appointments availability status seems to be a bit flaky._
