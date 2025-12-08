# routes/book_routes.py

from flask import Blueprint, request, redirect, url_for, render_template
from db_config import get_db_connection

# Create a blueprint named 'books'
book_bp = Blueprint('books', __name__)


# Main page and book list view (Read)
@book_bp.route('/')
def index():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, title, author FROM books ORDER BY id DESC")
    books = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('index.html', books=books)


# Add a new book (Create)
@book_bp.route('/add', methods=['POST'])
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

    return redirect(url_for('books.index'))


# Update book information (Update)
@book_bp.route('/update/<int:book_id>', methods=['POST'])
def update_book(book_id):
    # Use f-string as each input field name is formatted like 'title_1', 'author_1', etc.
    new_title = request.form.get(f'title_{book_id}')
    new_author = request.form.get(f'author_{book_id}')

    conn = get_db_connection()
    cursor = conn.cursor()
    query = "UPDATE books SET title = %s, author = %s WHERE id = %s"
    cursor.execute(query, (new_title, new_author, book_id))
    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('books.index'))


# Delete selected books (Delete)
@book_bp.route('/delete', methods=['POST'])
def delete_books():
    selected_ids = request.form.getlist('book_ids')

    if selected_ids:
        conn = get_db_connection()
        cursor = conn.cursor()

        # Dynamically generate placeholders (%s) for the IN clause
        placeholders = ','.join(['%s'] * len(selected_ids))
        query = f"DELETE FROM books WHERE id IN ({placeholders})"

        cursor.execute(query, tuple(selected_ids))
        conn.commit()
        cursor.close()
        conn.close()

    return redirect(url_for('books.index'))
