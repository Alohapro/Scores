
import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
from itertools import combinations

# Connect or create database
conn = sqlite3.connect('pickleball.db', check_same_thread=False)
cursor = conn.cursor()

# Create table if not exists
cursor.execute('''
CREATE TABLE IF NOT EXISTS matches (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    team1_player1 TEXT,
    team1_player2 TEXT,
    team2_player1 TEXT,
    team2_player2 TEXT,
    team1_score INTEGER,
    team2_score INTEGER,
    date TEXT
)
''')
conn.commit()

# Player list
players = ["AK", "NK", "VS", "GB", "MB", "AC", "JJ", "PS", "Player9", "Player10"]

st.title("🏓 Pickle Pack Point Diff Negative Scoring")
st.subheader("Log a Pickleball Match")

# Form to enter match result
with st.form("match_form"):
    col1, col2 = st.columns(2)
    with col1:
        team1_player1 = st.selectbox("Team 1 - Player 1", players)
        team1_player2 = st.selectbox("Team 1 - Player 2", [p for p in players if p != team1_player1])
        team1_score = st.number_input("Team 1 Score", min_value=0, max_value=11, step=1)

    with col2:
        team2_player1 = st.selectbox("Team 2 - Player 1", [p for p in players if p not in [team1_player1, team1_player2]])
        team2_player2 = st.selectbox("Team 2 - Player 2", [p for p in players if p not in [team1_player1, team1_player2, team2_player1]])
        team2_score = st.number_input("Team 2 Score", min_value=0, max_value=11, step=1)

    submit = st.form_submit_button("Log Match")

if submit:
    match_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute('''
        INSERT INTO matches (team1_player1, team1_player2, team2_player1, team2_player2, team1_score, team2_score, date)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (team1_player1, team1_player2, team2_player1, team2_player2, team1_score, team2_score, match_date))
    conn.commit()
    st.success("Match logged successfully!")

# Show Leaderboard
st.subheader("📊 Leaderboard (Negative Points)")

# Fetch match data
df = pd.read_sql_query("SELECT * FROM matches", conn)

# Calculate negative points
from collections import defaultdict

pair_scores = defaultdict(int)

for _, row in df.iterrows():
    t1 = f"{row['team1_player1']} & {row['team1_player2']}"
    t2 = f"{row['team2_player1']} & {row['team2_player2']}"
    s1 = row['team1_score']
    s2 = row['team2_score']

    if s1 > s2:
        pair_scores[t2] += (11 - s2) * 2
    elif s2 > s1:
        pair_scores[t1] += (11 - s1) * 2

leaderboard = pd.DataFrame(pair_scores.items(), columns=["Pair", "Total Negative Points"]).sort_values("Total Negative Points", ascending=False)

st.dataframe(leaderboard)

# Show match history
with st.expander("📜 Match History"):
    st.dataframe(df)
