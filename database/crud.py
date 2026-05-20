from datetime import datetime
from database.models import Upload, Transaction, CategoryRule

def create_upload(session, filename, period_start, period_end):
    new_upload = Upload(filename=filename, period_start=period_start, period_end=period_end)
    session.add(new_upload)
    session.commit()
    session.refresh(new_upload)
    return new_upload

def insert_transaction(session, 
                       upload_id, 
                       date, 
                       type, 
                       description, 
                       category, 
                       amount
                       ):
    query = session.query(Transaction).filter(Transaction.date == date, 
                                              Transaction.description == description, 
                                              Transaction.amount == amount)
    existing = query.first()

    if existing:
        return existing
    
    else:
        new_transaction = Transaction(upload_id=upload_id,
                                  date=date,
                                  type=type,
                                  description=description,
                                  category=category,
                                  amount=amount)
        session.add(new_transaction)
        session.commit()
        session.refresh(new_transaction)
        return new_transaction


def create_rule(session, keyword, category):
    rule = CategoryRule(keyword=keyword, category=category)
    session.add(rule)
    session.commit()
    session.refresh(rule)
    return rule


def create_transactions(session, upload_id, transactions):
    rules = session.query(CategoryRule).all()
    seen_ids = set()
    result = []
    for t in transactions:
        date = datetime.strptime(t["date"], "%Y-%m-%d").date()
        category = None
        for rule in rules:
            if rule.keyword in t["description"]:
                category = rule.category
                break
        tx = insert_transaction(
            session,
            upload_id=upload_id,
            date=date,
            type=t["category"],
            description=t["description"],
            category=category,
            amount=t["amount"],
        )
        if tx.id not in seen_ids:
            seen_ids.add(tx.id)
            result.append(tx)
    return result


def update_category(session, transaction_id, category):
    tx = session.query(Transaction).filter(Transaction.id == transaction_id).first()
    if tx is None:
        return None
    tx.category = category
    session.commit()
    session.refresh(tx)
    return tx