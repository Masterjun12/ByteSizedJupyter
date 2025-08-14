import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "game_bet_all.db"

# 데이터베이스 연결 함수
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False, timeout=1)

# 게임 정보 가져오기
def get_game_numbers():
    conn = get_connection()
    df = pd.read_sql("SELECT game_number FROM game", conn)
    conn.close()
    return df["game_number"].tolist() if not df.empty else []

# 선수 목록 가져오기
def get_players(game_number):
    conn = get_connection()
    query = "SELECT * FROM player WHERE game_number = ?"
    df = pd.read_sql(query, conn, params=(game_number,))
    conn.close()
    return df

# 배팅 내역 가져오기
def get_bets(game_number):
    conn = get_connection()
    query = "SELECT * FROM bet WHERE game_number = ?"
    df = pd.read_sql(query, conn, params=(game_number,))
    conn.close()
    return df

# 게임 삭제
def delete_game(game_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM game WHERE game_number = ?", (game_number,))
    cursor.execute("DELETE FROM player WHERE game_number = ?", (game_number,))
    cursor.execute("DELETE FROM bet WHERE game_number = ?", (game_number,))
    conn.commit()
    conn.close()

# 선수 정보 수정
def update_player(player_id, player_name, odds, remarks):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE player SET player_name = ?, odds = ?, remarks = ? WHERE id = ?",
        (player_name, odds, remarks, player_id),
    )
    conn.commit()
    conn.close()

# 선수 삭제
def delete_player(player_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM player WHERE id = ?", (player_id,))
    cursor.execute("DELETE FROM bet WHERE player_id = ?", (player_id,))
    conn.commit()
    conn.close()

# 배팅 내역 수정
def update_bet(bet_id, bet_amount, player_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE bet SET bet_amount = ?, player_id = ? WHERE id = ?",
        (bet_amount, player_id, bet_id),
    )
    conn.commit()
    conn.close()

# 배팅 내역 삭제
def delete_bet(bet_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM bet WHERE id = ?", (bet_id,))
    conn.commit()
    conn.close()

# Streamlit UI
st.title("🔧 게임, 선수 및 배팅 정보 수정/삭제")

game_numbers = get_game_numbers()
if game_numbers:
    selected_game = st.selectbox("게임 번호 선택", game_numbers)

    # 게임 삭제
    if st.button("게임 삭제"):
        delete_game(selected_game)
        st.success(f"게임 {selected_game}과 관련된 모든 정보가 삭제되었습니다.")

    # 선수 수정 및 삭제
    st.header("선수 수정/삭제")
    players = get_players(selected_game)
    for _, row in players.iterrows():
        with st.expander(f"{row['player_name']} 선수 정보 수정"):
            player_name = st.text_input(f"선수 이름 ({row['player_name']})", value=row['player_name'])
            odds = st.number_input(f"배당률 ({row['odds']})", value=row['odds'], step=0.1)
            remarks = st.text_area(f"특이사항 ({row['remarks']})", value=row['remarks'])
            
            if st.button(f"수정: {row['player_name']}"):
                update_player(row['id'], player_name, odds, remarks)
                st.success(f"{player_name} 선수 정보가 수정되었습니다.")
            
            if st.button(f"삭제: {row['player_name']}"):
                delete_player(row['id'])
                st.success(f"{row['player_name']} 선수가 삭제되었습니다.")

    # 배팅 내역 수정 및 삭제
    st.header("배팅 내역 수정/삭제")
    bets = get_bets(selected_game)
    for _, row in bets.iterrows():
        with st.expander(f"{row['bettor_name']}의 배팅 내역 수정"):
            bet_amount = st.number_input(f"배팅 금액 ({row['bet_amount']})", value=row['bet_amount'], step=1000)
            selected_player = st.selectbox(f"배팅한 선수", get_players(selected_game)["player_name"].tolist(), index=get_players(selected_game)["id"].tolist().index(row['player_id']))
            
            if st.button(f"수정: {row['bettor_name']} 배팅"):
                player_id = get_players(selected_game).loc[get_players(selected_game)["player_name"] == selected_player, "id"].values[0]
                update_bet(row['id'], bet_amount, player_id)
                st.success(f"{row['bettor_name']}님의 배팅 내역이 수정되었습니다.")
            
            if st.button(f"삭제: {row['bettor_name']} 배팅"):
                delete_bet(row['id'])
                st.success(f"{row['bettor_name']}님의 배팅 내역이 삭제되었습니다.")
else:
    st.warning("등록된 게임이 없습니다.")
