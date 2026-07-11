# pages/03_demand.py — demand analysis page

import os
import sys

import plotly.express as px
import streamlit as st


sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from utils import load_data, sidebar_filters


# Load the data and apply the same persistent filters used on Pages 1 and 2.
df, p95 = load_data()
filtered = sidebar_filters(df, p95)


st.title("Where is guest demand strongest?")

st.caption(
    "Reviews per month are used as a proxy for guest demand. "
    "Higher review activity may indicate stronger guest interest."
)


# Create a list of room types that remain after the sidebar filters.
room_types_available = sorted(
    filtered["room_type"].dropna().unique()
)


# Initialise the page-specific widget once.
if "sel_room" not in st.session_state:
    st.session_state.sel_room = room_types_available[0]
else:
    # Keep the room-type choice alive while navigating between pages.
    st.session_state.sel_room = st.session_state.sel_room


# Guard against a previously selected room type being filtered out.
if st.session_state.sel_room not in room_types_available:
    st.session_state.sel_room = room_types_available[0]


st.selectbox(
    "Focus on one room type",
    room_types_available,
    key="sel_room",
)


selected_room = st.session_state.sel_room

room_df = filtered[
    filtered["room_type"] == selected_room
].copy()


# Treat missing review values as zero review activity.
selected_reviews = room_df["reviews_per_month"].fillna(0)
market_reviews = filtered["reviews_per_month"].fillna(0)

selected_demand = selected_reviews.median()
market_demand = market_reviews.median()
demand_difference = selected_demand - market_demand


# KPI row: these three metrics should communicate the story within five seconds.
k1, k2, k3 = st.columns(3)

k1.metric(
    "Listings",
    f"{len(room_df):,}",
)

k2.metric(
    "Median Reviews/Month",
    f"{selected_demand:.1f}",
    f"{demand_difference:+.1f} vs filtered market",
)

k3.metric(
    "Median Price",
    f"£{room_df['price'].median():.0f}/night",
)


st.divider()


plot_df = filtered.copy()

plot_df["reviews_per_month"] = (
    plot_df["reviews_per_month"].fillna(0)
)

plot_df["highlight"] = plot_df["room_type"].apply(
    lambda room_type: (
        selected_room
        if room_type == selected_room
        else "Other room types"
    )
)


# BBD HIGHLIGHT COLOUR TYPE:
# Blue highlights the selected room type, while grey makes other listings
# recede. Red and green are not used as the only differentiator.
fig = px.scatter(
    plot_df,
    x="price",
    y="reviews_per_month",
    color="highlight",
    opacity=0.65,
    color_discrete_map={
        selected_room: "#2E75B6",
        "Other room types": "#AAAAAA",
    },
    labels={
        "price": "Nightly Price (£)",
        "reviews_per_month": "Reviews per Month",
        "highlight": "",
    },
    title=(
        f"{selected_room} demand is concentrated at particular "
        "price levels"
    ),
    hover_data={
        "neighbourhood": True,
        "room_type": True,
        "price": ":.0f",
        "reviews_per_month": ":.1f",
    },
)


fig.update_traces(
    marker=dict(
        size=7,
        line_width=0,
    )
)


fig.update_layout(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(
        family="Arial",
        size=12,
    ),
    xaxis=dict(
        gridcolor="#EEEEEE",
        title="Nightly Price (£)",
    ),
    yaxis=dict(
        gridcolor="#EEEEEE",
        title="Reviews per Month",
    ),
    legend=dict(
        orientation="h",
        y=1.08,
    ),
    margin=dict(
        l=10,
        r=10,
        t=60,
        b=10,
    ),
)


st.plotly_chart(fig, use_container_width=True)


with st.expander("How is demand estimated?"):
    st.write(
        "The dataset does not contain confirmed booking totals. "
        "Reviews per month are therefore used as a demand proxy. "
        "Listings with more reviews may have more guest stays, but this "
        "measure is not exact because not every guest writes a review."
    )