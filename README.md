# Vaccine Finder

A Python script to query [VaccineSpotter]("https://www.vaccinespotter.org/")'s API to find local clinics with available vaccine appointments.

- Install requirements.txt `python3 -m pip install -r requirements.txt`
- Change the ALL_CAPS variables at the top of vaccine.py to suit your search preferences.
- Rename `configEXAMPLE.py` to `config.py`. If you enter your SEARCH_ADDRESS as a GPS tuple, i.e. (39.414036, -97.047080) you won't need to enter a Google Maps API Key. You can try using a plain text address but if it's not known to OpenStreetMap you'll need to sign up for a [Google Maps]("https://console.cloud.google.com") API Key to translate more rural addresses to GPS lat/ long.

Run from the terminal using:

`python3 vaccine.py`

_A warning that Rite-Aid's appointments availability status seems to be a bit flaky._
