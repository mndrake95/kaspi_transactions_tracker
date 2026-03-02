# Kaspi PDF Tracker — Implementation Plan

> **Mentoring mode:** This plan gives hints and direction. You write all code yourself.
> **TDD cycle:** RED (write failing test) → GREEN (minimal code to pass) → REFACTOR (clean up)

**Goal:** Parse Kaspi bank PDF statements and display transactions in a filtered web UI.

**Architecture:** Layered — parser → service → API → frontend. Each layer tested in isolation.

**Tech Stack:** Python 3, pdfplumber, FastAPI, pytest, Vanilla HTML/JS

---

## Phase 0: Project Setup

### Task 0.1: Create folder structure

Create these folders and empty `__init__.py` files:
```
kaspi-pdf-tracker/
├── parser/
├── services/
├── api/
├── frontend/
├── tests/
└── sample/        ← put your Kaspi PDF here
```

Hint: `__init__.py` is what makes a folder a Python package. It can be completely empty.

### Task 0.2: Create requirements.txt

You need these packages:
- `pdfplumber` — PDF text extraction
- `fastapi` — web framework
- `uvicorn` — ASGI server to run FastAPI
- `python-multipart` — needed for file uploads in FastAPI
- `pytest` — test runner
- `httpx` — needed for FastAPI TestClient

Install them all with `pip install -r requirements.txt`.

### Task 0.3: Verify pytest works

Create `tests/test_placeholder.py` with one trivially passing test (e.g., `assert 1 == 1`).
Run `pytest` from the project root. It should find and pass that test.
Delete `test_placeholder.py` after confirming it works.

---

## Phase 1: Parser Layer

### Task 1.1: Explore your sample PDF

Before writing any tests, open your PDF with pdfplumber in a throwaway script and print the raw text.

**Hint:** `pdfplumber.open("sample/your_file.pdf")` gives you a PDF object. Each page has an `.extract_text()` method. Print the result and study it.

**Questions to answer:**
- What does one transaction line look like?
- How is the date formatted? (e.g., `15.01.2024` or `2024-01-15`?)
- Where is the amount? Is it on the same line as the description?
- What separates transactions from each other?
- Is there a "category" column or do you need to infer it?

Write down your observations — you'll need them to write tests.

### Task 1.2: Write the first failing parser test

**File:** `tests/test_parser.py`

**What to test first:** Given your real PDF file, `parse_kaspi_pdf()` should return a list with more than 0 transactions.

**Hint:** Your test needs to know where the sample PDF is. Use a relative path from the project root, or better — use `pathlib.Path(__file__).parent.parent / "sample" / "your_file.pdf"`.

