from datetime import date

import pytest
from services.transaction_service import (
    calculate_total,
    filter_transactions,
    group_by_category,
    group_by_month,
)
from database.models import Upload, Transaction

TRANSACTIONS = [
    {"date": "2024-01-15", "description": "Burger King", "category": "Покупка", "amount": -1500.0},
    {"date": "2024-01-20", "description": "Yandex Go", "category": "Покупка", "amount": -500.0},
    {"date": "2024-02-05", "description": "Salary", "category": "Пополнение", "amount": 5000.0},
    {"date": "2024-02-10", "description": "Magnum", "category": "Покупка", "amount": -2000.0},
]


@pytest.fixture
def seeded_transactions(session):
    upload = Upload(filename="test.pdf", period_start=date(2024, 1, 1), period_end=date(2024, 2, 28))
    session.add(upload)
    session.commit()
    session.refresh(upload)

    txs = [
        Transaction(upload_id=upload.id, date=date(2024, 1, 15), type="Покупка", description="Burger King", amount=-1500.0),
        Transaction(upload_id=upload.id, date=date(2024, 1, 20), type="Покупка", description="Yandex Go", amount=-500.0),
        Transaction(upload_id=upload.id, date=date(2024, 2, 5), type="Пополнение", description="Salary", amount=5000.0),
        Transaction(upload_id=upload.id, date=date(2024, 2, 10), type="Покупка", description="Magnum", amount=-2000.0),
    ]
    session.add_all(txs)
    session.commit()
    return txs


def test_filter_transactions_no_filters_returns_all(session, seeded_transactions):
    result = filter_transactions(session)
    assert len(result) == 4


def test_filter_transactions_by_month_returns_january_only(session, seeded_transactions):
    result = filter_transactions(session, month="2024-01")
    assert len(result) == 2
    assert all(t.date.strftime("%Y-%m") == "2024-01" for t in result)


def test_filter_transactions_by_month_returns_empty_for_missing_month(session, seeded_transactions):
    result = filter_transactions(session, month="2025-01")
    assert result == []


def test_filter_transactions_by_type_returns_popolnenie(session, seeded_transactions):
    result = filter_transactions(session, type="Пополнение")
    assert len(result) == 1
    assert result[0].description == "Salary"


def test_filter_transactions_by_month_and_type_combined(session, seeded_transactions):
    result = filter_transactions(session, month="2024-01", type="Покупка")
    assert len(result) == 2


def test_filter_transactions_invalid_month_format_ignored(session, seeded_transactions):
    result = filter_transactions(session, month="not-a-month")
    assert len(result) == 4


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
