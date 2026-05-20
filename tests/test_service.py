import pytest
from services.transaction_service import (
    filter_by_month,
    filter_by_category,
    calculate_total,
    group_by_category,
    group_by_month,
)

TRANSACTIONS = [
    {"date": "2024-01-15", "description": "Burger King", "category": "Покупка", "amount": -1500.0},
    {"date": "2024-01-20", "description": "Yandex Go", "category": "Покупка", "amount": -500.0},
    {"date": "2024-02-05", "description": "Salary", "category": "Пополнение", "amount": 5000.0},
    {"date": "2024-02-10", "description": "Magnum", "category": "Покупка", "amount": -2000.0},
]


def test_filter_by_month_returns_january_only():
    result = filter_by_month(TRANSACTIONS, "2024-01")
    assert len(result) == 2
    assert all(t["date"].startswith("2024-01") for t in result)


def test_filter_by_month_returns_february_only():
    result = filter_by_month(TRANSACTIONS, "2024-02")
    assert len(result) == 2
    assert all(t["date"].startswith("2024-02") for t in result)


def test_filter_by_month_returns_empty_for_missing_month():
    result = filter_by_month(TRANSACTIONS, "2025-01")
    assert result == []


def test_filter_by_category_returns_pokupka():
    result = filter_by_category(TRANSACTIONS, "Покупка")
    assert len(result) == 3
    assert all(t["category"] == "Покупка" for t in result)


def test_filter_by_category_returns_popolnenie():
    result = filter_by_category(TRANSACTIONS, "Пополнение")
    assert len(result) == 1
    assert result[0]["description"] == "Salary"


def test_filter_by_category_returns_empty_for_missing_category():
    result = filter_by_category(TRANSACTIONS, "NonExistent")
    assert result == []


def test_calculate_total_sums_all_amounts():
    result = calculate_total(TRANSACTIONS)
    assert result == pytest.approx(1000.0)


def test_calculate_total_empty_list_returns_zero():
    result = calculate_total([])
    assert result == 0.0


def test_group_by_category_returns_correct_dict():
    result = group_by_category(TRANSACTIONS)
    assert result == pytest.approx({"Покупка": -4000.0, "Пополнение": 5000.0})


def test_group_by_category_empty_list_returns_empty_dict():
    result = group_by_category([])
    assert result == {}


def test_group_by_month_returns_correct_dict():
    result = group_by_month(TRANSACTIONS)
    assert result == pytest.approx({"2024-01": -2000.0, "2024-02": 3000.0})


def test_group_by_month_empty_list_returns_empty_dict():
    result = group_by_month([])
    assert result == {}
