import streamlit as st
import sqlite3
import pandas as pd

DB_PATH = "game_bet_all.db"

# ✅ 단일 연결을 사용하도록 수정
def get_connection():
    conn = sqlite3.connect(DB_PATH, isolation_level=None)  # Auto-commit 모드
    conn.execute("PRAGMA foreign_keys = ON")  # 외래 키 활성화
    return conn

# ✅ 특정 게임의 모든 선수 결과 초기화
def reset_game_result(game_number):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE player SET result = NULL WHERE game_number = ?", (game_number,))
    conn.commit()
    conn.close()

def update_game_result(game_number, player_id, result):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("UPDATE player SET result = ? WHERE game_number = ? AND id = ?", (result, game_number, player_id))

    # 🔹 배팅 내역 업데이트
    if result == "WIN":
        cursor.execute(""" 
        UPDATE bet 
        SET result = "WIN", payout_amount = bet_amount * (SELECT odds FROM player WHERE id = ?)
        WHERE game_number = ? AND player_id = ? 
        """, (player_id, game_number, player_id))

        cursor.execute(""" 
        UPDATE bet 
        SET result = "LOSE", payout_amount = -bet_amount
        WHERE game_number = ? AND player_id != ? 
        """, (game_number, player_id))

    elif result == "LOSE":
        cursor.execute("UPDATE bet SET result = 'LOSE', payout_amount = -bet_amount WHERE game_number = ? AND player_id = ?", (game_number, player_id))

    conn.commit()
    conn.close()

# ✅ UI 부분
st.title("📊 게임 및 배팅 내역 조회")

# 🔹 게임 목록 가져오기
conn = get_connection()
game_numbers = pd.read_sql("SELECT game_number FROM game", conn)["game_number"].tolist()
conn.close()

if game_numbers:
    selected_game = st.selectbox("게임 번호 선택", game_numbers, index=len(game_numbers) - 1)

    if selected_game:
        conn = get_connection()
        players = pd.read_sql("SELECT * FROM player WHERE game_number = ?", conn, params=[selected_game])
        bets = pd.read_sql("SELECT * FROM bet WHERE game_number = ?", conn, params=[selected_game])
        conn.close()

        if players.empty:
            st.warning(f"⚠️ 이 게임에는 선수가 없습니다.")
        
        if not players.empty:
            st.subheader("🏆 선수 정보")
            cols = st.columns(len(players))

            # 각 선수의 결과를 저장할 딕셔너리
            player_results = {}

            for i, row in players.iterrows():
                with cols[i]:
                    st.info(f"**선수:** {row['player_name']}\n\n**배당:** {row['odds']}\n\n**특이사항:** {row['remarks']}")

                    # 🔹 WIN/LOSE 콤보박스
                    result = st.selectbox(f"{row['player_name']}의 결과", ["WIN", "LOSE"], key=f"result_{row['id']}", index=0 if row['result'] is None else ["WIN", "LOSE"].index(row['result']))

                    # 선수의 결과를 딕셔너리에 저장
                    player_results[row['id']] = result

                    # 자동으로 DB에 저장 (선택 후 즉시 저장)
                    update_game_result(selected_game, row['id'], result)

            st.success("모든 선수의 결과가 자동으로 업데이트되었습니다.")

            # 🔹 결과 초기화 버튼
            if st.button("🔄 결과 초기화"):
                reset_game_result(selected_game)
                st.success("모든 선수의 결과가 초기화되었습니다.")
                st.rerun()

        # 🔹 배팅 내역이 없을 때
        if bets.empty:
            st.warning(f"⚠️ 이 게임에는 배팅 내역이 없습니다.")
        elif not bets.empty:
            st.subheader("💰 배팅 내역")
            bet_details = []

            for index, bet in bets.iterrows():
                # player_id와 players 테이블의 id를 기준으로 선수를 찾음
                player_row = players.loc[players['player_name'] == bet['player_id']]

                if player_row.empty:
                    st.warning(f"⚠️ 배팅 내역에 해당 선수 정보가 없습니다. 배팅자 ID: {bet['bettor_name']}")
                    continue

                player_name = player_row['player_name'].values[0]
                player_result = player_row['result'].values[0]  # 선수의 결과
                bet_amount = bet['bet_amount']
                payout_amount = bet['payout_amount']
                result = bet['result']

                # 선수 결과에 따른 배팅 내역 업데이트
                if player_result == "WIN":
                    result = "WIN"
                    payout_amount = bet_amount * player_row['odds'].values[0]  # 배당금액 계산
                elif player_result == "LOSE":
                    result = "LOSE"
                    payout_amount = -bet_amount  # 배팅금액의 부호를 반대로 설정

                # 결과를 DB에 반영
                conn = get_connection()
                cursor = conn.cursor()
                cursor.execute(""" 
                UPDATE bet 
                SET result = ?, payout_amount = ? 
                WHERE game_number = ? AND player_id = ? 
                """, (result, payout_amount, selected_game, bet['player_id']))
                conn.commit()
                conn.close()

                # 배팅자, 배팅금액, 배팅선수, 결과만 출력
                if result == "WIN":
                    result_display = f"🟢 {payout_amount:,.0f}원"
                elif result == "LOSE":
                    result_display = f"🔴 -{bet_amount:,.0f}원"
                else:
                    result_display = "❓ 미정"

                bet_details.append([bet['bettor_name'], f"{bet_amount:,.0f}원", player_name, result_display])

            # st.dataframe을 사용하여 테이블 출력
            bet_df = pd.DataFrame(bet_details, columns=["배팅자 닉네임", "배팅금액", "배팅선수", "결과"])
            st.dataframe(bet_df)

else:
    st.warning(f"⚠️ 등록된 게임이 없습니다.")
if st.button("🔧 게임 및 배팅 수정 / 삭제"):
    st.switch_page("modify")