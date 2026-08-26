import os
import tempfile
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, Depends, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, field_validator
from sqlalchemy.orm import Session

from database.crud import create_transactions, create_upload, update_category, create_rule
from database.models import Transaction, CategoryRule
from database.session import Base, engine, get_db
from parser.kaspi_parser import parse_kaspi_pdf
from services.transaction_service import group_by_month, group_by_category, filter_transactions, calculate_total

app = FastAPI()

Base.metadata.create_all(bind=engine)


class TransactionOut(BaseModel):
    model_config = {"from_attributes": True}
    id: int
    upload_id: int
    date: str
    type: str
    description: str
    category: Optional[str]
    amount: float

    @field_validator("date", mode="before")
    @classmethod
    def coerce_date(cls, v):
        return str(v)


@app.post("/upload", response_model=list[TransactionOut])
async def upload_pdf(file: UploadFile, db: Session = Depends(get_db)):
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are accepted")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        transactions = parse_kaspi_pdf(tmp_path)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=400, detail="Could not parse PDF")
    finally:
        os.unlink(tmp_path)

    if not transactions:
        raise HTTPException(status_code=400, detail="No transactions found in PDF")

    dates = [datetime.strptime(t["date"], "%Y-%m-%d").date() for t in transactions]
    upload = create_upload(db, file.filename, min(dates), max(dates))
    saved = create_transactions(db, upload.id, transactions)
    return saved


@app.get("/transactions", response_model=list[TransactionOut])
def get_transactions(
    month: str = None,
    type: str = None,
    db: Session = Depends(get_db),
):
    return filter_transactions(db, month=month, type=type)


class CategoryUpdate(BaseModel):
    category: Optional[str] = None


class RuleCreate(BaseModel):
    keyword: str
    category: str


@app.patch("/transactions/{transaction_id}", response_model=TransactionOut)
def patch_transaction(
    transaction_id: int,
    body: CategoryUpdate,
    db: Session = Depends(get_db),
):
    tx = update_category(db, transaction_id, body.category)
    if tx is None:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return tx


@app.get("/analytics")
def get_analytics(month: str = None, type: str = None, db: Session = Depends(get_db)):
    txs = [
        {
            "id": tx.id,
            "upload_id": tx.upload_id,
            "date": str(tx.date),
            "type": tx.type,
            "description": tx.description,
            "category": tx.category,
            "amount": tx.amount,
        }
        for tx in filter_transactions(db, month=month, type=type)
    ]
    by_type: dict = {}
    for t in txs:
        by_type[t["type"]] = by_type.get(t["type"], 0.0) + t["amount"]
    return {
        "by_type": by_type,
        "by_category": group_by_category(txs),
        "by_month": group_by_month(txs),
        "total": calculate_total(txs),
    }


@app.get("/rules")
def get_rules(db: Session = Depends(get_db)):
    rules = db.query(CategoryRule).all()
    return [{"id": r.id, "keyword": r.keyword, "category": r.category} for r in rules]


@app.post("/rules", status_code=201)
def post_rule(body: RuleCreate, db: Session = Depends(get_db)):
    rule = create_rule(db, body.keyword, body.category)
    return {"id": rule.id, "keyword": rule.keyword, "category": rule.category}


@app.delete("/rules/{rule_id}")
def delete_rule(rule_id: int, db: Session = Depends(get_db)):
    rule = db.query(CategoryRule).filter(CategoryRule.id == rule_id).first()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")
    db.delete(rule)
    db.commit()
    return {"deleted": rule_id}


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
