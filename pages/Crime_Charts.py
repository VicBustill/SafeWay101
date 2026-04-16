import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Crime Type Chart")

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

incidents = crime_data.get("incidents", [])
df = pd.DataFrame(incidents)

if df.empty:
    st.warning("No crime data available.")
else:
    chart_type = st.selectbox(
        "Select Chart Type",
        ["Pie Chart", "Bar Graph"]
    )

    offense_counts = df["incident_offense"].value_counts().sort_values(ascending=True)
    num_categories = len(offense_counts)

    if chart_type == "Pie Chart":
        fig, ax = plt.subplots(figsize=(8, 8))
        ax.pie(
            offense_counts,
            labels=offense_counts.index,
            autopct="%1.1f%%",
            startangle=90
        )
        ax.set_title("Crime Types by Incident Offense")
        plt.tight_layout()

    else:
        if num_categories == 1:
            fig_width = 5
            fig_height = 4
            bar_width = 0.25
        elif num_categories <= 3:
            fig_width = 7
            fig_height = 5
            bar_width = 0.4
        else:
            fig_width = max(8, num_categories * 1.5)
            fig_height = 5
            bar_width = 0.7

        fig, ax = plt.subplots(figsize=(fig_width, fig_height))

        x_positions = list(range(num_categories))
        ax.bar(x_positions, offense_counts.values, width=bar_width)

        ax.set_title("Crime Types by Incident Offense")
        ax.set_xlabel("Crime Type")
        ax.set_ylabel("Occurrences")

        ax.set_xticks(x_positions)
        ax.set_xticklabels(offense_counts.index, rotation=45, ha="right")

        max_value = offense_counts.max()

        if num_categories == 1:
            ax.set_ylim(0, max(5, max_value * 5))
            ax.set_xlim(-0.5, 0.5)
        elif num_categories <= 3:
            ax.set_ylim(0, max_value * 2)
            ax.margins(x=0.2)
        else:
            ax.set_ylim(0, max_value * 1.25)
            ax.margins(x=0.15)

        label_offset = max(max_value * 0.03, 0.1)

        for i, value in enumerate(offense_counts.values):
            ax.text(
                i,
                value + label_offset,
                str(value),
                ha="center",
                va="bottom"
            )

        plt.tight_layout()

    st.pyplot(fig)

    chart_df = offense_counts.reset_index()
    chart_df.columns = ["Crime Type", "Count"]

    st.subheader("Crime Type Breakdown")
    st.dataframe(chart_df, use_container_width=True)