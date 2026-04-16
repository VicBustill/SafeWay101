import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Crime Stats")

crime_data = {
    "incidents_count": 1,
    "pages_count": 1,
    "incidents": [
        {
            "city_key": "CHI",
            "incident_code": "13337116",
            "incident_date": "2024-01-12T21:00:00Z",
            "incident_offense": "Motor Vehicle Theft",
            "incident_offense_code": "240",
            "incident_offense_description": "Motor Vehicle Theft",
            "incident_offense_detail_description": "Motor Vehicle Theft at 050XX N LAKE SHORE DR SB",
            "incident_offense_crime_against": "Property",
            "incident_offense_action": "C",
            "incident_source_original_type": "MOTOR VEHICLE THEFT - THEFT / RECOVERY - AUTOMOBILE",
            "incident_source_name": "Chicago_Police_Department",
            "incident_latitude": 41.9751781,
            "incident_longitude": -87.6499609,
            "incident_address": "050XX N LAKE SHORE DR SB"
        }
    ]
}

st.subheader("Crime Summary")
col1, col2 = st.columns(2)
col1.metric("Incidents Count", crime_data["incidents_count"])
col2.metric("Pages Count", crime_data["pages_count"])

incidents_df = pd.DataFrame(crime_data["incidents"])

display_df = incidents_df[
    [
        "incident_date",
        "incident_offense",
        "incident_offense_description",
        "incident_offense_crime_against",
        "incident_address",
        "incident_source_name",
    ]
].copy()

display_df.columns = [
    "Date",
    "Offense",
    "Description",
    "Crime Against",
    "Address",
    "Source",
]

st.subheader("Incident Table")
st.dataframe(display_df, use_container_width=True)