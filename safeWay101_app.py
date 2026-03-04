import streamlit as st
import streamlit.components.v1 as components
from dotenv import load_dotenv
import os

#-----A inital setup for my streamlit env and pages-----------
load_dotenv()
st.set_page_config(layout="wide")
api_key = os.getenv("Google_Maps_API")


#-----Inital setup ends here-------------------------

# ----------------------Here starts my section for Maps Embed API------------------------------------
st.sidebar.title("SafeWay101 Controls")
address = st.sidebar.text_input("Enter a location", "Los Angeles, CA")

# There is my Embbedded URL for [Maps Embed API]
map_url = f"https://www.google.com/maps/embed/v1/place?key={api_key}&q={address}"

# Here I will configure aspects of my map sizes and the actual display
st.title("SafeWay101 Map")
components.html(
    f'<iframe width="100%" height="800" frameborder="0" style="border:0" src="{map_url}" allowfullscreen></iframe>',
    height=800,
)
# ----------------------Here ends my section for Maps Embed API------------------------------------

#----------------------Here starts my section for places API --------------------------------------


#----------------------Here ends my section for places API --------------------------------------
