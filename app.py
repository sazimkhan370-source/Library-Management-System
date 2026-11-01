"""
Library Management System - Flask backend
-----------------------------------------
Serves the frontend (static/index.html) and a small JSON API
backed by an SQLite database file (library.db, created automatically).

API endpoints
    GET    /api/books                 -> list books (optional ?q=search text)
    POST   /api/books                 -> add a new book
    PUT    /api/books/<id>/issue      -> mark a book as Issued
    PUT    /api/books/<id>/return     -> mark a book as Available
    DELETE /api/books/<id>            -> delete a book
"""
import os
import sqlite3

from flask import Flask, g, jsonify, request

app = Flask(__name__, static_folder="static", static_url_path="")

# The database file lives next to this script.
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "library.db")


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------
def get_db():
    """Open one database connection per request and reuse it."""
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row  # lets us read columns by name
    return g.db


@app.teardown_appcontext
def close_db(exception):
    """Close the connection automatically when the request ends."""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Create the books table (if missing) and add sample data on first run."""
    db = sqlite3.connect(DATABASE)
    db.execute(
        """
        CREATE TABLE IF NOT EXISTS books (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            title  TEXT NOT NULL,
            author TEXT NOT NULL,
            genre  TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Available'
        )
        """
    )
    if db.execute("SELECT COUNT(*) FROM books").fetchone()[0] == 0:
        db.executemany(
            "INSERT INTO books (title, author, genre, status) VALUES (?, ?, ?, ?)",
            [
                ("The Alchemist", "Paulo Coelho", "Fiction", "Available"),
                ("Wings of Fire", "A. P. J. Abdul Kalam", "Autobiography", "Issued"),
                ("A Brief History of Time", "Stephen Hawking", "Science", "Available"),
                ("Train to Pakistan", "Khushwant Singh", "Historical Fiction", "Available"),
            ],
        )
    db.commit()
    db.close()


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------
@app.route("/")
def home():
    """Serve the single-page frontend."""
    return app.send_static_file("index.html")


@app.route("/api/books", methods=["GET"])
def list_books():
    """Return all books. If ?q=text is given, match title OR author."""
    q = request.args.get("q", "").strip()
    db = get_db()
    if q:
        like = f"%{q}%"
        rows = db.execute(
            "SELECT * FROM books WHERE title LIKE ? OR author LIKE ? ORDER BY title",
            (like, like),
        ).fetchall()
    else:
        rows = db.execute("SELECT * FROM books ORDER BY title").fetchall()
    return jsonify([dict(r) for r in rows])


@app.route("/api/books", methods=["POST"])
def add_book():
    """Add a book. Expects JSON: {"title": ..., "author": ..., "genre": ...}"""
    data = request.get_json(silent=True) or {}
    title = str(data.get("title", "")).strip()
    author = str(data.get("author", "")).strip()
    genre = str(data.get("genre", "")).strip()

    if not (title and author and genre):
        return jsonify({"error": "Title, author and genre are all required."}), 400

    db = get_db()
    cur = db.execute(
        "INSERT INTO books (title, author, genre) VALUES (?, ?, ?)",
        (title, author, genre),
    )
    db.commit()
    book = db.execute("SELECT * FROM books WHERE id = ?", (cur.lastrowid,)).fetchone()
    return jsonify(dict(book)), 201


def change_status(book_id, required, new_status, error_message):
    """Shared logic for issue/return: check the current status, then update it."""
    db = get_db()
    book = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    if book is None:
        return jsonify({"error": "Book not found."}), 404
    if book["status"] != required:
        return jsonify({"error": error_message}), 409  # 409 = conflict
    db.execute("UPDATE books SET status = ? WHERE id = ?", (new_status, book_id))
    db.commit()
    updated = db.execute("SELECT * FROM books WHERE id = ?", (book_id,)).fetchone()
    return jsonify(dict(updated))


@app.route("/api/books/<int:book_id>/issue", methods=["PUT"])
def issue_book(book_id):
    """Available -> Issued"""
    return change_status(book_id, "Available", "Issued", "This book is already issued.")


@app.route("/api/books/<int:book_id>/return", methods=["PUT"])
def return_book(book_id):
    """Issued -> Available"""
    return change_status(book_id, "Issued", "Available", "This book is not currently issued.")


@app.route("/api/books/<int:book_id>", methods=["DELETE"])
def delete_book(book_id):
    """Remove a book permanently."""
    db = get_db()
    cur = db.execute("DELETE FROM books WHERE id = ?", (book_id,))
    db.commit()
    if cur.rowcount == 0:
        return jsonify({"error": "Book not found."}), 404
    return jsonify({"deleted": book_id})


# ---------------------------------------------------------------------------
# Start the app
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    init_db()
    app.run(debug=True)  # http://127.0.0.1:5000
