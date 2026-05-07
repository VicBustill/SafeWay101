import os
import math
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DATASET_ID = "k7nn-b2ep"
QUERY_URL = f"https://data.lacity.org/api/v3/views/{DATASET_ID}/query.json"

LAPD_API_KEY = os.getenv("LAPD_API")


def make_bounding_box(center_lat, center_lng, radius_meters):
    lat_delta = radius_meters / 111_320

    lon_delta = radius_meters / (
        111_320 * math.cos(math.radians(center_lat))
    )

    return {
        "south": center_lat - lat_delta,
        "north": center_lat + lat_delta,
        "west": center_lng - lon_delta,
        "east": center_lng + lon_delta,
    }


def haversine_meters(lat1, lng1, lat2, lng2):
    earth_radius_m = 6_371_000

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)

    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lng2 - lng1)

    a = (
        math.sin(delta_phi / 2) ** 2
        + math.cos(phi1)
        * math.cos(phi2)
        * math.sin(delta_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    return earth_radius_m * c


def is_yes(value):
    if isinstance(value, bool):
        return value

    if value is None:
        return False

    return str(value).strip().lower() in {"true", "yes", "y", "1", "t"}


def clean_nibr_description(raw_description):
    if not raw_description:
        return "Unknown offense"

    parts = [part.strip() for part in raw_description.split(" - ")]

    if len(parts) >= 2:
        last_part = parts[-2] if len(parts[-1]) <= 4 else parts[-1]
        return last_part

    return raw_description


def active_flags(record):
    flag_map = {
        "victim_shot": "Victim shot",
        "domestic_violence": "Domestic violence",
        "hate_crime": "Hate crime",
        "gang_related": "Gang-related",
        "transit_related": "Transit-related",
        "homeless_victim": "Homeless victim",
        "homeless_suspect": "Homeless suspect",
        "homeless_arrestee": "Homeless arrestee",
    }

    flags = []

    for field, label in flag_map.items():
        if is_yes(record.get(field)):
            flags.append(label)

    return flags


def choose_icon_category(record):
    description = (record.get("nibr_description") or "").lower()
    crime_against = (record.get("crime_against") or "").lower()

    if is_yes(record.get("victim_shot")):
        return "high-severity-crime"

    property_words = [
        "theft",
        "burglary",
        "vandalism",
        "robbery",
        "vehicle",
        "stolen",
    ]

    person_words = [
        "assault",
        "battery",
        "threat",
        "homicide",
        "kidnap",
        "sex",
    ]

    society_words = [
        "parole",
        "weapon",
        "narcotic",
        "drug",
        "trespass",
        "violation",
    ]

    if any(word in description for word in person_words):
        return "person-crime"

    if any(word in description for word in property_words):
        return "property-crime"

    if any(word in description for word in society_words):
        return "society-crime"

    if "person" in crime_against:
        return "person-crime"

    if "property" in crime_against:
        return "property-crime"

    if "society" in crime_against:
        return "society-crime"

    return "unknown-crime"
def format_lapd_datetime(value):
    if not value:
        return "Unknown"

    text = str(value).strip()

    try:
        dt = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return text

    month = dt.strftime("%b")
    day = dt.day
    year = dt.year

    hour = dt.strftime("%I").lstrip("0")
    minute = dt.strftime("%M")
    am_pm = dt.strftime("%p")

    return f"{month} {day}, {year} at {hour}:{minute} {am_pm}"

def make_marker(record, center_lat, center_lng):
    lat = float(record["lat"])
    lng = float(record["lon"])

    distance_m = haversine_meters(center_lat, center_lng, lat, lng)

    flags = active_flags(record)

    return {
        "marker_id": record.get("unique_nibr_no") or record.get("case_no"),
        "case_no": record.get("case_no"),
        "lat": lat,
        "lon": lng,
        "distance_m": round(distance_m, 1),
        "icon_category": choose_icon_category(record),
        "title": clean_nibr_description(record.get("nibr_description")),
        "summary": {
            "crime_against": record.get("crime_against"),
            "occurred": record.get("date_occ"),
            "reported": record.get("date_rptd"),
            "time_occ": record.get("time_occ"),
            "location": record.get("location"),
            "premise": record.get("premise_desc"),
            "status": record.get("status_desc"),
            "flags": flags,

            "occurred": format_lapd_datetime(record.get("date_occ")),
            "reported": format_lapd_datetime(record.get("date_rptd")),
        },
    }


def get_nearby_crime_markers(center_lat, center_lng, radius_meters, max_records=500):
    if not LAPD_API_KEY:
        raise RuntimeError("Missing LAPD_API key in .env file.")

    bbox = make_bounding_box(center_lat, center_lng, radius_meters)

    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept": "application/json",
        "X-App-Token": LAPD_API_KEY,
    }

    query = f"""
        SELECT
            `uniquenibrno` AS `unique_nibr_no`,
            `caseno` AS `case_no`,
            `date_rptd` AS `date_rptd`,
            `date_occ` AS `date_occ`,
            `time_occ` AS `time_occ`,
            `hndrdth_loc_chk` AS `location`,
            `hndrdth_lat` AS `lat`,
            `hndrdth_lon` AS `lon`,
            `nibr_description` AS `nibr_description`,
            `crime_against` AS `crime_against`,
            `premis_desc` AS `premise_desc`,
            `status_desc` AS `status_desc`,
            `victim_shot` AS `victim_shot`,
            `domestic_violence_crime` AS `domestic_violence`,
            `hate_crime` AS `hate_crime`,
            `gang_related_crime` AS `gang_related`,
            `transit_related_crime` AS `transit_related`,
            `homeless_victim_crime` AS `homeless_victim`,
            `homeless_suspect_crime` AS `homeless_suspect`,
            `homeless_arrestee_crime` AS `homeless_arrestee`
        WHERE
            `hndrdth_lat` IS NOT NULL
            AND `hndrdth_lon` IS NOT NULL
            AND `hndrdth_lat` >= {bbox["south"]}
            AND `hndrdth_lat` <= {bbox["north"]}
            AND `hndrdth_lon` >= {bbox["west"]}
            AND `hndrdth_lon` <= {bbox["east"]}
        LIMIT {max_records}
    """

    response = requests.get(
        QUERY_URL,
        headers=headers,
        params={"query": query},
        timeout=30,
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"LAPD API error {response.status_code}: {response.text[:1000]}"
        )

    records = response.json()

    markers = []

    for record in records:
        try:
            lat = float(record["lat"])
            lng = float(record["lon"])
        except (KeyError, TypeError, ValueError):
            continue

        distance_m = haversine_meters(center_lat, center_lng, lat, lng)

        if distance_m <= radius_meters:
            markers.append(make_marker(record, center_lat, center_lng))

    markers.sort(key=lambda marker: marker["distance_m"])

    return markers