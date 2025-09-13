import streamlit as st
import sqlite3
import pandas as pd
import time

DB_PATH = "game_bet.db"

# 데이터베이스 연결 함수
def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

# 게임 정보 가져오기
def get_game_numbers():
    conn = get_connection()
    df = pd.read_sql("SELECT game_number FROM game", conn)
    conn.close()
    return df["game_number"].tolist() if not df.empty else []

# 특정 게임 정보 가져오기
def get_game_info(game_number):
    conn = get_connection()
    query = "SELECT * FROM game WHERE game_number = ?"
    df = pd.read_sql(query, conn, params=(game_number,))
    conn.close()
    return df

# 특정 게임의 배팅 내역 가져오기
def get_bet_info(game_number):
    conn = get_connection()
    query = "SELECT * FROM bet WHERE game_number = ?"
    df = pd.read_sql(query, conn, params=(game_number,))
    conn.close()
    return df

# 게임 정보 추가
def add_game(game_number, home_player, home_odds, home_remarks, away_player, away_odds, away_remarks):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    INSERT INTO game (game_number, home_player_name, home_odds, home_remarks, away_player_name, away_odds, away_remarks)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    """
    cursor.execute(query, (game_number, home_player, home_odds, home_remarks, away_player, away_odds, away_remarks))
    conn.commit()
    conn.close()

# 배팅 정보 추가
def add_bet(game_number, bettor_name, bet_amount, bet_team):
    conn = get_connection()
    cursor = conn.cursor()
    query = """
    INSERT INTO bet (game_number, bettor_name, bet_amount, bet_team, payout_amount, result)
    VALUES (?, ?, ?, ?, 0, NULL)
    """
    cursor.execute(query, (game_number, bettor_name, bet_amount, bet_team))
    conn.commit()
    conn.close()
    
# 게임 결과 업데이트 및 bet 테이블 반영
def update_game_result(game_number, result):
    conn = get_connection()
    cursor = conn.cursor()

    # 해당 경기의 모든 배팅 결과 업데이트
    cursor.execute("UPDATE bet SET result = ? WHERE game_number = ?", (result, game_number))

    conn.commit()
    conn.close()

    # 결과 업데이트 후 배당 지급금액 반영
    update_payouts(game_number)


# 배당 지급금액 업데이트
def update_payouts(game_number):
    conn = get_connection()
    cursor = conn.cursor()

    # 게임 정보 가져오기 (배당률 확인)
    query = "SELECT home_odds, away_odds FROM game WHERE game_number = ?"
    cursor.execute(query, (game_number,))
    game = cursor.fetchone()
    
    if not game:
        conn.close()
        return

    home_odds, away_odds = game

    # 배팅 정보 업데이트 (배당 지급)
    query = """
    UPDATE bet 
    SET payout_amount = 
        CASE 
            WHEN result = bet_team THEN bet_amount * (CASE WHEN bet_team = 'HOME' THEN ? ELSE ? END)
            ELSE -bet_amount
        END
    WHERE game_number = ?
    """
    cursor.execute(query, (home_odds, away_odds, game_number))

    conn.commit()
    conn.close()



# Streamlit UI
# 🔹 배너 이미지 삽입
st.image("banner.png", use_container_width=True)

st.title("🎲 게임 및 배팅 관리 시스템")

col1, col2 = st.columns(2)

# 게임 추가 (왼쪽)
with col1:
    st.header("📝 게임 정보 추가")
    game_numbers = get_game_numbers()
    latest_game_number = max(game_numbers) if game_numbers else 1
    
    with st.form("add_game_form"):
        game_number = st.number_input("게임 번호", min_value=1, step=1, value=latest_game_number)
        home_player = st.text_input("홈팀 선수")
        home_odds = st.number_input("홈팀 배당", min_value=1.0, step=0.1)
        home_remarks = st.text_area("홈팀 특이사항")

        away_player = st.text_input("어웨이팀 선수")
        away_odds = st.number_input("어웨이팀 배당", min_value=1.0, step=0.1)
        away_remarks = st.text_area("어웨이팀 특이사항")

        submitted = st.form_submit_button("게임 추가")
        if submitted:
            add_game(game_number, home_player, home_odds, home_remarks, away_player, away_odds, away_remarks)
            st.success(f"게임 {game_number}이(가) 추가되었습니다!")

# 배팅 추가 (오른쪽)
with col2:
    st.header("💰 배팅 정보 추가")
    with st.form("add_bet_form"):
        game_number_bet = st.number_input("배팅할 게임 번호", min_value=1, step=1, value=latest_game_number)
        bet_input = st.text_area("배팅 정보 입력 (닉네임/금액/배팅한 팀형식)")
        bet_submitted = st.form_submit_button("배팅 추가")
        
        if bet_submitted:
            bet_entries = bet_input.split(",")
            added_bets = []
            
            for entry in bet_entries:
                try:
                    name, amount, bet_team  = entry.strip().split("/")
                    amount = float(amount)
                    add_bet(game_number_bet, name, amount, bet_team)
                    added_bets.append(f"{name}: {amount}원, {bet_team}")
                except Exception as e:
                    st.error(f"입력 오류: {entry} (올바른 형식: 닉네임/금액/팀)")
            
            if added_bets:
                st.success("다음 배팅이 추가되었습니다:")
                st.write("\n".join(added_bets))

# 게임 및 배팅 내역 조회 버튼 추가
if st.button("📊 게임 및 배팅 내역 조회"):
    st.session_state["show_game_bet_info"] = True

if st.session_state.get("show_game_bet_info", False):
    st.write("")
    st.write("")
    st.header("📌 게임 및 배팅 내역 조회")
    game_numbers = get_game_numbers()
    
    if game_numbers:
        selected_game = st.selectbox("게임 번호 선택", game_numbers, index=len(game_numbers)-1)

        
        
        if selected_game:
            st.subheader("🏠 홈팀 정보 vs 🏆 어웨이팀 정보")
            game_info = get_game_info(selected_game).iloc[0]
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown(f"### 🏠 홈팀")
                st.info(f"**선수:** {game_info['home_player_name']}\n\n**배당:** {game_info['home_odds']}\n\n**특이사항:** {game_info['home_remarks']}")
            
            with col2:
                st.markdown(f"### 🏆 어웨이팀")
                st.info(f"**선수:** {game_info['away_player_name']}\n\n**배당:** {game_info['away_odds']}\n\n**특이사항:** {game_info['away_remarks']}")
            
            # 타이머 설정 (사용자가 입력)
            if "timer" not in st.session_state:
                st.session_state.timer = 0  # 기본값
            st.write("")
            st.write("")
            st.session_state.timer = st.number_input("⏳ 타이머 설정 (초)", min_value=1, value=10, step=1)
            
            # 타이머 시작 버튼
            if st.button("▶ 타이머 시작"):
                with st.empty():  # 타이머를 업데이트할 공간
                    for i in range(st.session_state.timer, -1, -1):
                        st.write(f"⏳ 남은 시간: **{i}초**")
                        time.sleep(1)  # 1초 대기
                        if i == 0:
                            st.balloons()  # 풍선 애니메이션!
            st.write("")
            st.write("")
            # 🏠 홈승 / 🏆 어웨이승 버튼 추가
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🏠 홈팀 승리"):
                    update_game_result(selected_game, "home")
                    st.success(f"게임 {selected_game} 결과: 홈팀 승리")
                    st.rerun()  # 새로고침

            with col2:
                if st.button("🏆 어웨이팀 승리"):
                    update_game_result(selected_game, "away")
                    st.success(f"게임 {selected_game} 결과: 어웨이팀 승리")
                    st.rerun()  # 새로고침
            st.write("")
            st.write("")
            # 배팅 내역 표시
            st.subheader("💰 배팅 내역")
            bet_info = get_bet_info(selected_game)
            if not bet_info.empty:
                bet_info['payout'] = bet_info.apply(lambda row: row['bet_amount'] * (game_info['home_odds'] if row['bet_team'] == 'home' else game_info['away_odds']), axis=1)
                bet_info['result_display'] = bet_info.apply(lambda row: f"🟢 {row['payout']}원" if row['result'] == row['bet_team'] else f"🔴 -{row['bet_amount']}원", axis=1)
                st.dataframe(bet_info[['bettor_name', 'bet_amount', 'bet_team', 'payout', 'result_display']], use_container_width=True)
            # 🔹 게임 및 배팅 수정 페이지로 이동
            if st.button("🔧 게임 및 배팅 수정 / 삭제"):
                st.session_state["selected_game"] = selected_game
                st.switch_page("pages/modify.py")

    else:
        st.warning("현재 등록된 게임이 없습니다.")


st.write("NOLBET365")
