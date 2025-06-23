import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import os

# Import backend logic from analysis folder
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'analysis')))
from analysis import ipl_analysis as ipl

# Load data
matches, deliveries = ipl.load_data()

# Page config
st.set_page_config(page_title="IPL Dashboard", layout="wide")

# Title
st.title("🏏 IPL Data Analysis Dashboard")

# Sidebar
st.sidebar.title("Navigation")
option = st.sidebar.radio("Select Section", ["Overview", "Top Teams", "Top Players", "Toss Impact", "Batting Stats","Bowling Stats"])

# Sidebar Filters with "All" Option
st.sidebar.subheader("🔍 Filter by:")

season_options = ["All"] + sorted(matches['season'].unique(), reverse=True)
selected_season = st.sidebar.selectbox("Season", season_options)

team_options = ["All"] + sorted(pd.unique(matches[['team1', 'team2']].values.ravel()))
selected_team = st.sidebar.selectbox("Team", team_options)

# Filter Matches by Season
if selected_season == "All":
    filtered_matches = matches.copy()
else:
    filtered_matches = matches[matches['season'] == selected_season]

# Match IDs for deliveries filter
match_ids = filtered_matches['id'].unique()
filtered_deliveries = deliveries[deliveries['match_id'].isin(match_ids)]

# Optional: Filter by Team
if selected_team != "All":
    filtered_matches = filtered_matches[
        (filtered_matches['team1'] == selected_team) | (filtered_matches['team2'] == selected_team)
    ]
    filtered_deliveries = filtered_deliveries[
        (filtered_deliveries['batting_team'] == selected_team) | (filtered_deliveries['bowling_team'] == selected_team)
    ]
season_display = "All Seasons" if selected_season == "All" else selected_season
team_display = "All Teams" if selected_team == "All" else selected_team
st.markdown(f"### 📅 Season: `{season_display}` | 🏏 Team: `{team_display}`")


# Overview Section
if option == "Overview":
    st.subheader("📊 Basic IPL Stats")
    stats = ipl.get_basic_overview(matches)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Matches", stats["Total Matches"])
    col2.metric("Seasons", stats["Total Seasons"])
    col3.metric("Teams", stats["Total Teams"])
    col4.metric("Unique PoM Players", stats["Unique Awarded Players"])

# Top Teams Section
elif option == "Top Teams":
    st.subheader("🏆 Top Winning Teams")
    top_teams = ipl.get_top_winning_teams(matches, top_n=10)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=top_teams.values, y=top_teams.index, palette="Blues_d", ax=ax)
    ax.set_title("Top Teams by Wins")
    ax.set_xlabel("Number of Wins")
    ax.set_ylabel("Teams")
    st.pyplot(fig)

# Top Players Section
elif option == "Top Players":
    st.subheader("🏅 Most Player of the Match Awards")
    top_players = ipl.get_top_players(matches, top_n=10)

    fig, ax = plt.subplots(figsize=(10, 5))
    sns.barplot(x=top_players.values, y=top_players.index, palette="magma", ax=ax)
    ax.set_title("Top Players by PoM Awards")
    ax.set_xlabel("Awards")
    ax.set_ylabel("Player")
    st.pyplot(fig)

# Toss Impact Section
elif option == "Toss Impact":
    st.subheader("🎲 Toss Impact Analysis")
    same, total, perc = ipl.get_toss_match_win_stats(filtered_matches)
    st.markdown(f"""
        ✅ **{same}** times out of **{total}** matches  
        ✅ Toss winner also won the match **{perc}%** of the time.
    """)
# Batting Stats Section
elif option == "Batting Stats":
    st.subheader("🏏 Top Run Scorers in IPL")
    top_batsmen = ipl.get_top_batsmen(filtered_deliveries)
    st.download_button("⬇ Download Top Batsmen", top_batsmen.to_csv().encode('utf-8'), file_name="top_batsmen.csv", mime="text/csv")
    st.dataframe(top_batsmen)
   
    
    st.subheader("⚡ Best Strike Rates (Min 200 Balls Faced)")
    top_strike = ipl.get_best_strike_rates(filtered_deliveries)
    st.download_button("⬇ Download Strike Rates", top_strike.to_csv().encode('utf-8'), file_name="strike_rates.csv", mime="text/csv")
    st.dataframe(top_strike.style.format({"strike_rate": "{:.2f}"}))
    
# Bowling Stats Section
elif option == "Bowling Stats":
    st.subheader("🎯 Top Wicket Takers")
    top_bowlers = ipl.get_top_wicket_takers(filtered_deliveries)
    top_bowlers_df = top_bowlers.reset_index().rename(columns={"index": "bowler", "bowler": "wickets"})
    st.download_button("⬇ Download Top Bowlers", top_bowlers_df.to_csv().encode('utf-8'), file_name="top_bowlers.csv", mime="text/csv")
    st.dataframe(top_bowlers_df)
   
    st.subheader("🔒 Best Economy Bowlers (Min 300 Balls Bowled)")
    top_economy = ipl.get_best_economy_bowlers(filtered_deliveries)
    st.download_button("⬇ Download Top Economy Bowlers", top_bowlers_df.to_csv().encode('utf-8'), file_name="economy.csv", mime="text/csv")
    st.dataframe(top_economy.style.format({"economy": "{:.2f}"}))
