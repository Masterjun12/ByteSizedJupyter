import streamlit as st
import sqlite3
import pandas as pd
import time

DB_PATH = "game_bet.db"

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def get_game_numbers():
    conn = get_connection()
    df = pd.read_sql("SELECT game_number FROM game", conn)
    conn.close()
    return df["game_number"].tolist() if not df.empty else []

def get_game_info(game_number):
    conn = get_connection()
    query = "SELECT * FROM game WHERE game_number = ?"
    df = pd.read_sql(query, conn, params=(game_number,))
    conn.close()
    return df

def get_bet_info(game_number):
    conn = get_connection()
    query = "SELECT * FROM bet WHERE game_number = ?"
    df = pd.read_sql(query, conn, params=(game_number,))
    conn.close()
    return df

st.title("📢 경기 진행 화면")

selected_game = st.selectbox("게임 번호 선택", get_game_numbers())

timer_value = st.number_input("⏳ 배팅 마감까지 남은 시간 (초)", min_value=1, value=30, step=1)

if st.button("▶ 타이머 시작"):
    with st.empty():
        for i in range(timer_value, -1, -1):
            st.write(f"⏳ 배팅 마감까지 {i}초 남음")
            time.sleep(1)
            if i == 0:
                st.balloons()

st.markdown(
    """
    <style>
    @keyframes gradientAnimation {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    .animated-box {
        background: linear-gradient(-45deg, #ff7e5f, #feb47b, #86a8e7, #7f7fd5);
        background-size: 400% 400%;
        animation: gradientAnimation 5s ease infinite;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        font-weight: bold;
        font-size: 18px;
        margin: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if selected_game:
    game_info = get_game_info(selected_game).iloc[0]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f'<div class="animated-box">🏠 홈팀: {game_info["home_player_name"]}<br> 배당: {game_info["home_odds"]}</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'<div class="animated-box">🏆 어웨이팀: {game_info["away_player_name"]}<br> 배당: {game_info["away_odds"]}</div>', unsafe_allow_html=True)
    
    st.subheader("💰 배팅 정보")
    bet_info = get_bet_info(selected_game)
    if not bet_info.empty:
        bet_info['payout'] = bet_info.apply(lambda row: row['bet_amount'] * (game_info['home_odds'] if row['bet_team'] == 'home' else game_info['away_odds']), axis=1)
        st.dataframe(bet_info[['bettor_name', 'bet_amount', 'bet_team', 'payout']], use_container_width=True)
    else:
        st.info("아직 배팅 내역이 없습니다.")
