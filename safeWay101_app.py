import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from dotenv import load_dotenv
import os
from map_controller import render_map

#-----A inital setup for my streamlit env and pages-----------
load_dotenv()
st.set_page_config(layout="wide")
api_key = os.getenv("Google_Maps_API")


#-----Inital setup ends here-------------------------

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

# ---- Toggle for manual or current location ----
use_current_location = st.sidebar.toggle(
    "Use Current Location",
    value=st.session_state.use_current_location,
    key="use_current_location"
)

status_text = "🟢 On" if use_current_location else "🔴 Off"
st.sidebar.markdown(f"**Status:** {status_text}")

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

    if loc and loc.get("latitude") and loc.get("longitude"):
        st.session_state.start_address = f"{loc['latitude']},{loc['longitude']}"
        st.sidebar.success("Current location detected")
    else:
        st.sidebar.info("Waiting for location permission...")

    start_address = st.session_state.start_address

else:
    st.session_state.start_address = st.sidebar.text_input(
        "Enter starting point",
        value=st.session_state.start_address
    )
    start_address = st.session_state.start_address

# ---- Destination ----
st.session_state.destination_address = st.sidebar.text_input(
    "Enter destination",
    value=st.session_state.destination_address
)
destination_address = st.session_state.destination_address


# Line below is my URL for [Maps Embed API]
from map_controller import render_map

st.title("SafeWay101 Map")
render_map(api_key, start_address, destination_address)
# ----------------------Here ends my section for Maps Embed API------------------------------------



#----------------------Here starts my section for places API --------------------------------------


#----------------------Here ends my section for places API --------------------------------------
