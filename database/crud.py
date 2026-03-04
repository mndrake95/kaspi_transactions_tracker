from database.models import Upload, Transaction

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