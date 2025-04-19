import streamlit as st
import pandas as pd
import altair as alt

# Load data
@st.cache_data
def load_data():
    batting_df = pd.read_csv("aggregated_batting_vs_bowling_type.csv")
    match_df = pd.read_csv("match_metadata.csv")
    
    # Merge to get season info if not already in batting_df
    if 'season' not in batting_df.columns:
        batting_df = batting_df.merge(match_df[['match_id', 'season']], on='match_id', how='left')
    
    return batting_df

df = load_data()

# ----------------------------
# Sidebar Inputs
# ----------------------------
st.sidebar.title("⚙️ Dashboard Filters")

bowling_type = st.sidebar.selectbox(
    "Select Bowling Type",
    ["Right Fast", "Left Fast", "Spin"]
)

years = sorted(df['season'].dropna().unique())[::-1]
selected_seasons = st.sidebar.multiselect(
    "Select Seasons",
    years,
    default=years[:2]  # Default last 2 seasons
)

top_n = st.sidebar.slider("Select number of top batsmen", 3, 20, 5)

# ----------------------------
# Mapping for dynamic filtering
# ----------------------------
bowling_columns = {
    "Right Fast": ("runs_against_right_fast", "balls_against_right_fast"),
    "Left Fast": ("runs_against_left_fast", "balls_against_left_fast"),
    "Spin": ("runs_against_spin", "balls_against_spin"),
}

run_col, ball_col = bowling_columns[bowling_type]

# Filter and calculate strike rate
filtered_df = df[df["season"].isin(selected_seasons)]

# Remove rows with zero balls
filtered_df = filtered_df[filtered_df[ball_col] > 0].copy()

filtered_df["strike_rate"] = 100 * filtered_df[run_col] / filtered_df[ball_col]

# Aggregate strike rates per batsman
agg_df = filtered_df.groupby("name").agg({
    run_col: "sum",
    ball_col: "sum"
}).reset_index()

agg_df = agg_df[agg_df[ball_col] > 0].copy()
agg_df["strike_rate"] = 100 * agg_df[run_col] / agg_df[ball_col]

top_batsmen_df = agg_df.sort_values("strike_rate", ascending=False).head(top_n)

# ----------------------------
# Display Results
# ----------------------------
st.title("🏏 IPL Auction Dashboard")
st.subheader(f"Top {top_n} Batsmen by Strike Rate vs {bowling_type}")
st.caption(f"Filtered by seasons: {', '.join(map(str, selected_seasons))}")

# Bar chart
chart = alt.Chart(top_batsmen_df).mark_bar().encode(
    x=alt.X('strike_rate:Q', title='Strike Rate'),
    y=alt.Y('name:N', sort='-x', title='Batsman'),
    tooltip=["name", "strike_rate"]
).properties(
    width=700,
    height=400
)

st.altair_chart(chart, use_container_width=True)