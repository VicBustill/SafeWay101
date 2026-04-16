import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from dotenv import load_dotenv
import os
from map_controller import render_map
from places_autocomplete import get_autocomplete, get_place_details

#-----A inital setup for my streamlit env and pages-----------
load_dotenv()
st.set_page_config(layout="wide")
api_key = os.getenv("Google_Maps_API")


#-----Inital setup ends here-------------------------

# --- Places session token ---
if "places_session_token" not in st.session_state:
    st.session_state.places_session_token = os.urandom(16).hex()

places_token = st.session_state.places_session_token

def is_valid_lat_lng(lat, lng):
    return (
        lat is not None and lng is not None
        and isinstance(lat, (int, float))
        and isinstance(lng, (int, float))
        and -90 <= lat <= 90
        and -180 <= lng <= 180
    )
#This section will help with my autofill section of code
def sidebar_places_input(label: str, default_value: str, key_prefix: str):
    """
    Returns:
      typed_value: what user typed (store in session_state to persist)
      final_value: best value for mapping (lat,lng if available; else formatted address)
    """
    typed_value = st.sidebar.text_input(label, value=default_value, key=f"{key_prefix}_typed")
    final_value = typed_value  # fallback if no selection

    predictions = []
    if typed_value and len(typed_value) >= 3:
        data = get_autocomplete(
         typed_value,
         api_key,
         places_token,
         location=st.session_state.get("last_location"),  # "lat,lng" or None
         radius=50000,
         types="geocode",
         components="country:us",
        )
        predictions = data.get("predictions", [])

    if predictions:
        options = {p["description"]: p["place_id"] for p in predictions}
        choice = st.sidebar.selectbox(
            f"{label} suggestions",
            ["(pick one)"] + list(options.keys()),
            key=f"{key_prefix}_choice",
        )

        if choice != "(pick one)":
            details = get_place_details(options[choice], api_key, places_token)
            result = details.get("result", {})

            formatted = result.get("formatted_address", choice)
            loc = (result.get("geometry", {}).get("location") or {})
            lat = loc.get("lat")
            lng = loc.get("lng")

            final_value = f"{lat},{lng}" if (lat is not None and lng is not None) else formatted

    return typed_value, final_value



# ----------------------Here starts my section for Maps Embed API----------------------------------------
st.sidebar.title("SafeWay101 Controls")


# ---- Starting point logic ---
# ---- Session State Defaults ----
if "use_current_location" not in st.session_state:
    st.session_state.use_current_location = False

if "start_address" not in st.session_state:
    st.session_state.start_address = "Los Angeles, CA"

if "destination_address" not in st.session_state:
    st.session_state.destination_address = ""

if "radius_miles" not in st.session_state:
    st.session_state.radius_miles = 0

if "last_location" not in st.session_state:
    st.session_state.last_location = None

if "travel_mode" not in st.session_state:
    st.session_state.travel_mode = "DRIVING"

# ---- Toggle for manual or current location ----
use_current_location = st.sidebar.toggle(
    "Use Current Location",
    value=st.session_state.use_current_location,
    key="use_current_location"
)

status_text = "🟢 On" if use_current_location else "🔴 Off"
st.sidebar.markdown(f"**Status:** {status_text}")

radius_miles = st.sidebar.slider(
    "Radius (In miles)",
    min_value=0,
    max_value=3,
    value=st.session_state.radius_miles,
    step=1,
    key="radius_miles"
)

travel_mode = st.sidebar.selectbox(
    "Travel Mode",
    options=["Driving", "Walking", "Transit"],
    index=["DRIVING", "WALKING", "TRANSIT"].index(st.session_state.travel_mode),
    key="travel_mode",
)

# ---- Starting Point Logic ----
if use_current_location:
    # Invisible container in main page (hides the component's tiny UI)
    with st.container():
        st.markdown(
            """
            <style>
            div[data-testid="stHorizontalBlock"] button {
                height: 0px;
                padding: 0px;
                margin: 0px;
                visibility: hidden;
            }
            </style>
            """,
            unsafe_allow_html=True
        )
        loc = streamlit_geolocation()  # asks browser for permission which is needed for below

    with st.sidebar.expander("Location debug"):
        st.write(loc)

    if isinstance(loc, dict):
        lat = loc.get("latitude")
        lng = loc.get("longitude")
        accuracy = loc.get("accuracy")

        if is_valid_lat_lng(lat, lng):
           detected_coords = f"{lat},{lng}"
           st.session_state.last_location = detected_coords

           if accuracy is not None and accuracy <= 100:
               st.session_state.start_address = detected_coords
               st.sidebar.success(
                   f"Current location detected ({accuracy:.0f} m accuracy)"
            )
           elif accuracy is not None and accuracy <= 500:
               st.session_state.start_address = detected_coords
               st.sidebar.warning(
                   f"Current location detected, but it is coarse ({accuracy:.0f} m accuracy). "
                   "Verify before routing."
               )
           else:
               st.sidebar.warning(
                   "Current location looks approximate on this device. "
                   "Use manual input if the map looks wrong."
               )
        else:
            st.sidebar.info("Location data received, but coordinates were invalid.")
    else:
        st.sidebar.info("Waiting for location permission...")

    start_address = st.session_state.start_address

else:
    typed_start, start_address = sidebar_places_input(
        label="Enter starting point",
        default_value=st.session_state.start_address,
        key_prefix="start"
    )
    st.session_state.start_address = typed_start

# ---- Destination ----
typed_dest, destination_address = sidebar_places_input(
    label="Enter destination",
    default_value=st.session_state.destination_address,
    key_prefix="dest"
)
st.session_state.destination_address = typed_dest

st.sidebar.divider()

st.title("SafeWay101 Map")
render_map(api_key, start_address, destination_address, radius_miles, use_current_location,travel_mode)
# ----------------------Here ends my section for Maps Embed API------------------------------------



#----------------------Here starts my section for places API --------------------------------------


#----------------------Here ends my section for places API --------------------------------------
