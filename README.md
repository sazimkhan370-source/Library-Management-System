# Library Management System

A simple, beginner-friendly mini-project to manage a library catalog.
Built with **Flask (Python)**, **SQLite**, and **HTML / CSS / Vanilla JavaScript**.

## Features

- View all books (Title, Author, Genre, Status: Available / Issued)
- Add a new book
- Search books by title or author
- Issue and return a book
- Delete a book

## Tech Stack

| Part     | Technology                          |
|----------|-------------------------------------|
| Backend  | Python, Flask                       |
| Database | SQLite (created automatically)      |
| Frontend | HTML5, CSS3, JavaScript (Fetch API) |

## Project Structure

```
library-management/
├── app.py              # Flask backend and API routes
├── requirements.txt    # Python dependencies
├── README.md
└── static/
    ├── index.html      # Page structure
    ├── style.css       # Styling (responsive)
    └── app.js          # Frontend logic (fetch calls)
```

## How to Run

1. Install Python 3.8 or newer.
2. Clone or download this repository and open a terminal in the project folder.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the server:
   ```bash
   python app.py
   ```
5. Open http://127.0.0.1:5000 in your browser.

The database file `library.db` is created automatically on the first run with a few sample books.

## API Endpoints

| Method | URL                        | Description                                  |
|--------|----------------------------|----------------------------------------------|
| GET    | `/api/books`               | List all books (use `?q=text` to search)     |
| POST   | `/api/books`               | Add a book (`title`, `author`, `genre`)      |
| PUT    | `/api/books/<id>/issue`    | Mark a book as Issued                        |
| PUT    | `/api/books/<id>/return`   | Mark a book as Available                     |
| DELETE | `/api/books/<id>`          | Delete a book                                |

## Future Ideas

- Edit book details
- Track who borrowed a book and the due date
- Librarian login
