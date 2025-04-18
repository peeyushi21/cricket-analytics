import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Team Dismissal Analysis", layout="wide")
st.title("🎯 Team Dismissal Breakdown")
st.markdown("Select a team and season to view dismissal type distribution.")

# Load Data
@st.cache_data
def load_data():
    return pd.read_csv("data/mw_overall.csv")

df = load_data()

# Define dismissal types
dismissal_cols = ["bowled", "caught", "caught and bowled", "lbw", "run out"]
required_cols = dismissal_cols + ["batting_team", "season"]

# Check for required columns
missing_cols = [col for col in required_cols if col not in df.columns]
if missing_cols:
    st.error(f"Missing columns: {missing_cols}")
else:
    # STEP 1: Merge seasons like 2002 and 2003 into 2002/03
    season_mapping = {}

    # Extract all proper "YYYY/YY" seasons
    combined_seasons = df["season"].dropna().unique()
    combined_seasons = [s for s in combined_seasons if isinstance(s, str) and "/" in s]

    for cs in combined_seasons:
        try:
            base_year = int(cs.split("/")[0])
            season_mapping[str(base_year)] = cs
            season_mapping[str(base_year + 1)] = cs
        except:
            pass

    # Normalize all seasons
    def normalize_season(season_val):
        season_str = str(season_val)
        return season_mapping.get(season_str, season_str)

    df["normalized_season"] = df["season"].apply(normalize_season)

    # STEP 2: Select season
    available_seasons = sorted(df["normalized_season"].unique())
    selected_season = st.radio("📅 Select Season", available_seasons, horizontal=True)

    # Filter data by selected season
    season_df = df[df["normalized_season"] == selected_season]

    # STEP 3: Select team
    teams = sorted(season_df["batting_team"].dropna().unique())
    selected_team = st.selectbox("🏏 Select Team", teams)

    # STEP 4: Summarize dismissals for the selected team
    team_dismissals = (
        season_df[season_df["batting_team"] == selected_team][dismissal_cols]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
    )
    team_dismissals.columns = ["Dismissal Type", "Count"]
    team_dismissals = team_dismissals[team_dismissals["Count"] > 0]

    # STEP 5: Plot pie chart with enhanced styling
    fig = px.pie(
        team_dismissals,
        names="Dismissal Type",
        values="Count",
        title=f"{selected_team} Dismissal Breakdown - {selected_season}",
        color_discrete_sequence=px.colors.qualitative.Set3,
        hole=0.4
    )

    fig.update_traces(
        textinfo='label+percent',
        pull=[0.03] * len(team_dismissals),
        marker=dict(line=dict(color='black', width=1)),
        hovertemplate="%{label}: %{value} dismissals (%{percent})<extra></extra>"
    )

    st.plotly_chart(fig, use_container_width=True)
