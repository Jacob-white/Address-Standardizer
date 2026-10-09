"""
Build an evaluation corpus from OpenStreetMap (Overpass API).
=============================================================
Ground truth comes from the structured OSM ``addr:*`` tags of real mapped addresses, NOT from this engine.
The messy "renderings" are produced by seeded, deterministic string transformations that never call the
engine. See docs/evaluation.md for methodology and limits.

Data (c) OpenStreetMap contributors, available under the Open Database License (ODbL) 1.0.
See benchmarks/eval/DATA_LICENSE.md.

Usage (needs network; be polite, the defaults are conservative):

    PYTHONPATH=. python benchmarks/eval/build_osm_corpus.py --out benchmarks/eval/osm_sample.json \
        --per-country 22 --seed 20261009

Raw Overpass responses are cached under --cache-dir (default benchmarks/eval/.cache, git-ignored), so a
rebuild from the cache is offline and byte-for-byte reproducible.
"""

import argparse
import hashlib
import json
import os
import random
import sys
import time
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from typing import Any, Callable, Dict, List, Optional, Tuple

HERE = os.path.dirname(os.path.abspath(__file__))
USER_AGENT = (
    "address-standardizer-eval/0.1 (+https://github.com/Jacob-white/Address-Standardizer; "
    "evaluation corpus builder; contact via repo issues)"
)
ENDPOINTS = [
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
]
HOLDOUT_SEED = 20261201
HOLDOUT_V2_SEED = 20270115
FIELDS = ("house_number", "street", "city", "state", "postcode", "country")

