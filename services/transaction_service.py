from parser.kaspi_parser import parse_kaspi_pdf

BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
pdf_path = os.path.join(BASE, "sample", "gold_statement.pdf")

transactions = parse_kaspi_pdf(pdf_path)

def filter_by_month(transactions, month):
    return []