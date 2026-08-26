from sqlalchemy import extract
from sqlalchemy.orm import Session

from database.models import Transaction


def filter_transactions(db: Session, month: str = None, type: str = None):
    query = db.query(Transaction)
    if month:
        try:
            year, mo = month.split("-")
            query = query.filter(
                extract("year", Transaction.date) == int(year),
                extract("month", Transaction.date) == int(mo),
            )
        except (ValueError, AttributeError):
            pass
    if type:
        query = query.filter(Transaction.type == type)
    return query.all()


def calculate_total(transactions):
    return sum(t["amount"] for t in transactions)


def group_by_category(transactions):
    result = {}
    for t in transactions:
        result[t["category"]] = result.get(t["category"], 0) + t["amount"]
    return result


def group_by_month(transactions):
    result = {}
    for t in transactions:
        month = t["date"][:7]
        result[month] = result.get(month, 0) + t["amount"]
    return result
