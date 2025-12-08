# init_db.py

from db_config import get_db_connection


def create_table():
    """'books' 테이블을 생성하는 함수"""
    conn = None
    try:
        conn = get_db_connection()
        if conn is None:
            print("check db_config")
            return

        cursor = conn.cursor()

        # 'books' 테이블이 없으면 생성
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS books
                       (
                           id
                           INT
                           AUTO_INCREMENT
                           PRIMARY
                           KEY,
                           title
                           VARCHAR
                       (
                           255
                       ) NOT NULL,
                           author VARCHAR
                       (
                           255
                       ) NOT NULL,
                           created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                           )
                       """)
        conn.commit()
        print("✅ 'books' table ready")

    except Exception as e:
        print(f"error arises {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


if __name__ == '__main__':
    create_table()
