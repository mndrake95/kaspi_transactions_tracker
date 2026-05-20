import pytest
import datetime
from database.crud import create_upload, insert_transaction, create_rule, create_transactions, update_category
from sqlalchemy import func, select
from database.models import Transaction

def test_create_upload(session):
    response = create_upload(session, 
                             "test.pdf", 
                             datetime.date(2026, 2, 28), 
                             datetime.date(2026, 3, 2
                                           ))

    assert isinstance(response.id, int)
    assert response.filename == "test.pdf"
    assert response.period_start == datetime.date(2026, 2, 28)
    assert response.period_end == datetime.date(2026, 3, 2)

def test_insert_transaction(session):
    fake_upload = create_upload(session, 
                             "test.pdf", 
                             datetime.date(2026, 2, 28), 
                             datetime.date(2026, 3, 2
                                           ))
    response = insert_transaction(session, 
                                  fake_upload.id,
                                  datetime.date(2026, 2, 28),
                                  "test_type",
                                  "test_description",
                                  "test_category",
                                  1000.0
                                  )
    
    assert isinstance(response.id, int)
    assert response.date == datetime.date(2026, 2, 28)
    assert response.type == "test_type"
    assert response.description == "test_description"
    assert response.category == "test_category"
    assert response.amount == 1000.0

def test_duplication_transaction(session):
    fake_upload = create_upload(session, 
                             "test.pdf", 
                             datetime.date(2026, 2, 28), 
                             datetime.date(2026, 3, 2
                                           ))
    response1 = insert_transaction(session, 
                                  fake_upload.id,
                                  datetime.date(2026, 2, 28),
                                  "test_type",
                                  "test_description",
                                  "test_category",
                                  1000.0
                                  )
    response2 = insert_transaction(session, 
                                  fake_upload.id,
                                  datetime.date(2026, 2, 28),
                                  "test_type",
                                  "test_description",
                                  "test_category",
                                  1000.0
                                  )
    query = select(func.count()).select_from(Transaction)
    duplicate = session.scalar(query)
    assert duplicate == 1


SAMPLE_TRANSACTIONS = [
    {"date": "2026-02-10", "description": "YANDEX.GO", "category": "Покупка", "amount": -500.0},
    {"date": "2026-02-15", "description": "Burger King", "category": "Покупка", "amount": -300.0},
]


def test_create_rule(session):
    rule = create_rule(session, keyword="YANDEX", category="Transport")
    assert isinstance(rule.id, int)
    assert rule.keyword == "YANDEX"
    assert rule.category == "Transport"


def test_create_transactions_bulk_insert(session):
    upload = create_upload(session, "test.pdf", datetime.date(2026, 2, 1), datetime.date(2026, 2, 28))
    result = create_transactions(session, upload.id, SAMPLE_TRANSACTIONS)
    assert len(result) == 2


def test_create_transactions_applies_category_rule(session):
    upload = create_upload(session, "test.pdf", datetime.date(2026, 2, 1), datetime.date(2026, 2, 28))
    create_rule(session, keyword="YANDEX", category="Transport")
    result = create_transactions(session, upload.id, SAMPLE_TRANSACTIONS)
    yandex_tx = next(t for t in result if t.description == "YANDEX.GO")
    assert yandex_tx.category == "Transport"


def test_create_transactions_no_rule_match_sets_category_none(session):
    upload = create_upload(session, "test.pdf", datetime.date(2026, 2, 1), datetime.date(2026, 2, 28))
    result = create_transactions(session, upload.id, SAMPLE_TRANSACTIONS)
    burger_tx = next(t for t in result if t.description == "Burger King")
    assert burger_tx.category is None


def test_create_transactions_deduplication(session):
    upload = create_upload(session, "test.pdf", datetime.date(2026, 2, 1), datetime.date(2026, 2, 28))
    result1 = create_transactions(session, upload.id, SAMPLE_TRANSACTIONS)
    result2 = create_transactions(session, upload.id, SAMPLE_TRANSACTIONS)
    assert result2[0].id == result1[0].id
    assert result2[1].id == result1[1].id


def test_rule_applied_to_existing_transaction_on_reupload(session):
    upload1 = create_upload(session, "test.pdf", datetime.date(2026, 2, 1), datetime.date(2026, 2, 28))
    create_transactions(session, upload1.id, SAMPLE_TRANSACTIONS)
    create_rule(session, keyword="YANDEX", category="Transport")
    upload2 = create_upload(session, "test2.pdf", datetime.date(2026, 2, 1), datetime.date(2026, 2, 28))
    result = create_transactions(session, upload2.id, SAMPLE_TRANSACTIONS)
    yandex_tx = next(t for t in result if t.description == "YANDEX.GO")
    assert yandex_tx.category == "Transport"


def test_update_category(session):
    upload = create_upload(session, "test.pdf", datetime.date(2026, 2, 1), datetime.date(2026, 2, 28))
    txs = create_transactions(session, upload.id, SAMPLE_TRANSACTIONS)
    updated = update_category(session, txs[0].id, "Food")
    assert updated.id == txs[0].id
    assert updated.category == "Food"


def test_insert_transaction_same_day_amount_different_type_both_saved(session):
    upload = create_upload(session, "test.pdf", datetime.date(2026, 2, 1), datetime.date(2026, 2, 28))
    tx1 = insert_transaction(session, upload.id, datetime.date(2026, 2, 10), "Покупка", "BURGER KING", None, -500.0)
    tx2 = insert_transaction(session, upload.id, datetime.date(2026, 2, 10), "Перевод", "BURGER KING", None, -500.0)
    assert tx1.id != tx2.id
