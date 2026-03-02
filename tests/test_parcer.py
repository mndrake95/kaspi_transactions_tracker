import pytest
from pathlib import Path
from parser.kaspi_parser import parse_kaspi_pdf

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