**Run:** `pytest tests/test_parser.py -v`
**Expected:** FAIL — `ImportError` or `ModuleNotFoundError` (function doesn't exist yet)

### Task 1.3: Create the parser module

**File:** `parser/kaspi_parser.py`

Create a function `parse_kaspi_pdf(filepath: str) -> list[dict]`.
For now, make it return an empty list `[]` — just enough to import without crashing.

**Run:** `pytest tests/test_parser.py -v`
**Expected:** FAIL — your test asserts `len(result) > 0` but gets 0. This is correct RED state.

### Task 1.4: Implement minimal text extraction

Make `parse_kaspi_pdf` actually open the PDF and extract text.
Loop over pages, extract text lines, and try to return at least one transaction dict.

**Don't try to be perfect yet.** Get one transaction parsed correctly, make the test pass, then expand.

**Hint for parsing lines:** `str.split()`, `str.strip()`, and regex (`re` module) are your friends. Look at the raw text from Task 1.1 to figure out the pattern.

**Run:** `pytest tests/test_parser.py -v`
**Expected:** PASS

### Task 1.5: Add field validation tests

Now write more specific tests:

- Each transaction has all 4 keys: `date`, `description`, `category`, `amount`
- `amount` is a `float` (not a string)
- `date` is a string in `YYYY-MM-DD` format (use a regex or try parsing with `datetime`)
- `description` is a non-empty string

Write one test per assertion. Run after each one — RED first, then GREEN.

**Hint for date conversion:** `datetime.strptime(raw_date, "%d.%m.%Y").strftime("%Y-%m-%d")` — adjust format to match what you saw in your PDF.

### Task 1.6: Add edge case tests

- Test with a PDF that has no transactions (or an empty page) → should return `[]`, not crash
- Test that Cyrillic characters appear correctly in descriptions (not garbled)

**Hint for Cyrillic:** If you see garbled text, try `page.extract_text(x_tolerance=2)` in pdfplumber.

**Commit** when all parser tests pass.

---

## Phase 2: Service Layer

### Task 2.1: Write failing service tests

**File:** `tests/test_service.py`

At the top of this test file, define a hardcoded list of fake transactions (no PDF needed):
```
transactions = [
    {"date": "2024-01-15", "description": "...", "category": "Food", "amount": -1500.0},
    {"date": "2024-01-20", "description": "...", "category": "Transport", "amount": -500.0},
    {"date": "2024-02-05", "description": "...", "category": "Food", "amount": -2000.0},
]
```

Write tests for:
- `filter_by_month(transactions, "2024-01")` returns only January transactions (2 items)
- `filter_by_month(transactions, "2024-02")` returns only February transactions (1 item)
- `filter_by_category(transactions, "Food")` returns only Food transactions (2 items)
- `calculate_total(transactions)` returns the correct sum of all amounts
- `calculate_total([])` returns `0.0`

**Run:** FAIL — functions don't exist yet

### Task 2.2: Create the service module

**File:** `services/transaction_service.py`

Implement the three functions. Each one should be simple — a few lines max.

**Hint:** `filter_by_month` should check if the transaction's date *starts with* the given month string (e.g., `"2024-01"`).

**Run:** `pytest tests/test_service.py -v`
**Expected:** All PASS

**Commit** when done.

---

## Phase 3: API Layer

### Task 3.1: Create the FastAPI app skeleton

**File:** `api/main.py`

Create a FastAPI app instance. Don't add any routes yet.

**Hint:** `app = FastAPI()` is all you need to start.

### Task 3.2: Write the first API test

**File:** `tests/test_api.py`

**How FastAPI testing works:** You don't run a server. You create a `TestClient(app)` and call `.post()` / `.get()` on it like a regular HTTP client.

Write a test for `POST /upload`:
- Send your sample PDF as a multipart file upload
- Assert response status code is `200`
- Assert response JSON is a list
- Assert the list has more than 0 items

**Hint:** Look at FastAPI docs for `TestClient` and `UploadFile`. The test sends a file like:
```
with open("sample/your_file.pdf", "rb") as f:
    response = client.post("/upload", files={"file": f})
```

**Run:** FAIL — route doesn't exist

### Task 3.3: Implement POST /upload

Add the `/upload` endpoint to `api/main.py`.

It should:
1. Accept an `UploadFile` parameter
2. Save it temporarily (use `tempfile` module or write to a temp path)
3. Call `parse_kaspi_pdf()` from your parser
4. Return the list of transactions as JSON

**Hint:** FastAPI automatically converts a returned list of dicts to JSON. You don't need to call `json.dumps()`.

**Hint for temp file:** `import tempfile` then `tempfile.NamedTemporaryFile(suffix=".pdf", delete=False)`.

**Run:** `pytest tests/test_api.py -v`
**Expected:** PASS

### Task 3.4: Add GET /transactions with filtering

Write the test first:
- `GET /transactions` returns all transactions (need to upload first, or mock data)
- `GET /transactions?month=2024-01` returns only January
- `GET /transactions?category=Food` returns only Food

**Hint:** You'll need to store parsed transactions somewhere between requests. For now, a simple module-level list in `main.py` is fine. (Not production-ready, but fine for learning.)

**Hint:** FastAPI query params are just function parameters: `def get_transactions(month: str = None, category: str = None)`.

Write test → run (RED) → implement → run (GREEN) → commit.

### Task 3.5: Add error handling tests

Write a test:
- `POST /upload` with an empty file → should return HTTP 400 with an error message

Implement: catch the `ValueError` your parser raises and return `HTTPException(status_code=400, detail="...")`.

**Run:** RED → implement → GREEN → **commit**

---

## Phase 4: Frontend

No TDD here — this is manual testing only.

### Task 4.1: Create index.html

**File:** `frontend/index.html`

Build the page with:
- A file input (`<input type="file" accept=".pdf">`) and an upload button
- A results table (hidden by default, shown after upload)
- A category dropdown filter
- A month filter
- A "Total" display at the bottom

Use `fetch()` to call your API. No jQuery, no frameworks.

**To serve the frontend:** Add a static file route to FastAPI, or just open the HTML file directly in a browser (works fine for local dev).

### Task 4.2: Connect upload to API

Write the JS to:
1. Grab the file from the input
2. Build a `FormData` object with the file
3. `fetch("http://localhost:8000/upload", { method: "POST", body: formData })`
4. Parse the JSON response
5. Store transactions in a JS variable
6. Call a `renderTable(transactions)` function

### Task 4.3: Render the table

`renderTable(transactions)` should:
- Clear the existing table body
- Loop over transactions
- Create a `<tr>` per transaction with `<td>` for each field
- Append to the table

### Task 4.4: Add filters

On filter change (dropdown / input):
- Filter the stored transactions array with JS
- Re-call `renderTable()` with the filtered result
- Update the total display

---

## Phase 5: Polish

### Task 5.1: Error states in frontend

- Show a visible error message if the API returns non-200
- Show "No transactions found" if the result array is empty
- Disable the upload button while loading

### Task 5.2: Add a CSS framework

Pick one: Bootstrap (simpler) or Tailwind (more control).
Link it via CDN in your `index.html` — no build step needed.

### Task 5.3: Add Chart.js pie chart

Show spending by category.
Link Chart.js via CDN.
After rendering the table, aggregate amounts by category and pass to `new Chart(...)`.

---

## Running the project

```bash
# Start the backend
uvicorn api.main:app --reload

# Open frontend
# Just open frontend/index.html in your browser
# OR add static file serving to FastAPI
```

---

## Checklist before calling it done

- [ ] All pytest tests pass
- [ ] Can upload a real Kaspi PDF and see transactions
- [ ] Month filter works
- [ ] Category filter works
- [ ] Total updates when filtering
- [ ] Error message shows for bad uploads
- [ ] Chart shows category breakdown
