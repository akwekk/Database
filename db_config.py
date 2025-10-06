# db_config.py

import mysql.connector

# ⚠️ 본인의 DB 환경에 맞게 수정하세요.
db_info = {
    'user': 'root',
    'password': '1234',
    'host': 'localhost',
    'database': 'testdb'
}

def get_db_connection():
    """데이터베이스 커넥션 객체를 반환하는 함수"""
    try:
        conn = mysql.connector.connect(**db_info)
        return conn
    except mysql.connector.Error as err:
        print(f"DB 연결 오류: {err}")
        return None