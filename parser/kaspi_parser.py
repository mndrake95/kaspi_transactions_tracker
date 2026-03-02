import os
import pdfplumber

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
pdf_path = os.path.join(BASE, "sample", "gold_statement.pdf")

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
                transactions.append(j)

    return transactions