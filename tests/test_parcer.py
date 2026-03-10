import pytest
from pathlib import Path
from parser.kaspi_parser import parse_kaspi_pdf, parse_date, parse_transaction_line, extract_pages, filter_transaction_lines, parse_amount
import re

SAMPLE_PDF = Path(__file__).parent.parent/"sample"/"gold_statement.pdf"

def test_parse_returns_transactions():
    result = parse_kaspi_pdf(SAMPLE_PDF)
    assert isinstance(result, list)
    assert len(result) > 0

def test_each_transaction_is_a_dict():
    result = parse_kaspi_pdf(SAMPLE_PDF)
    for i in result:
        assert isinstance(i, dict)
        assert "date" in i
        assert "description" in i
        assert "category" in i
        assert "amount" in i

def test_transaction_fields_have_correct_types():
    result = parse_kaspi_pdf(SAMPLE_PDF)
    for item in result:
        assert isinstance(item["amount"], float)
        assert re.match(r"\d{4}-\d{2}-\d{2}", item["date"])
        assert len(item["description"]) > 0

def test_missing_file_raises_error():
    with pytest.raises(FileNotFoundError):
        parse_kaspi_pdf("nonexistent.pdf")

def test_cyrillic_description_are_readable():
    result = parse_kaspi_pdf(SAMPLE_PDF)
    description = [t["description"] for t in result]
    assert any("ТОО" in d for d in description)

def test_parse_date():
    result = parse_date("03.03.26")
    assert result == "2026-03-03"

def test_parse_transaction_line():
    result = parse_transaction_line("03.03.26 - 1 500,00 ₸ Покупка Some Store")
    assert isinstance(result, dict)
    assert result["date"] == "2026-03-03"
    assert result["description"] == "Some Store"
    assert result["category"] == "Покупка"
    assert result["amount"] == -1500.0

def test_extract_pages():
    result = extract_pages(SAMPLE_PDF)
    assert isinstance(result, list)
    assert len(result) > 0
    assert all(isinstance(item, list) for item in result)

def test_filter_transaction_lines():
    result = filter_transaction_lines(["03.03.26 - 1 500,00 ₸ Покупка Some Store", "random text", "Дата Сумма Операция"])
    assert len(result) == 1
    assert result[0]["amount"] == -1500.0
    assert result[0]["category"] == "Покупка"
    
def test_parse_transaction_line():
    result = parse_transaction_line("random text")
    assert result is None

def test_parse_amount_positive():
    result = parse_amount("1 500,00", "+")
    assert result == 1500.0

def test_parse_amount_negative():
    result = parse_amount("1 500,00", "-")
    assert result == -1500.0

def test_extract_pages_missing_file():
    with pytest.raises(FileNotFoundError):
        extract_pages("nonexistent.pdf")