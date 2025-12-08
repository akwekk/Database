# app.py

from flask import Flask
from routes.book_routes import book_bp

app = Flask(__name__)

# Register the blueprint
app.register_blueprint(book_bp)

if __name__ == '__main__':
    # Use debug=True only during development.
    app.run(debug=True)
