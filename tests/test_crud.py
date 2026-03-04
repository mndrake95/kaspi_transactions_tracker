import pytest
import datetime
from database.crud import create_upload, insert_transaction

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
