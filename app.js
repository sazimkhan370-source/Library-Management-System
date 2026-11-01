// Library Management System - frontend logic (vanilla JS + Fetch API)

const API = "/api/books";

const listEl = document.getElementById("book-list");
const emptyEl = document.getElementById("empty");
const statsEl = document.getElementById("stats");
const searchEl = document.getElementById("search");
const formEl = document.getElementById("add-form");
const toastEl = document.getElementById("toast");

// ---------- Small helpers ----------

/** Show a short message at the bottom of the screen. */
function showToast(message, isError = false) {
  toastEl.textContent = message;
  toastEl.className = "toast show" + (isError ? " error" : "");
  clearTimeout(showToast.timer);
  showToast.timer = setTimeout(() => (toastEl.className = "toast"), 2500);
}

/** Call the backend and return the JSON. Throws an Error with the server's message on failure. */
async function request(url, options = {}) {
  const res = await fetch(url, options);
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Something went wrong.");
  return data;
}

/** Create a <td> with text (textContent keeps user input safe from HTML injection). */
function cell(text, label, className) {
  const td = document.createElement("td");
  td.textContent = text;
  td.dataset.label = label; // used by the mobile card layout
  if (className) td.className = className;
  return td;
}

/** Create a button for the Actions column. */
function actionButton(text, className, onClick) {
  const btn = document.createElement("button");
  btn.textContent = text;
  btn.className = "btn " + className;
  btn.addEventListener("click", onClick);
  return btn;
}

// ---------- Rendering ----------

function renderBooks(books) {
  listEl.innerHTML = "";
  emptyEl.hidden = books.length > 0;

  for (const book of books) {
    const tr = document.createElement("tr");
    tr.append(
      cell(book.title, "Title", "title"),
      cell(book.author, "Author"),
      cell(book.genre, "Genre")
    );

    // Status badge
    const statusTd = document.createElement("td");
    const badge = document.createElement("span");
    badge.className = "badge " + book.status.toLowerCase();
    badge.textContent = book.status;
    statusTd.appendChild(badge);
    tr.appendChild(statusTd);

    // Action buttons: Issue or Return, plus Delete
    const actionsTd = document.createElement("td");
    actionsTd.className = "actions";
    if (book.status === "Available") {
      actionsTd.appendChild(actionButton("Issue", "", () => changeStatus(book.id, "issue")));
    } else {
      actionsTd.appendChild(actionButton("Return", "", () => changeStatus(book.id, "return")));
    }
    actionsTd.appendChild(actionButton("Delete", "btn-danger", () => deleteBook(book)));
    tr.appendChild(actionsTd);

    listEl.appendChild(tr);
  }
}

/** Update the "4 books · 3 available · 1 issued" line using the full catalog. */
async function updateStats() {
  const all = await request(API);
  const issued = all.filter((b) => b.status === "Issued").length;
  statsEl.textContent = `${all.length} books, ${all.length - issued} available, ${issued} issued`;
}

// ---------- Actions ----------

/** Fetch books (filtered by the search box) and redraw the table. */
async function loadBooks() {
  try {
    const q = searchEl.value.trim();
    const books = await request(q ? `${API}?q=${encodeURIComponent(q)}` : API);
    renderBooks(books);
    await updateStats();
  } catch (err) {
    showToast(err.message, true);
  }
}

async function changeStatus(id, action) {
  try {
    await request(`${API}/${id}/${action}`, { method: "PUT" });
    showToast(action === "issue" ? "Book issued." : "Book returned.");
    loadBooks();
  } catch (err) {
    showToast(err.message, true);
    loadBooks();
  }
}

async function deleteBook(book) {
  if (!confirm(`Delete "${book.title}"? This cannot be undone.`)) return;
  try {
    await request(`${API}/${book.id}`, { method: "DELETE" });
    showToast("Book deleted.");
    loadBooks();
  } catch (err) {
    showToast(err.message, true);
  }
}

formEl.addEventListener("submit", async (event) => {
  event.preventDefault(); // stop the page from reloading
  const body = {
    title: document.getElementById("title").value,
    author: document.getElementById("author").value,
    genre: document.getElementById("genre").value,
  };
  try {
    await request(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    formEl.reset();
    showToast("Book added.");
    loadBooks();
  } catch (err) {
    showToast(err.message, true);
  }
});

// Search as the user types, waiting 250 ms after the last keystroke.
let searchTimer;
searchEl.addEventListener("input", () => {
  clearTimeout(searchTimer);
  searchTimer = setTimeout(loadBooks, 250);
});

// First load
loadBooks();
