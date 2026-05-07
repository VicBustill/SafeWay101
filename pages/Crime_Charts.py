import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("Crime Offense Chart")

crime_markers = st.session_state.get("crime_markers", [])

if not crime_markers:
    st.warning("No LAPD crime records loaded yet.")
    st.info(
        "Go to the map page, choose a location and radius, "
        "then click 'Load nearby crime records'."
    )

else:
    rows = []

    for marker in crime_markers:
        summary = marker.get("summary", {})

        flags = summary.get("flags", [])

        if isinstance(flags, list):
            flags_text = ", ".join(flags)
        else:
            flags_text = str(flags) if flags else ""

        rows.append(
            {
                "Case No": marker.get("case_no"),
                "Offense": marker.get("title"),
                "Crime Against": summary.get("crime_against"),
                "Occurred": summary.get("occurred"),
                "Reported": summary.get("reported"),
                "Location": summary.get("location"),
                "Premise": summary.get("premise"),
                "Status": summary.get("status"),
                "Flags": flags_text,
                "Distance (m)": marker.get("distance_m"),
                "Icon Category": marker.get("icon_category"),
            }
        )

    df = pd.DataFrame(rows)

    st.subheader("Crime Summary")

    unique_cases = df["Case No"].dropna().nunique()

    col1, col2, col3 = st.columns(3)
    col1.metric("Nearby Records Count", len(df))
    col2.metric("Unique Case Count", unique_cases)
    col3.metric("Source", "LAPD / LA City")

    st.divider()

    offense_counts_full = (
        df["Offense"]
        .fillna("Unknown")
        .replace("", "Unknown")
        .value_counts()
    )

    max_categories = min(50, len(offense_counts_full))

    top_n = st.slider(
        "Number of offenses to show",
        min_value=5,
        max_value=max(5, max_categories),
        value=min(10, max_categories),
        step=1,
    )

    top_counts = offense_counts_full.head(top_n)
    other_count = offense_counts_full.iloc[top_n:].sum()

    if other_count > 0:
        offense_counts_plot = pd.concat(
            [
                top_counts,
                pd.Series({"Other": other_count}),
            ]
        )
    else:
        offense_counts_plot = top_counts

    offense_counts_plot = offense_counts_plot.sort_values(ascending=True)

    st.subheader("Offense Breakdown")

    num_categories = len(offense_counts_plot)

    fig_height = max(5, num_categories * 0.45)
    fig_width = 12

    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    ax.barh(
        offense_counts_plot.index,
        offense_counts_plot.values,
    )

    ax.set_title("Nearby Crime Records by Offense")
    ax.set_xlabel("Nearby Records")
    ax.set_ylabel("Offense")

    max_value = offense_counts_plot.max()

    if max_value == 1:
        ax.set_xlim(0, 5)
    else:
        ax.set_xlim(0, max_value * 1.25)

    label_offset = max(max_value * 0.02, 0.1)

    for i, value in enumerate(offense_counts_plot.values):
        ax.text(
            value + label_offset,
            i,
            str(value),
            va="center",
        )

    plt.tight_layout()

    st.pyplot(fig)
