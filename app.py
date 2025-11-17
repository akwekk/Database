from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from pymongo import MongoClient, DESCENDING  # Import DESCENDING for sorting
import os
import json
import csv
import io

# --- Flask Initialization ---
app = Flask(__name__, template_folder="templates")
# A secret_key is required for flash messages
app.secret_key = os.urandom(24)

# --- MongoDB Connection Setup ---
client = MongoClient('mongodb://localhost:27017/')
db = client["book_management_db"]  # Database name updated to 'book_management_db'
collection = db["books"]           # Collection name updated to 'books'


# --- Main Route (Handles both GET and POST) ---
@app.route('/', methods=['GET', 'POST'])
def index():
    # === POST Request Handling ===
    if request.method == 'POST':

        # 1. Check for file upload (bulk)
        if 'file' in request.files and request.files['file'].filename != '':
            file = request.files["file"]
            try:
                # CSV file processing
                if file.filename.endswith(".csv"):
                    stream = io.StringIO(file.stream.read().decode("utf-8-sig"))
                    reader = csv.DictReader(stream)
                    data = list(reader)
                    if not data:
                        raise Exception("CSV file is empty.")
                    collection.insert_many(data)
                    flash(f"CSV file successfully uploaded. {len(data)} records inserted.", "success")
                # JSON file processing
                elif file.filename.endswith(".json"):
                    data = json.load(file.stream)
                    if not isinstance(data, list):
                        raise Exception("JSON file must contain a list of objects.")
                    if not data:
                        raise Exception("JSON file is empty.")
                    collection.insert_many(data)
                    flash(f"JSON file successfully uploaded. {len(data)} records inserted.", "success")
                else:
                    flash("Invalid file type. Please upload .csv or .json file.", "error")
            except Exception as e:
                flash(f"File processing error: {e}", "error")

        # 2. If not a file upload, treat as single form entry
        # --- THIS PART IS UPDATED ---
        elif 'title' in request.form:
            title = request.form.get('title')
            author = request.form.get('author')

            if title and author:
                new_entry = {"title": title, "author": author}
                collection.insert_one(new_entry)
                flash("Book added successfully!", "success")
            else:
                flash("Title and Author are required for single entry.", "error")
        # --- END OF UPDATE ---

        # After POST processing, redirect to GET to show the new list
        return redirect(url_for('index'))

    # === GET Request Handling ===
    # --- THIS PART IS UPDATED ---
    try:
        # Sort by _id descending (most recent first)
        cursor = collection.find().sort("_id", DESCENDING)
        books = list(cursor) # Variable name changed to 'books'
    except Exception as e:
        books = [] # Variable name changed to 'books'
        flash(f"Error fetching data: {e}", "error")

    # Pass 'books' to the template
    return render_template('index.html', books=books)
    # --- END OF UPDATE ---


# === Main Program Execution ===
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)