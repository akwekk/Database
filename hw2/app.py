# app.py (English Version)

from flask import Flask, render_template, request, redirect, url_for, flash
import mysql.connector
from datetime import datetime, timedelta

# --- DB 연결 설정 ---
db_info = {
    'user': 'root',
    'password': '1234',
    'host': 'localhost',
    'database': 'bookdb'
}


def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_info)
        return conn
    except mysql.connector.Error as err:
        print(f"DB connecting error: {err}")
        return None


# --- Flask 앱 생성 및 설정 ---
app = Flask(__name__)
app.secret_key = 'supersecretkey'


# --- 도서(Book) 관련 기능 ---

@app.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT book_id, title, author FROM books ORDER BY book_id DESC")
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', books=books)


@app.route('/add', methods=['POST'])
def add_book():
    title = request.form['title']
    author = request.form['author']
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "INSERT INTO books (title, author) VALUES (%s, %s)"
    cursor.execute(query, (title, author))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('index'))


@app.route('/update/<int:book_id>', methods=['POST'])
def update_book(book_id):
    new_title = request.form.get(f'title_{book_id}')
    new_author = request.form.get(f'author_{book_id}')
    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE books SET title = %s, author = %s WHERE book_id = %s"
    cursor.execute(query, (new_title, new_author, book_id))
    conn.commit()
    cursor.close()
    conn.close()
    return redirect(url_for('index'))


@app.route('/delete', methods=['POST'])
def delete_books():
    selected_ids = request.form.getlist('book_ids')
    if selected_ids:
        conn = get_db_connection()
        cursor = conn.cursor()
        placeholders = ','.join(['%s'] * len(selected_ids))
        query = f"DELETE FROM books WHERE book_id IN ({placeholders})"
        cursor.execute(query, tuple(selected_ids))
        conn.commit()
        cursor.close()
        conn.close()
    return redirect(url_for('index'))


# --- 사용자(User) 관련 기능 ---

@app.route('/users', methods=['GET', 'POST'])
def users_page():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        user_name = request.form['name']
        try:
            query = "INSERT INTO users (name) VALUES (%s)"
            cursor.execute(query, (user_name,))
            conn.commit()
            flash(f"User '{user_name}' has been successfully registered.", "success")
        except Exception as e:
            flash(f"An error occurred while registering the user: {e}", "error")
    cursor.execute("SELECT user_id, name FROM users ORDER BY user_id DESC")
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('users.html', users=users)


@app.route('/users/update/<int:user_id>', methods=['POST'])
def update_user(user_id):
    new_name = request.form['name']
    if not new_name:
        flash("Name cannot be empty.", "error")
        return redirect(url_for('users_page'))

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "UPDATE users SET name = %s WHERE user_id = %s"
        cursor.execute(query, (new_name, user_id))
        conn.commit()
        flash("User name has been successfully updated.", "success")
    except Exception as e:
        flash(f"An error occurred during the update: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('users_page'))


@app.route('/users/delete/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "DELETE FROM users WHERE user_id = %s"
        cursor.execute(query, (user_id,))
        conn.commit()
        flash("User has been deleted.", "success")
    except Exception as e:
        flash(f"An error occurred during deletion. Users with checkout records cannot be deleted.", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('users_page'))


# --- 대출(Checkout) 관련 기능 ---

@app.route('/checkout', methods=['GET', 'POST'])
def checkout_book():
    if request.method == 'GET':
        return render_template('checkout.html')
    if request.method == 'POST':
        user_name = request.form['user_name']
        book_title = request.form['book_title']
        book_author = request.form['book_author']
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT book_id FROM books WHERE title = %s AND author = %s", (book_title, book_author))
            book = cursor.fetchone()
            if not book:
                flash("This book does not exist.", "error")
                return redirect(url_for('checkout_book'))

            cursor.execute("SELECT user_id FROM users WHERE name = %s", (user_name,))
            user = cursor.fetchone()
            if not user:
                cursor.execute("INSERT INTO users (name) VALUES (%s)", (user_name,))
                conn.commit()
                user_id = cursor.lastrowid
            else:
                user_id = user['user_id']

            book_id = book['book_id']
            checkout_date = datetime.now()
            return_date = checkout_date + timedelta(weeks=2)
            query = "INSERT INTO checkouts (book_id, user_id, checkout_date, return_date) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (book_id, user_id, checkout_date, return_date))
            conn.commit()
            flash("Checkout successful!", "success")
        except Exception as e:
            flash(f"An error occurred: {e}", "error")
        finally:
            cursor.close()
            conn.close()
        return redirect(url_for('checkout_status'))


@app.route('/status')
def checkout_status():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    query = """
            SELECT c.checkout_id, u.name, b.title, b.author, c.checkout_date, c.return_date
            FROM checkouts AS c
                     JOIN users AS u ON c.user_id = u.user_id
                     JOIN books AS b ON c.book_id = b.book_id
            WHERE c.return_date > NOW()
            ORDER BY c.checkout_date DESC \
            """
    cursor.execute(query)
    checkouts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('status.html', checkouts=checkouts)


@app.route('/renew/<int:checkout_id>', methods=['POST'])
def renew_book(checkout_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "UPDATE checkouts SET return_date = DATE_ADD(return_date, INTERVAL 7 DAY) WHERE checkout_id = %s"
        cursor.execute(query, (checkout_id,))
        conn.commit()
        flash("The return date has been extended by one week.", "success")
    except Exception as e:
        flash(f"An error occurred during renewal: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('checkout_status'))


@app.route('/checkout/delete/<int:checkout_id>', methods=['POST'])
def delete_checkout(checkout_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        query = "DELETE FROM checkouts WHERE checkout_id = %s"
        cursor.execute(query, (checkout_id,))
        conn.commit()
        flash("The checkout record has been successfully deleted (cancelled).", "success")
    except Exception as e:
        flash(f"An error occurred during deletion: {e}", "error")
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('checkout_status'))


# --- DB 테이블 생성 함수 ---
def create_all_tables():
    conn = None
    try:
        conn = get_db_connection()
        if conn is None: return
        cursor = conn.cursor()

        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS books
                       (
                           book_id
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
                       ) NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                           )""")
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS users
                       (
                           user_id
                           INT
                           AUTO_INCREMENT
                           PRIMARY
                           KEY,
                           name
                           VARCHAR
                       (
                           50
                       ) NOT NULL
                           )""")
        cursor.execute("""
                       CREATE TABLE IF NOT EXISTS checkouts
                       (
                           checkout_id
                           INT
                           AUTO_INCREMENT
                           PRIMARY
                           KEY,
                           book_id
                           INT
                           NOT
                           NULL,
                           user_id
                           INT
                           NOT
                           NULL,
                           checkout_date
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP,
                           return_date
                           TIMESTAMP
                           NULL,
                           FOREIGN
                           KEY
                       (
                           book_id
                       ) REFERENCES books
                       (
                           book_id
                       ), FOREIGN KEY
                       (
                           user_id
                       ) REFERENCES users
                       (
                           user_id
                       )
                           )""")

        conn.commit()
        print("✅ All tables are ready.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()


# --- 앱 실행 ---
if __name__ == '__main__':
    create_all_tables()
    app.run(debug=True)