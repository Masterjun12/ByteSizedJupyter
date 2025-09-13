import sqlite3

DB_PATH = "game_bet_all.db"

# game_bet.db 데이터베이스 생성 및 테이블 생성
def create_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # game 테이블 생성 (게임 정보만 관리)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS game (
        game_number INTEGER PRIMARY KEY
    )
    ''')

    # player 테이블 생성 (경기별 선수 정보 저장)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS player (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        game_number INTEGER,
        player_name TEXT,
        odds REAL,
        remarks REAL,
        FOREIGN KEY(game_number) REFERENCES game(game_number) ON DELETE CASCADE
    )
    ''')

    # bet 테이블 생성
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS bet (
        game_number INTEGER,
        bettor_name TEXT,
        bet_amount REAL,
        player_id INTEGER,
        payout_amount REAL DEFAULT 0,
        result TEXT DEFAULT NULL,
        FOREIGN KEY(game_number) REFERENCES game(game_number) ON DELETE CASCADE,
        FOREIGN KEY(player_id) REFERENCES player(id) ON DELETE CASCADE
    )
    ''')

    # 커밋 및 연결 종료
    conn.commit()
    conn.close()
    print("✅ game_bet.db 데이터베이스 및 테이블 생성 완료!")

# 함수 실행
if __name__ == "__main__":
    create_database()
