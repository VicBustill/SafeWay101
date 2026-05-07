import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("Crime Stats")


def get_available_date_range(df, date_column):
    valid_dates = df[date_column].dropna()

    if valid_dates.empty:
        return None, None

    earliest_date = valid_dates.min().date()
    latest_date = valid_dates.max().date()

    return earliest_date, latest_date


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

        rows.append(
            {
                "Description": marker.get("title"),
                "Occurred": summary.get("occurred"),
                "Reported": summary.get("reported"),
                "Location": summary.get("location"),

                # Used only for filtering/sorting.
                # Prefer raw ISO timestamp if available.
                "Occurred Source": summary.get("occurred_raw") or summary.get("occurred"),
            }
        )

    df = pd.DataFrame(rows)

    df["Occurred Source"] = (
        df["Occurred Source"]
        .fillna("")
        .astype(str)
        .str.replace(" at ", " ", regex=False)
    )

    df["Occurred Date"] = pd.to_datetime(
        df["Occurred Source"],
        errors="coerce"
    )

    earliest_date, latest_date = get_available_date_range(
        df,
        "Occurred Date"
    )

    st.subheader("Nearby Crime Records")

    st.markdown("### Filter")

    if earliest_date is None or latest_date is None:
        st.warning("No valid occurred dates available for filtering.")
        start_date = None
        end_date = None

    else:
        st.caption(
            f"Available occurred date range: {earliest_date} to {latest_date}"
        )

        col1, col2 = st.columns(2)

        with col1:
            start_date = st.date_input(
                "Occurred between",
                value=None,
                min_value=earliest_date,
                max_value=latest_date,
                key="occurred_start_date",
            )

        with col2:
            end_date = st.date_input(
                "to",
                value=None,
                min_value=earliest_date,
                max_value=latest_date,
                key="occurred_end_date",
            )

    filtered_df = df.copy()

    invalid_date_range = (
        start_date is not None
        and end_date is not None
        and start_date > end_date
    )

    if invalid_date_range:
        st.error(
            "Invalid date range: the start date must be before or equal to the end date."
        )

        filtered_df = df.iloc[0:0].copy()

    else:
        if start_date is not None:
            filtered_df = filtered_df[
                filtered_df["Occurred Date"].dt.date >= start_date
            ]

        if end_date is not None:
            filtered_df = filtered_df[
                filtered_df["Occurred Date"].dt.date <= end_date
            ]

        filtered_df = filtered_df.sort_values(
            by="Occurred Date",
            ascending=True
        )

    display_df = filtered_df[
        [
            "Description",
            "Occurred",
            "Reported",
            "Location",
        ]
    ]

    st.dataframe(display_df, use_container_width=True)