import pandas as pd
import os
# ---------- File Paths ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATCHES_PATH = os.path.join(BASE_DIR, '..', 'data', 'matches.csv')
DELIVERIES_PATH = os.path.join(BASE_DIR, '..', 'data', 'deliveries.csv')
# ---------- Load Data ----------
def load_data():
    matches = pd.read_csv(MATCHES_PATH)
    deliveries = pd.read_csv(DELIVERIES_PATH)

    # Clean column names
    matches.columns = matches.columns.str.strip().str.lower()
    deliveries.columns = deliveries.columns.str.strip().str.lower()

    # Fix season column if missing
    if 'season' not in matches.columns:
        matches['date'] = pd.to_datetime(matches['date'])
        matches['season'] = matches['date'].dt.year

    return matches, deliveries

# ---------- Overview Stats ----------
def get_basic_overview(matches_df):
    total_matches = matches_df.shape[0]
    total_seasons = matches_df['season'].nunique()
    total_teams = pd.unique(matches_df[['team1', 'team2']].values.ravel()).shape[0]
    total_players = matches_df['player_of_match'].nunique()

    return {
        "Total Matches": total_matches,
        "Total Seasons": total_seasons,
        "Total Teams": total_teams,
        "Unique Awarded Players": total_players
    }

# ---------- Top Teams ----------
def get_top_winning_teams(matches_df, top_n=5):
    win_counts = matches_df['winner'].value_counts().head(top_n)
    return win_counts

# ---------- Top Players ----------
def get_top_players(matches_df, top_n=10):
    return matches_df['player_of_match'].value_counts().head(top_n)

# ---------- Toss vs Match Winner ----------
def get_toss_match_win_stats(matches_df):
    same = matches_df[matches_df['toss_winner'] == matches_df['winner']].shape[0]
    total = matches_df.shape[0]
    percentage = round((same / total) * 100, 2)
    return same, total, percentage

# ---------- Top Run Scorers ----------
def get_top_batsmen(deliveries_df, top_n=10):
    runs_by_batsman = deliveries_df.groupby('batsman')['batsman_runs'].sum()
    top_batsmen = runs_by_batsman.sort_values(ascending=False).head(top_n)
    return top_batsmen

# ---------- Best Strike Rates (min 200 balls faced) ----------
def get_best_strike_rates(deliveries_df, min_balls=200, top_n=10):
    batsman_stats = deliveries_df.groupby('batsman').agg({
        'batsman_runs': 'sum',
        'ball': 'count'
    }).rename(columns={'ball': 'balls_faced'})

    batsman_stats = batsman_stats[batsman_stats['balls_faced'] >= min_balls]
    batsman_stats['strike_rate'] = (batsman_stats['batsman_runs'] / batsman_stats['balls_faced']) * 100
    top_strike_rate = batsman_stats.sort_values(by='strike_rate', ascending=False).head(top_n)

    return top_strike_rate[['strike_rate']]

# ---------- Top Wicket Takers ----------
def get_top_wicket_takers(deliveries_df, top_n=10):
    # Remove extra runs (like leg-byes, wides) that don't count as wickets
    wickets_df = deliveries_df[deliveries_df['dismissal_kind'].notnull()]
    top_bowlers = wickets_df['bowler'].value_counts().head(top_n)
    return top_bowlers

# ---------- Best Economy Rates (Min 300 balls bowled) ----------
def get_best_economy_bowlers(deliveries_df, min_balls=300, top_n=10):
    df = deliveries_df.copy()
    
    # Count only valid deliveries
    df = df[df['wide_runs'] == 0]
    df = df[df['noball_runs'] == 0]

    bowler_stats = df.groupby('bowler').agg({
        'total_runs': 'sum',
        'ball': 'count'
    }).rename(columns={'ball': 'balls_bowled'})

    bowler_stats = bowler_stats[bowler_stats['balls_bowled'] >= min_balls]
    bowler_stats['economy'] = (bowler_stats['total_runs'] / bowler_stats['balls_bowled']) * 6
    top_economy = bowler_stats.sort_values(by='economy').head(top_n)

    return top_economy[['economy']]

