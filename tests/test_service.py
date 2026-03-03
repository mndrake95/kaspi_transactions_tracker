import pytest
from pathlib import Path
from parser.kaspi_parser import parse_kaspi_pdf
from services.transaction_service import filter_by_month
transactions = [
    {"date": "2024-01-15", "description": "ONAY.KZ", "category": "Покупка", "amount": -1000.0},
    {"date": "2024-01-20", "description": "Анна К.", "category": "Пополнение", "amount": 5000.0},
    {"date": "2024-02-05", "description": "YANDEX.GO", "category": "Покупка", "amount": -500.0},

]

def test_filter_by_month():
    filter = filter_by_month(transactions, "2024-01")
    assert len(filter) == 2