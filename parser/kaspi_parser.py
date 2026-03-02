import os
import pdfplumber
import re
from datetime import datetime

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
pdf_path = os.path.join(BASE, "sample", "gold_statement.pdf")

pattern = r"(\d{2}\.\d{2}\.\d{2})\s+([+\-])\s+([\d\s]+,\d{2})\s+₸\s+(\S+)\s+(.+)"

def parse_kaspi_pdf(filepath):
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"{filepath!r} does not exist")
    
    transactions = []

    with pdfplumber.open(filepath) as pdf:
        for i in pdf.pages:
            text = i.extract_text()
            lines = text.splitlines()
            if "Дата Сумма Операция Детали" not in lines:
                continue
            transaction_lines = lines[lines.index("Дата Сумма Операция Детали") + 1:]
            for j in transaction_lines:
                match = re.match(pattern, j)
                if match: 
                    raw_date = match.group(1)
                    sign = match.group(2)
                    raw_amount = match.group(3)
                    category = match.group(4)
                    description = match.group(5)
                    date = datetime.strptime(raw_date, "%d.%m.%y").strftime("%Y-%m-%d")
                    amount = float(raw_amount.replace(" ", "").replace(",", "."))
                    if sign == "-":
                        amount = amount * -1
                    transactions.append({
                        "date": date,
                        "description": description,
                        "category": category,
                        "amount": amount
                    })

    return transactions