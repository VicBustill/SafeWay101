import streamlit as st
import folium
from streamlit_folium import st_folium

# 1. Page Configuration
st.set_page_config(layout="wide")

# 2. Sidebar UI
with st.sidebar:
    st.title("Place Holder for Filters")
    st.subheader("Filter 1 Controls")
    
    # Example inputs
    map_style = st.selectbox(
        "Choose filter Style",
        ["OpenStreetMap", "filter2", "filter3"]
    )
    
    show_markers = st.checkbox("Show Points of Interest", value=True)
    
    st.info("Adjust the settings above to update the map on the right.")

# 3. Main Area (The Map)
st.title("SafeWay101 Dashboard")

# Create a placeholder or logic for your map
m = folium.Map(location=[34.0522, -118.2437], zoom_start=10, tiles=map_style)

# Add a marker if the checkbox is checked
if show_markers:
    folium.Marker(
        [34.0522, -118.2437], 
        popup="Los Angeles", 
        tooltip="Click for info"
    ).add_to(m)

# Render the map in the main area
st_folium(m, width=1200, height=600)