# Per-country configuration. bboxes are (south, west, north, east). ``street1`` is how the street line is
# written locally; ``segments`` is the local order of an address line (empty segments are dropped).
COUNTRIES: Dict[str, Dict[str, Any]] = {
    "US": {"iso3": "USA", "name": "United States", "script": "Latin", "lang": "en",
           "bboxes": [(42.30, -71.15, 42.40, -71.00), (37.74, -122.45, 37.80, -122.39)],
           "holdout_bboxes": [(41.89,-87.66,41.93,-87.62), (30.25,-97.76,30.29,-97.72), (39.72,-105.00,39.76,-104.96)],
           "street1": "{hn} {street}", "segments": ["{street1}", "{city}", "{state} {pc}"]},
    "CA": {"iso3": "CAN", "name": "Canada", "script": "Latin", "lang": "en", "state_keys": ["addr:province", "addr:state"],
           "bboxes": [(43.64, -79.42, 43.68, -79.36), (45.40, -75.72, 45.43, -75.67)],
           "holdout_bboxes": [(49.26,-123.14,49.29,-123.09), (45.50,-73.60,45.53,-73.55)],
           "street1": "{hn} {street}", "segments": ["{street1}", "{city}", "{state} {pc}"]},
    "GB": {"iso3": "GBR", "name": "United Kingdom", "script": "Latin", "lang": "en",
           "bboxes": [(51.49, -0.15, 51.54, -0.07), (53.46, -2.27, 53.50, -2.20)],
           "holdout_bboxes": [(52.47,-1.92,52.50,-1.88), (55.94,-3.21,55.96,-3.17), (51.44,-2.62,51.47,-2.57)],
           "street1": "{hn} {street}", "segments": ["{street1}", "{city}", "{pc}"]},
    "IE": {"iso3": "IRL", "name": "Ireland", "script": "Latin", "lang": "en",
           "bboxes": [(53.33, -6.30, 53.36, -6.23)],
           "holdout_bboxes": [(51.89,-8.50,51.91,-8.45), (53.26,-9.07,53.28,-9.03)],
           "street1": "{hn} {street}", "segments": ["{street1}", "{city}", "{pc}"]},
    "AU": {"iso3": "AUS", "name": "Australia", "script": "Latin", "lang": "en", "city_keys": ["addr:city", "addr:suburb"],
           "bboxes": [(-33.90, 151.17, -33.85, 151.23), (-37.84, 144.94, -37.79, 145.00)],
           "holdout_bboxes": [(-33.83,151.00,-33.80,151.04), (-37.83,145.02,-37.80,145.06), (-27.49,153.00,-27.45,153.04), (-34.94,138.58,-34.91,138.62)],
           "street1": "{hn} {street}", "segments": ["{street1}", "{city}", "{state} {pc}"]},
    "NZ": {"iso3": "NZL", "name": "New Zealand", "script": "Latin", "lang": "en",
           "bboxes": [(-36.88, 174.74, -36.83, 174.80)],
           "holdout_bboxes": [(-41.30,174.76,-41.27,174.79), (-43.54,172.62,-43.51,172.66)],
           "street1": "{hn} {street}", "segments": ["{street1}", "{city}", "{pc}"]},
    "DE": {"iso3": "DEU", "name": "Germany", "script": "Latin", "lang": "de",
           "bboxes": [(52.49, 13.35, 52.55, 13.45), (48.12, 11.53, 48.17, 11.60)],
           "holdout_bboxes": [(53.54,9.96,53.57,10.01), (50.92,6.93,50.95,6.97), (50.10,8.66,50.13,8.70)],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
    "AT": {"iso3": "AUT", "name": "Austria", "script": "Latin", "lang": "de",
           "bboxes": [(48.19, 16.34, 48.23, 16.40)],
           "holdout_bboxes": [(47.06,15.42,47.09,15.46), (47.79,13.03,47.82,13.06)],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
    "CH": {"iso3": "CHE", "name": "Switzerland", "script": "Latin", "lang": "de",
           "bboxes": [(47.36, 8.52, 47.40, 8.57)],
           "holdout_bboxes": [(46.94,7.43,46.96,7.46), (46.19,6.13,46.22,6.16)],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
    "FR": {"iso3": "FRA", "name": "France", "script": "Latin", "lang": "fr",
           "bboxes": [(48.84, 2.30, 48.88, 2.38), (45.74, 4.82, 45.78, 4.88)],
           "holdout_bboxes": [(43.28,5.36,43.31,5.40), (43.59,1.43,43.62,1.46), (44.83,-0.59,44.86,-0.56)],
           "street1": "{hn} {street}", "segments": ["{street1}", "{pc} {city}"]},
    "ES": {"iso3": "ESP", "name": "Spain", "script": "Latin", "lang": "es",
           "bboxes": [(40.40, -3.72, 40.44, -3.66), (41.37, 2.15, 41.42, 2.20)],
           "holdout_bboxes": [(37.38,-6.01,37.41,-5.97), (39.46,-0.39,39.49,-0.35)],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
    "IT": {"iso3": "ITA", "name": "Italy", "script": "Latin", "lang": "it",
           "bboxes": [(41.88, 12.46, 41.92, 12.52), (44.48, 11.32, 44.52, 11.37)],
           "holdout_bboxes": [(45.45,9.17,45.48,9.21), (40.83,14.24,40.86,14.28), (45.06,7.66,45.09,7.70)],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
    "PT": {"iso3": "PRT", "name": "Portugal", "script": "Latin", "lang": "pt",
           "bboxes": [(38.70, -9.16, 38.74, -9.12)],
           "holdout_bboxes": [(41.14,-8.63,41.17,-8.59)],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
    "NL": {"iso3": "NLD", "name": "Netherlands", "script": "Latin", "lang": "nl",
           "bboxes": [(52.35, 4.87, 52.39, 4.94), (51.90, 4.45, 51.94, 4.51)],
           "holdout_bboxes": [(52.08,5.10,52.11,5.14), (52.07,4.29,52.10,4.33)],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
    "BE": {"iso3": "BEL", "name": "Belgium", "script": "Latin", "lang": "nl",
           "bboxes": [(50.83, 4.33, 50.87, 4.39)],
           "holdout_bboxes": [(51.20,4.39,51.23,4.43), (51.04,3.71,51.07,3.75)],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
    "PL": {"iso3": "POL", "name": "Poland", "script": "Latin", "lang": "pl",
           "bboxes": [(52.21, 20.97, 52.25, 21.04)],
           "holdout_bboxes": [(50.05,19.92,50.08,19.96), (51.10,17.02,51.12,17.06)],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
    "SE": {"iso3": "SWE", "name": "Sweden", "script": "Latin", "lang": "sv",
           "bboxes": [(59.31, 18.04, 59.35, 18.10)],
           "holdout_bboxes": [(57.69,11.95,57.72,11.99), (55.59,12.99,55.62,13.02)],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
    "DK": {"iso3": "DNK", "name": "Denmark", "script": "Latin", "lang": "da",
           "bboxes": [(55.66, 12.55, 55.70, 12.61)],
           "holdout_bboxes": [(56.14,10.19,56.17,10.23), (55.39,10.37,55.41,10.41)],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
    "BR": {"iso3": "BRA", "name": "Brazil", "script": "Latin", "lang": "pt",
           "bboxes": [(-23.58, -46.68, -23.54, -46.63)],
           "holdout_bboxes": [(-22.98,-43.22,-22.95,-43.18), (-25.45,-49.29,-25.42,-49.25)],
           "street1": "{street}, {hn}", "segments": ["{street1}", "{city} - {state}", "{pc}"]},
    "RU": {"iso3": "RUS", "name": "Russia", "script": "Cyrillic", "lang": "ru",
           "bboxes": [(55.73, 37.58, 55.78, 37.66), (59.91, 30.28, 59.96, 30.36)],
           "holdout_bboxes": [(55.77,49.10,55.81,49.14), (55.01,82.91,55.05,82.96)],
           "street1": "{street}, {hn}", "segments": ["{pc}", "{city}", "{street1}"]},
    "UA": {"iso3": "UKR", "name": "Ukraine", "script": "Cyrillic", "lang": "uk",
           "bboxes": [(50.43, 30.50, 50.47, 30.56)],
           "holdout_bboxes": [(49.83,24.00,49.86,24.04), (49.98,36.22,50.01,36.26)],
           "street1": "{street}, {hn}", "segments": ["{pc}", "{city}", "{street1}"]},
    "GR": {"iso3": "GRC", "name": "Greece", "script": "Greek", "lang": "el",
           "bboxes": [(37.96, 23.71, 38.00, 23.76), (40.61, 22.93, 40.65, 22.97)],
           "holdout_bboxes": [(38.23,21.72,38.26,21.76), (35.33,25.12,35.35,25.15)],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
    "IL": {"iso3": "ISR", "name": "Israel", "script": "Hebrew", "lang": "he",
           "bboxes": [(32.05, 34.76, 32.10, 34.80), (31.76, 35.19, 31.80, 35.23)],
           "holdout_bboxes": [(32.79,34.98,32.83,35.02), (31.24,34.78,31.27,34.81)],
           "street1": "{street} {hn}", "segments": ["{street1}", "{city}", "{pc}"]},
    "TH": {"iso3": "THA", "name": "Thailand", "script": "Thai", "lang": "th",
           "bboxes": [(13.72, 100.50, 13.78, 100.58), (18.77, 98.96, 18.81, 99.01)],
           "holdout_bboxes": [(7.87,98.38,7.90,98.41), (12.92,100.87,12.95,100.90)],
           "street1": "{hn} {street}", "segments": ["{street1}", "{city} {pc}"]},
    "JP": {"iso3": "JPN", "name": "Japan", "script": "Japanese", "lang": "ja", "sep": " ",
           "bboxes": [(35.65, 139.69, 35.70, 139.78), (34.66, 135.48, 34.71, 135.53)],
           "holdout_bboxes": [(35.15,136.89,35.19,136.93), (43.05,141.33,43.08,141.37), (33.58,130.39,33.61,130.43)],
           "street1": "{street}{hn}", "segments": ["{pc}", "{city}", "{street1}"]},
    "KR": {"iso3": "KOR", "name": "South Korea", "script": "Hangul", "lang": "ko", "sep": " ",
           "bboxes": [(37.50, 127.00, 37.56, 127.08), (35.14, 129.03, 35.18, 129.09)],
           "holdout_bboxes": [(37.44,126.69,37.47,126.73), (35.86,128.58,35.89,128.62)],
           "street1": "{street} {hn}", "segments": ["{city}", "{street1}", "{pc}"]},
    "TW": {"iso3": "TWN", "name": "Taiwan", "script": "Han", "lang": "zh", "sep": " ",
           "bboxes": [(25.02, 121.50, 25.06, 121.56)],
           "holdout_bboxes": [(24.13,120.66,24.16,120.70), (22.61,120.29,22.64,120.33)],
           "street1": "{street}{hn}", "segments": ["{pc}", "{city}", "{street1}"]},
    # ---- held-out only countries (no development bboxes; used by --holdout) ----
    "MX": {"iso3": "MEX", "name": "Mexico", "script": "Latin", "lang": "es", "bboxes": [],
           "holdout_bboxes": [(19.40, -99.18, 19.44, -99.14), (20.65, -103.38, 20.69, -103.34)],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
    "AR": {"iso3": "ARG", "name": "Argentina", "script": "Latin", "lang": "es", "bboxes": [],
           "holdout_bboxes": [(-34.62, -58.45, -34.59, -58.41), (-31.43, -64.20, -31.40, -64.17)],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
    "CL": {"iso3": "CHL", "name": "Chile", "script": "Latin", "lang": "es", "bboxes": [],
           "holdout_bboxes": [(-33.46, -70.67, -33.43, -70.63), (-33.05, -71.63, -33.02, -71.60)],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
    "IN": {"iso3": "IND", "name": "India", "script": "Latin", "lang": "en", "bboxes": [],
           "holdout_bboxes": [(28.62, 77.19, 28.65, 77.23), (19.05, 72.82, 19.09, 72.87), (12.96, 77.58, 13.00, 77.62)],
           "street1": "{hn} {street}", "segments": ["{street1}", "{city} {pc}"]},
    "ZA": {"iso3": "ZAF", "name": "South Africa", "script": "Latin", "lang": "en", "bboxes": [],
           "holdout_bboxes": [(-33.94, 18.40, -33.91, 18.44), (-26.22, 28.02, -26.18, 28.06)],
           "street1": "{hn} {street}", "segments": ["{street1}", "{city}", "{pc}"]},
    "SG": {"iso3": "SGP", "name": "Singapore", "script": "Latin", "lang": "en", "bboxes": [],
           "holdout_bboxes": [(1.28, 103.83, 1.32, 103.87), (1.33, 103.72, 1.37, 103.76)],
           "street1": "{hn} {street}", "segments": ["{street1}", "{city} {pc}"]},
    "HK": {"iso3": "HKG", "name": "Hong Kong", "script": "Latin", "lang": "en", "bboxes": [],
           "holdout_bboxes": [(22.27, 114.15, 22.30, 114.19)],
           "street1": "{hn} {street}", "segments": ["{street1}", "{city}"]},
    "SA": {"iso3": "SAU", "name": "Saudi Arabia", "script": "Arabic", "lang": "ar", "bboxes": [],
           "holdout_bboxes": [(24.62, 46.69, 24.66, 46.73), (21.50, 39.15, 21.54, 39.20)],
           "street1": "{hn} {street}", "segments": ["{street1}", "{city} {pc}"]},
    "EG": {"iso3": "EGY", "name": "Egypt", "script": "Arabic", "lang": "ar", "bboxes": [],
           "holdout_bboxes": [(30.03, 31.22, 30.07, 31.26), (31.19, 29.89, 31.23, 29.93)],
           "street1": "{hn} {street}", "segments": ["{street1}", "{city}", "{pc}"]},
    "TR": {"iso3": "TUR", "name": "Turkey", "script": "Latin", "lang": "tr", "bboxes": [],
           "holdout_bboxes": [(41.02, 28.97, 41.06, 29.01), (39.91, 32.84, 39.94, 32.88), (38.41, 27.12, 38.44, 27.16)],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
    "NO": {"iso3": "NOR", "name": "Norway", "script": "Latin", "lang": "no", "bboxes": [],
           "holdout_bboxes": [(59.91, 10.73, 59.94, 10.77), (60.38, 5.31, 60.41, 5.35)],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
    "FI": {"iso3": "FIN", "name": "Finland", "script": "Latin", "lang": "fi", "bboxes": [],
           "holdout_bboxes": [(60.16, 24.92, 60.19, 24.96), (61.48, 23.75, 61.51, 23.79)],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
    "CZ": {"iso3": "CZE", "name": "Czechia", "script": "Latin", "lang": "cs", "bboxes": [],
           "holdout_bboxes": [(50.07, 14.40, 50.10, 14.44), (49.18, 16.59, 49.21, 16.63)],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
    "HU": {"iso3": "HUN", "name": "Hungary", "script": "Latin", "lang": "hu", "bboxes": [],
           "holdout_bboxes": [(47.48, 19.04, 47.51, 19.08), (47.52, 21.60, 47.55, 21.64)],
           "street1": "{street} {hn}", "segments": ["{pc} {city}", "{street1}"]},
    "RO": {"iso3": "ROU", "name": "Romania", "script": "Latin", "lang": "ro", "bboxes": [],
           "holdout_bboxes": [(44.42, 26.08, 44.45, 26.12), (46.75, 23.57, 46.78, 23.61)],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
    # ---- countries that appear only in the sealed v2 holdout (--holdout-v2) ----
    "ID": {"iso3": "IDN", "name": "Indonesia", "script": "Latin", "lang": "id", "bboxes": [],
           "street1": "{street} {hn}", "segments": ["{street1}", "{city} {pc}"]},
    "MY": {"iso3": "MYS", "name": "Malaysia", "script": "Latin", "lang": "ms", "bboxes": [],
           "street1": "{hn} {street}", "segments": ["{street1}", "{pc} {city}"]},
    "PH": {"iso3": "PHL", "name": "Philippines", "script": "Latin", "lang": "en", "bboxes": [],
           "street1": "{hn} {street}", "segments": ["{street1}", "{city} {pc}"]},
    "VN": {"iso3": "VNM", "name": "Vietnam", "script": "Latin", "lang": "vi", "bboxes": [],
           "street1": "{hn} {street}", "segments": ["{street1}", "{city}", "{pc}"]},
    "KE": {"iso3": "KEN", "name": "Kenya", "script": "Latin", "lang": "en", "bboxes": [],
           "street1": "{hn} {street}", "segments": ["{street1}", "{city} {pc}"]},
    "NG": {"iso3": "NGA", "name": "Nigeria", "script": "Latin", "lang": "en", "bboxes": [],
           "street1": "{hn} {street}", "segments": ["{street1}", "{city} {pc}"]},
    "UY": {"iso3": "URY", "name": "Uruguay", "script": "Latin", "lang": "es", "bboxes": [],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
    "CO": {"iso3": "COL", "name": "Colombia", "script": "Latin", "lang": "es", "bboxes": [],
           "street1": "{street} {hn}", "segments": ["{street1}", "{city}", "{pc}"]},
    "PE": {"iso3": "PER", "name": "Peru", "script": "Latin", "lang": "es", "bboxes": [],
           "street1": "{street} {hn}", "segments": ["{street1}", "{city} {pc}"]},
    "EC": {"iso3": "ECU", "name": "Ecuador", "script": "Latin", "lang": "es", "bboxes": [],
           "street1": "{street} {hn}", "segments": ["{street1}", "{pc} {city}"]},
}

# Sealed v2 holdout areas (--holdout-v2): disjoint from every ``bboxes`` and ``holdout_bboxes`` entry above (a test
# enforces it). Reserved for MEASUREMENT only: do not diagnose, tune or fix against records from these areas.
HOLDOUT_V2_BBOXES: Dict[str, List[Tuple[float, float, float, float]]] = {
    "US": [(47.60, -122.34, 47.63, -122.30), (39.93, -75.18, 39.96, -75.14), (33.76, -84.40, 33.79, -84.36),
           (45.51, -122.68, 45.54, -122.64)],
    "CA": [(51.03, -114.10, 51.06, -114.06), (44.64, -63.60, 44.67, -63.56), (46.80, -71.23, 46.83, -71.19)],
    "GB": [(53.79, -1.56, 53.81, -1.52), (55.85, -4.28, 55.88, -4.24), (51.47, -3.19, 51.50, -3.15),
           (54.96, -1.63, 54.99, -1.59)],
    "IE": [(52.65, -8.64, 52.68, -8.60), (52.25, -7.13, 52.27, -7.09)],
    "AU": [(-31.97, 115.84, -31.94, 115.88), (-35.30, 149.11, -35.27, 149.15), (-42.89, 147.31, -42.86, 147.35),
           (-32.94, 151.74, -32.91, 151.78)],
    "NZ": [(-37.80, 175.26, -37.77, 175.30), (-45.88, 170.49, -45.85, 170.53)],
    "DE": [(48.77, 9.16, 48.80, 9.20), (51.33, 12.36, 51.36, 12.40), (51.21, 6.77, 51.24, 6.81)],
    "AT": [(47.25, 11.38, 47.28, 11.42), (48.29, 14.27, 48.32, 14.31)],
    "CH": [(47.55, 7.58, 47.57, 7.62), (46.51, 6.62, 46.54, 6.65), (47.04, 8.29, 47.06, 8.32)],
    "FR": [(47.20, -1.57, 47.23, -1.53), (48.57, 7.74, 48.60, 7.78), (50.62, 3.05, 50.65, 3.09)],
    "ES": [(43.25, -2.94, 43.28, -2.90), (41.64, -0.91, 41.67, -0.87), (36.71, -4.44, 36.74, -4.40)],
    "IT": [(43.76, 11.24, 43.79, 11.28), (38.11, 13.35, 38.14, 13.39), (44.40, 8.92, 44.43, 8.96)],
    "PT": [(40.20, -8.44, 40.22, -8.40), (41.54, -8.44, 41.56, -8.40)],
    "NL": [(53.20, 6.55, 53.23, 6.59), (51.43, 5.46, 51.46, 5.50), (50.84, 5.68, 50.86, 5.72)],
    "BE": [(50.63, 5.56, 50.66, 5.60), (50.87, 4.69, 50.89, 4.72)],
    "PL": [(54.34, 18.63, 54.37, 18.67), (52.40, 16.91, 52.43, 16.95), (51.76, 19.44, 51.79, 19.48)],
    "SE": [(59.85, 17.62, 59.87, 17.66), (58.40, 15.60, 58.43, 15.64)],
    "DK": [(57.03, 9.91, 57.06, 9.95), (55.47, 8.44, 55.49, 8.48)],
    "BR": [(-19.94, -43.96, -19.91, -43.92), (-30.05, -51.24, -30.02, -51.20), (-12.99, -38.50, -12.96, -38.46)],
    "RU": [(56.82, 60.59, 56.85, 60.63), (56.31, 43.98, 56.34, 44.02), (53.19, 50.09, 53.22, 50.13)],
    "UA": [(46.47, 30.72, 46.49, 30.76), (48.45, 35.03, 48.47, 35.07), (47.83, 35.14, 47.86, 35.18), (49.22, 28.46, 49.25, 28.50)],
    "GR": [(39.62, 22.40, 39.65, 22.43), (39.35, 22.93, 39.38, 22.96), (39.65, 20.84, 39.68, 20.87)],
    "IL": [(32.31, 34.84, 32.34, 34.87), (31.96, 34.79, 31.99, 34.82), (31.78, 34.63, 31.81, 34.66), (32.08, 34.87, 32.10, 34.90), (32.00, 34.76, 32.03, 34.79)],
    "TH": [(16.42, 102.82, 16.45, 102.85), (7.00, 100.46, 7.02, 100.49), (19.89, 99.82, 19.92, 99.85)],
    "JP": [(35.44, 139.62, 35.47, 139.66), (34.98, 135.75, 35.01, 135.79), (34.38, 132.45, 34.41, 132.49),
           (38.25, 140.86, 38.28, 140.90), (34.68, 135.17, 34.71, 135.21), (26.20, 127.67, 26.23, 127.71)],
    "KR": [(36.34, 127.38, 36.37, 127.42), (35.14, 126.90, 35.17, 126.94), (37.26, 127.01, 37.29, 127.04)],
    "TW": [(22.98, 120.19, 23.01, 120.23), (24.79, 120.96, 24.82, 121.00), (24.98, 121.29, 25.01, 121.33)],
    "MX": [(25.66, -100.33, 25.69, -100.29), (19.03, -98.22, 19.06, -98.18), (20.96, -89.63, 20.99, -89.59)],
    "AR": [(-32.96, -60.66, -32.93, -60.62), (-32.91, -68.86, -32.88, -68.82)],
    "CL": [(-36.84, -73.07, -36.81, -73.03), (-38.74, -72.61, -38.72, -72.57)],
    "IN": [(13.04, 80.23, 13.07, 80.27), (22.55, 88.34, 22.58, 88.38), (18.51, 73.84, 18.54, 73.88),
           (17.41, 78.45, 17.44, 78.49)],
    "ZA": [(-25.76, 28.18, -25.73, 28.22), (-29.87, 31.00, -29.84, 31.04), (-33.94, 18.84, -33.92, 18.88)],
    "SG": [(1.29, 103.78, 1.32, 103.82), (1.35, 103.93, 1.38, 103.97), (1.30, 103.88, 1.33, 103.92),
           (1.42, 103.82, 1.45, 103.86)],
    "HK": [(22.31, 114.16, 22.34, 114.19), (22.38, 114.18, 22.40, 114.21), (22.36, 114.11, 22.38, 114.13), (22.28, 114.20, 22.30, 114.23), (22.44, 114.16, 22.46, 114.18)],
    "SA": [(26.41, 50.08, 26.44, 50.12), (24.46, 39.60, 24.49, 39.64), (21.40, 39.81, 21.43, 39.85), (28.37, 36.55, 28.40, 36.59), (26.27, 50.19, 26.30, 50.23)],
    "EG": [(29.99, 31.18, 30.02, 31.21), (30.08, 31.31, 30.11, 31.35), (31.03, 31.37, 31.06, 31.40), (30.77, 31.00, 30.80, 31.03), (30.04, 31.38, 30.07, 31.42)],
    "TR": [(40.17, 29.04, 40.20, 29.08), (36.88, 30.69, 36.91, 30.73), (36.98, 35.31, 37.01, 35.35)],
    "NO": [(63.42, 10.38, 63.44, 10.42), (58.96, 5.72, 58.98, 5.76), (69.64, 18.94, 69.67, 18.98)],
    "FI": [(60.44, 22.25, 60.46, 22.29), (65.00, 25.46, 65.03, 25.50), (60.20, 24.65, 60.22, 24.69)],
    "CZ": [(49.73, 13.36, 49.76, 13.40), (49.82, 18.25, 49.85, 18.29), (49.58, 17.24, 49.60, 17.28)],
    "HU": [(46.24, 20.14, 46.27, 20.18), (46.06, 18.21, 46.09, 18.25), (47.67, 17.62, 47.70, 17.66)],
    "RO": [(45.74, 21.21, 45.77, 21.25), (47.15, 27.57, 47.18, 27.61), (45.64, 25.58, 45.67, 25.62)],
    "ID": [(-6.24, 106.80, -6.21, 106.84), (-6.93, 107.60, -6.90, 107.64), (-7.28, 112.72, -7.25, 112.76)],
    "MY": [(3.13, 101.68, 3.16, 101.72), (5.40, 100.30, 5.43, 100.34), (1.46, 103.74, 1.49, 103.78)],
    "PH": [(14.55, 121.00, 14.58, 121.04), (10.30, 123.88, 10.33, 123.92), (7.06, 125.59, 7.09, 125.63)],
    "VN": [(21.01, 105.83, 21.04, 105.87), (10.77, 106.68, 10.80, 106.72), (16.05, 108.20, 16.08, 108.23)],
    "KE": [(-1.30, 36.80, -1.27, 36.84), (-4.07, 39.65, -4.04, 39.69), (-0.11, 34.74, -0.08, 34.78), (-0.30, 36.06, -0.27, 36.10)],
    "NG": [(6.43, 3.40, 6.46, 3.44), (9.05, 7.47, 9.08, 7.51), (7.37, 3.89, 7.40, 3.93), (4.80, 7.00, 4.83, 7.04)],
    "UY": [(-34.92, -56.18, -34.89, -56.14), (-34.91, -54.97, -34.89, -54.94)],
    "CO": [(4.64, -74.08, 4.67, -74.04), (6.23, -75.59, 6.26, -75.55), (3.43, -76.54, 3.46, -76.50)],
    "PE": [(-12.12, -77.05, -12.09, -77.01), (-16.41, -71.55, -16.38, -71.51)],
    "EC": [(-0.20, -78.50, -0.17, -78.46), (-2.19, -79.90, -2.16, -79.86), (-2.91, -79.02, -2.88, -78.98), (-1.26, -78.64, -1.23, -78.60)],
}
for _iso2, _boxes in HOLDOUT_V2_BBOXES.items():
    COUNTRIES.setdefault(_iso2, {})["holdout_v2_bboxes"] = _boxes

# Abbreviation tables per language, used ONLY to make messy renderings (independent of the engine).
ABBREVIATIONS: Dict[str, List[Tuple[str, str]]] = {
    "en": [("Street", "St"), ("Avenue", "Ave"), ("Road", "Rd"), ("Boulevard", "Blvd"), ("Drive", "Dr"),
           ("Lane", "Ln"), ("Court", "Ct"), ("Place", "Pl"), ("Terrace", "Ter"), ("Highway", "Hwy"),
           ("North", "N"), ("South", "S"), ("East", "E"), ("West", "W")],
    "de": [("straße", "str."), ("Straße", "Str."), ("strasse", "str."), ("Strasse", "Str."), ("Platz", "Pl.")],
    "fr": [("Avenue", "Av."), ("Boulevard", "Bd"), ("Place", "Pl."), ("Chemin", "Ch."), ("Impasse", "Imp.")],
    "es": [("Calle", "C/"), ("Avenida", "Avda."), ("Plaza", "Pza."), ("Paseo", "Pº")],
    "it": [("Via", "V."), ("Piazza", "P.za"), ("Viale", "V.le"), ("Corso", "C.so")],
    "pt": [("Rua", "R."), ("Avenida", "Av."), ("Travessa", "Tv."), ("Praça", "Pç.")],
    "nl": [("straat", "str."), ("Straat", "Str."), ("laan", "ln."), ("Laan", "Ln.")],
    "pl": [("ulica", "ul."), ("Aleja", "Al."), ("plac", "pl.")],
    "ru": [("улица", "ул."), ("проспект", "пр-т"), ("переулок", "пер."), ("бульвар", "бул.")],
    "uk": [("вулиця", "вул."), ("проспект", "просп."), ("провулок", "пров.")],
}

STYLES = (
    "structured", "structured_swapped", "line", "line_country_text", "line_nocomma", "line_upper",
    "line_lower", "line_abbrev", "line_no_postal", "line_swapped", "line_messy",
)
# Fields the style deliberately withholds from the input (so they are not scored against the engine).
UNSCORED = {"line_no_postal": ["postcode"]}


class OverpassError(RuntimeError):
    """Raised when every endpoint/retry failed."""


def build_query(bbox: Tuple[float, float, float, float], city_key: str, limit: int, timeout: int = 90) -> str:
    s, w, n, e = bbox
    box = f"({s},{w},{n},{e})"
    flt = f'["addr:housenumber"]["addr:street"]["addr:postcode"]["{city_key}"]'
    return f"[out:json][timeout:{timeout}];nwr{flt}{box};out center {limit};"


def fetch_overpass(
    query: str,
    cache_dir: str,
    endpoints: Optional[List[str]] = None,
    user_agent: str = USER_AGENT,
    delay: float = 5.0,
    retries: int = 3,
    offline: bool = False,
    sleep: Callable[[float], None] = time.sleep,
    opener: Callable[..., Any] = urllib.request.urlopen,
) -> Dict[str, Any]:
    """POST an Overpass query with disk caching, polite delays and retries/backoff across endpoints."""
    os.makedirs(cache_dir, exist_ok=True)
    key = hashlib.sha256(query.encode("utf-8")).hexdigest()[:20]
    path = os.path.join(cache_dir, f"{key}.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    if offline:
        raise OverpassError(f"offline mode and no cached response for query {query!r}")
    body = urllib.parse.urlencode({"data": query}).encode("utf-8")
    last_err: Optional[BaseException] = None
    for attempt in range(retries):
        for endpoint in endpoints or ENDPOINTS:
            req = urllib.request.Request(
                endpoint, data=body, headers={"User-Agent": user_agent, "Accept": "application/json"}
            )
            try:
                with opener(req, timeout=150) as resp:
                    payload = json.loads(resp.read().decode("utf-8"))
            except (urllib.error.URLError, OSError, ValueError) as exc:
                last_err = exc
                continue
            with open(path, "w", encoding="utf-8") as fh:
                json.dump(payload, fh, ensure_ascii=False)
            sleep(delay)
            return payload
        sleep(delay * (2 ** attempt) + 1)
    raise OverpassError(f"all Overpass endpoints failed after {retries} rounds: {last_err}")


# ----------------------------------------------------------------------------- OSM element -> labels


def _clean(value: Any) -> str:
    return " ".join(str(value or "").split())


def element_to_labels(el: Dict[str, Any], cfg: Dict[str, Any], city_key: str) -> Optional[Dict[str, str]]:
    """Return ground-truth labels for an Overpass element, or None if it is not a clean single address."""
    tags = el.get("tags") or {}
    hn = _clean(tags.get("addr:housenumber"))
    street = _clean(tags.get("addr:street"))
    city = _clean(tags.get(city_key))
    pc = _clean(tags.get("addr:postcode"))
    state = ""
    for k in cfg.get("state_keys", ["addr:state"]):
        state = state or _clean(tags.get(k))
    if not (hn and street and city and pc):
        return None
    if any(ch in hn + pc + street for ch in ";,"):
        return None
    if len(street) > 70 or len(hn) > 12 or len(city) > 50:
        return None
    return {
        "house_number": hn, "street": street, "city": city, "state": state, "postcode": pc,
        "country": cfg["iso3"],
    }


def parse_elements(payload: Dict[str, Any], iso2: str, cfg: Dict[str, Any], city_key: str) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    seen = set()
    for el in payload.get("elements", []):
        labels = element_to_labels(el, cfg, city_key)
        if labels is None:
            continue
        ident = (labels["street"], labels["house_number"], labels["city"], labels["postcode"])
        if ident in seen:
            continue
        seen.add(ident)
        out.append({
            "id": f"{iso2}-{el.get('type', 'x')[0]}{el.get('id', 0)}",
            "country": iso2,
            "script": cfg["script"],
            "source": f"osm:{el.get('type')}/{el.get('id')}",
            "labels": labels,
        })
    return out


# ----------------------------------------------------------------------------- renderings (engine-free)


def _street1(labels: Dict[str, str], cfg: Dict[str, Any]) -> str:
    return cfg["street1"].format(hn=labels["house_number"], street=labels["street"]).strip()


def _segments(labels: Dict[str, str], cfg: Dict[str, Any], with_pc: bool = True, swap: bool = False,
              country_text: Optional[str] = None) -> List[str]:
    city, state = labels["city"], labels["state"]
    if swap:
        city, state = state, city
    values = {"street1": _street1(labels, cfg), "city": city, "state": state,
              "pc": labels["postcode"] if with_pc else ""}
    segs = [" ".join(seg.format(**values).split()).strip(" -") for seg in cfg["segments"]]
    segs = [s for s in segs if s and s.strip("-,")]
    if country_text:
        segs.append(country_text)
    return segs


def _abbreviate(text: str, lang: str) -> str:
    for long, short in ABBREVIATIONS.get(lang, []):
        # whole-word for words, suffix-style for compounds such as "Hauptstraße"
        if long[0].islower():
            text = text.replace(long, short)
        else:
            text = text.replace(long + " ", short + " ").replace(long + ",", short + ",")
            if text.endswith(long):
                text = text[: -len(long)] + short
    return text


def _messy(text: str, rng: random.Random) -> str:
    words = text.split(" ")
    out = []
    for w in words:
        out.append(w)
        out.append(rng.choice([" ", " ", "  ", " ", " \t"]))
    text = "".join(out).strip()
    text = unicodedata.normalize("NFD", text) if rng.random() < 0.5 else text
    text = text.replace("'", "’").replace("-", rng.choice(["-", "‐", "–"]))
    return rng.choice(["", " ", " "]) + text + rng.choice(["", " ", ","])


def render_inputs(record: Dict[str, Any], cfg: Dict[str, Any], seed: int) -> Dict[str, Dict[str, Any]]:
    """Produce deterministic input renderings for a record. Never calls the address engine."""
    labels = record["labels"]
    rng = random.Random(f"{seed}:{record['id']}")
    sep = cfg.get("sep", ", ")
    iso2 = record["country"]
    has_state = bool(labels["state"])
    out: Dict[str, Dict[str, Any]] = {}

    def line(**kw: Any) -> str:
        return sep.join(_segments(labels, cfg, **kw))

    def add(style: str, fields: Dict[str, str]) -> None:
        entry: Dict[str, Any] = {"fields": {k: v for k, v in fields.items() if v is not None}}
        if style in UNSCORED:
            entry["unscored"] = list(UNSCORED[style])
        out[style] = entry

    add("structured", {"street1": _street1(labels, cfg), "city": labels["city"], "state": labels["state"],
                       "postal_code": labels["postcode"], "country": iso2})
    if has_state:
        add("structured_swapped", {"street1": _street1(labels, cfg), "city": labels["state"],
                                   "state": labels["city"], "postal_code": labels["postcode"], "country": iso2})
    base = line()
    add("line", {"street1": base, "country": iso2})
    add("line_country_text", {"street1": sep.join(_segments(labels, cfg, country_text=cfg["name"]))})
    add("line_nocomma", {"street1": " ".join(_segments(labels, cfg)), "country": iso2})
    add("line_upper", {"street1": base.upper(), "country": iso2})
    add("line_lower", {"street1": base.lower(), "country": iso2})
    abbreviated = _abbreviate(base, cfg["lang"])
    if abbreviated != base:
        add("line_abbrev", {"street1": abbreviated, "country": iso2})
    add("line_no_postal", {"street1": line(with_pc=False), "country": iso2})
    if has_state:
        add("line_swapped", {"street1": line(swap=True), "country": iso2})
    add("line_messy", {"street1": _messy(base, rng), "country": iso2})
    return out


def build_corpus(
    countries: List[str],
    per_country: int,
    seed: int,
    cache_dir: str,
    fetch_limit: int = 150,
    fetcher: Optional[Callable[[str], Dict[str, Any]]] = None,
    log: Callable[[str], None] = lambda m: None,
    holdout: bool = False,
    holdout_v2: bool = False,
) -> List[Dict[str, Any]]:
    """Fetch (or read from cache), label, sample and render. ``fetcher(query) -> payload`` is injectable."""
    if fetcher is None:  # pragma: no cover - network default
        def fetcher(q: str) -> Dict[str, Any]:
            return fetch_overpass(q, cache_dir)
    corpus: List[Dict[str, Any]] = []
    for iso2 in countries:
        cfg = COUNTRIES[iso2]
        pool: List[Dict[str, Any]] = []
        if holdout_v2:
            boxes = cfg.get("holdout_v2_bboxes", [])
        else:
            boxes = cfg.get("holdout_bboxes", []) if holdout else cfg["bboxes"]
        for bbox in boxes:
            for city_key in cfg.get("city_keys", ["addr:city"]):
                try:
                    payload = fetcher(build_query(bbox, city_key, fetch_limit))
                except OverpassError as exc:
                    log(f"{iso2} {bbox}: skipped ({exc})")
                    continue
                pool.extend(parse_elements(payload, iso2, cfg, city_key))
        # De-duplicate across bboxes, order deterministically, then sample.
        uniq = {r["id"]: r for r in pool}
        ordered = [uniq[k] for k in sorted(uniq)]
        random.Random(f"{seed}:{iso2}").shuffle(ordered)
        chosen = ordered[:per_country]
        log(f"{iso2}: {len(pool)} usable candidates, kept {len(chosen)}")
        for rec in chosen:
            rec["inputs"] = render_inputs(rec, cfg, seed)
            corpus.append(rec)
    return corpus


def write_corpus(corpus: List[Dict[str, Any]], path: str, seed: int, meta: Optional[Dict[str, Any]] = None) -> None:
    doc = {
        "_meta": {
            "description": "Evaluation corpus derived from OpenStreetMap addr:* tags. NOT human-reviewed.",
            "license": "ODbL 1.0 (c) OpenStreetMap contributors; see DATA_LICENSE.md",
            "seed": seed,
            "styles": list(STYLES),
            "records": len(corpus),
            **(meta or {}),
        },
        "records": corpus,
    }
    with open(path, "w", encoding="utf-8", newline="\n") as fh:
        fh.write('{"_meta": ' + json.dumps(doc["_meta"], ensure_ascii=False) + ',\n"records": [\n')
        fh.write(",\n".join(json.dumps(r, ensure_ascii=False, sort_keys=True) for r in corpus))
        fh.write("\n]}\n")


def main(argv: Optional[List[str]] = None) -> int:  # pragma: no cover - thin CLI wrapper
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--holdout", action="store_true",
                    help="use the disjoint holdout_bboxes (never used for tuning); changes default out/seed/per-country")
    ap.add_argument("--holdout-v2", action="store_true",
                    help="use the sealed holdout_v2_bboxes (measurement only; disjoint from sample and holdout v1)")
    ap.add_argument("--out", default=None,
                    help="default osm_sample.json, osm_holdout.json with --holdout, osm_holdout_v2.json with --holdout-v2")
    ap.add_argument("--countries", default=None, help="comma-separated ISO2 codes (default: all configured)")
    ap.add_argument("--per-country", type=int, default=None, help="default 22 (30 with --holdout)")
    ap.add_argument("--fetch-limit", type=int, default=150, help="max Overpass elements per bbox query")
    ap.add_argument("--seed", type=int, default=None, help="default 20261009 (20261201 with --holdout)")
    ap.add_argument("--cache-dir", default=os.path.join(HERE, ".cache"))
    ap.add_argument("--delay", type=float, default=5.0, help="seconds to wait after each network request")
    ap.add_argument("--offline", action="store_true", help="use only cached responses")
    ap.add_argument("--user-agent", default=USER_AGENT)
    args = ap.parse_args(argv)

    def fetcher(q: str) -> Dict[str, Any]:
        return fetch_overpass(q, args.cache_dir, user_agent=args.user_agent, delay=args.delay, offline=args.offline)

    v2 = args.holdout_v2
    hold = args.holdout and not v2
    if v2:
        out = args.out or os.path.join(HERE, "osm_holdout_v2.json")
        seed = args.seed if args.seed is not None else HOLDOUT_V2_SEED
        per_country = args.per_country or 30
        key = "holdout_v2_bboxes"
    else:
        out = args.out or os.path.join(HERE, "osm_holdout.json" if hold else "osm_sample.json")
        seed = args.seed if args.seed is not None else (HOLDOUT_SEED if hold else 20261009)
        per_country = args.per_country or (30 if hold else 22)
        key = "holdout_bboxes" if hold else "bboxes"
    default_countries = [c for c, cfg in COUNTRIES.items() if cfg.get(key)]
    wanted = [c.strip().upper() for c in (args.countries.split(",") if args.countries else default_countries)
              if c.strip()]
    corpus = build_corpus(wanted, per_country, seed, args.cache_dir, args.fetch_limit, fetcher,
                          log=lambda m: print(m, file=sys.stderr), holdout=hold, holdout_v2=v2)
    meta: Dict[str, Any] = {"countries": sorted({r["country"] for r in corpus})}
    if v2:
        meta["holdout"] = True
        meta["holdout_v2"] = True
        meta["note"] = ("Sealed held-out v2 set: areas disjoint from osm_sample.json and osm_holdout.json; "
                        "measurement only, never used to diagnose, tune or fix the engine.")
    elif hold:
        meta["holdout"] = True
        meta["note"] = "Held-out set: areas disjoint from osm_sample.json; never used for engine tuning."
    write_corpus(corpus, out, seed, meta)
    print(f"wrote {len(corpus)} records to {out}")
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
