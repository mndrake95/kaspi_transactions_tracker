import os
import pdfplumber
import re
from datetime import datetime

pattern = r"(\d{2}\.\d{2}\.\d{2})\s+([+\-])\s+([\d\s]+,\d{2})\s+₸\s+(\S+)\s+(.+)"



def extract_pages(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"{filepath!r} does not exist")
    list_lines = []
    with pdfplumber.open(filepath) as pdf:
        for i in pdf.pages:
            text = i.extract_text()
            if text is None:
                continue
            lines = text.splitlines()
            list_lines.append(lines)
        return list_lines

def extract_transaction_lines(lines):
    if "Дата Сумма Операция Детали" not in lines:
        return []
    transaction_lines = lines[lines.index("Дата Сумма Операция Детали") + 1:]
    return transaction_lines

def parse_transaction_line(line):
    match = re.match(pattern, line)
    if match is None:
        return None
    raw_date = match.group(1)
    sign = match.group(2)
    raw_amount = match.group(3)
    category = match.group(4)
    description = match.group(5)
    date = parse_date(raw_date)
    amount = parse_amount(raw_amount,sign)
    return {"date": date, 
            "description": description,
            "category": category,
            "amount": amount}
    
def filter_transaction_lines(lines):
    return [result for line in lines if (result := parse_transaction_line(line)) is not None]

def parse_date(raw_date):
    date = datetime.strptime(raw_date, "%d.%m.%y").strftime("%Y-%m-%d")
    return date

def parse_amount(raw_amount, sign):
    amount = float(raw_amount.replace(" ", "").replace(",", "."))
    if sign == "-":
        amount = amount * -1
    return amount

def parse_kaspi_pdf(filepath):
    pages = extract_pages(filepath)
    transactions = []
    for page in pages: 
        lines = extract_transaction_lines(page)
        transactions.extend(filter_transaction_lines(lines))

    return transactions