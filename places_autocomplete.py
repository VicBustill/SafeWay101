import requests

AUTOCOMPLETE_URL = "https://maps.googleapis.com/maps/api/place/autocomplete/json"
DETAILS_URL = "https://maps.googleapis.com/maps/api/place/details/json"

def get_autocomplete(
    query: str,
    api_key: str,
    session_token: str,
    location: str | None = None,   # "lat,lng"
    radius: int | None = None,      # meters
    types: str | None = None,       # e.g. "geocode"
    components: str | None = None,  # e.g. "country:us"
):
    params = {
        "input": query,
        "key": api_key,
        "sessiontoken": session_token,
    }

    # Optional quality boosters
    if location:
        params["location"] = location
    if radius:
        params["radius"] = radius
    if types:
        params["types"] = types
    if components:
        params["components"] = components

    try:
        r = requests.get(AUTOCOMPLETE_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        if data.get("status") != "OK":
            return {"predictions": []}

        return data
    except requests.RequestException:
        return {"predictions": []}


def get_place_details(place_id: str, api_key: str, session_token: str):
    params = {
        "place_id": place_id,
        "fields": "formatted_address,geometry",
        "key": api_key,
        "sessiontoken": session_token,
    }
    try:
        r = requests.get(DETAILS_URL, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()

        if data.get("status") != "OK":
            return {"result": {}}

        return data

    except requests.RequestException:
        return {"result": {}}