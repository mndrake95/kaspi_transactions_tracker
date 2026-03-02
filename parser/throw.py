import os
import pdfplumber

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
pdf_path = os.path.join(BASE, "sample", "gold_statement.pdf")

if not os.path.exists(pdf_path):
    raise FileNotFoundError(f"{pdf_path!r} does not exist")

with pdfplumber.open(pdf_path) as pdf:
    first_page = pdf.pages[0]
    print(first_page.extract_text())
    #print(first_page.extract_words())
    #print(first_page.extract_tables())
