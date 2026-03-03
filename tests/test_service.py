import pytest
from pathlib import Path
from services.transaction_service import filter_by_month, filter_by_category, calculate_total, get_totals_by_category, get_totals_by_month

transactions = [
    {"date": "2024-01-15", "description": "ONAY.KZ", "category": "Покупка", "amount": -1000.0},
    {"date": "2024-01-20", "description": "Анна К.", "category": "Пополнение", "amount": 5000.0},
    {"date": "2024-02-05", "description": "YANDEX.GO", "category": "Покупка", "amount": -500.0},
]

def test_filter_by_month():
    filter = filter_by_month(transactions, "2024-01")
    assert len(filter) == 2

def test_filter_by_category():
    filter = filter_by_category(transactions, "Покупка")
    assert len(filter) == 2

def test_calculate_total():
    result = calculate_total(transactions)
    assert result == sum(t["amount"] for t in transactions)

def test_calculate_total_empty():
    result = calculate_total([])
    assert result == 0.0

def test_get_totals_by_category():
    result = get_totals_by_category(transactions)
    sum_result = sum(result.values())
    assert sum_result == sum(t["amount"] for t in transactions)

def test_get_totals_by_month():
    result = get_totals_by_month(transactions)
    sum_result = sum(result.values())
    assert sum_result == sum(t["amount"] for t in transactions)