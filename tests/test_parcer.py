import pytest
from pathlib import Path
from parser.kaspi_parser import parse_kaspi_pdf

SAMPLE_PDF = Path(__file__).parent.parent/"sample"/"gold_statement.pdf"

def test_parse_returns_transactions():
    result = parse_kaspi_pdf(SAMPLE_PDF)
    assert isinstance(result, list)
    assert len(result) > 0
