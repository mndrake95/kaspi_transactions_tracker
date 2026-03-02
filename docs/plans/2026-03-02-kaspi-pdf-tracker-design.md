# Kaspi PDF Tracker — Design Document
**Date:** 2026-03-02

## Overview
A local web app that parses Kaspi bank PDF statements and displays transactions with filtering by month and category.

**Stack:** Python (FastAPI) + pdfplumber + Vanilla HTML/JS

---

## Project Structure

```
kaspi-pdf-tracker/
├── parser/
│   ├── __init__.py
│   └── kaspi_parser.py         # parse_kaspi_pdf() lives here
├── services/
│   ├── __init__.py
│   └── transaction_service.py  # filtering, aggregation logic
├── api/
│   ├── __init__.py
│   └── main.py                 # FastAPI app: /upload and /transactions
├── frontend/
│   └── index.html              # Vanilla JS + HTML
├── tests/
│   ├── test_parser.py
│   ├── test_service.py
│   └── test_api.py
├── sample/                     # Sample Kaspi PDFs for testing
├── requirements.txt
└── README.md
```

---

## Data Model

Each transaction is a dict:
```python
{
    "date": "2024-01-15",       # ISO format string
    "description": "...",       # merchant/description
    "category": "...",          # spending category
    "amount": -1500.0           # negative = expense, positive = income
}
```

---

## Data Flow

```
PDF file → parser/ → list[Transaction]
                   → services/ (filter by month/category, sum totals)
                              → api/ (HTTP JSON responses)
                                    → frontend (fetch + render table + chart)
```

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/upload` | Accepts PDF, returns list of transactions as JSON |
| GET | `/transactions` | Returns transactions filtered by `?month=` and `?category=` |

---

## TDD Strategy

### Phase 1 — Parser (`tests/test_parser.py`)
- Fixture: real sample Kaspi PDF
- Test: correct number of transactions returned
- Test: each transaction has all required fields
- Test: amounts are floats, dates are valid strings
- Test: Cyrillic descriptions are decoded correctly
- Edge: empty PDF returns `[]`

### Phase 2 — Service (`tests/test_service.py`)
- Fixture: hardcoded list of fake transactions
- Test: filter_by_month returns only matching transactions
- Test: filter_by_category returns only matching transactions
- Test: calculate_total sums amounts correctly
- Test: empty list returns 0 total

### Phase 3 — API (`tests/test_api.py`)
- Uses FastAPI `TestClient` — no running server needed
- Test: POST /upload with valid PDF returns 200 + list of transactions
- Test: POST /upload with empty file returns 400
- Test: GET /transactions?month=2024-01 returns filtered results
- Test: GET /transactions?category=Food returns filtered results

### Phase 4 — Manual
- UI polish, Chart.js visualization, error message display

---

## TDD Cycle

```
RED   → write a failing test that describes what you want
GREEN → write the minimum code to make it pass
REFACTOR → clean up without breaking the test
```

---

## Error Handling

| Layer | Scenario | Behavior |
|-------|----------|----------|
| Parser | PDF is image-based (no text) | Raise `ValueError` |
| Parser | No transactions found | Return `[]` |
| Parser | Cyrillic encoding issues | Use pdfplumber x_tolerance config |
| API | Parser raises ValueError | HTTP 400 with message |
| API | No file uploaded | HTTP 422 (FastAPI auto) |
| API | Unexpected crash | HTTP 500 (FastAPI auto) |
| Frontend | Upload fails | Show error message |
| Frontend | Empty result | Show "No transactions found" |

---

## Phases (from roadmap)

1. **PDF Parsing** — `parse_kaspi_pdf()` with unit tests
2. **Backend** — FastAPI endpoints with TestClient tests
3. **Frontend** — Vanilla HTML/JS, manual testing
4. **Polish** — Error handling, Bootstrap/Tailwind, Chart.js
5. **Optional** — Rewrite backend in Go
