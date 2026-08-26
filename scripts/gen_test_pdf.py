# Regenerates sample/kaspi_test_statement.pdf (the CI test fixture).
# Requires: pip install fpdf2, and a Cyrillic-capable TTF font (path below is Windows-specific).
from fpdf import FPDF

pdf = FPDF()
pdf.add_page()
pdf.add_font("Arial", "", "C:/Windows/Fonts/arial.ttf")
pdf.set_font("Arial", size=10)

lines = [
    "Kaspi Gold - Test Statement",
    "01.01.26 - 31.03.26",
    "",
    "Дата Сумма Операция Детали",
    "15.01.26 - 1 500,00 \u20b8 Покупка ТОО Magnum Cash&Carry",
    "20.01.26 - 500,00 \u20b8 Покупка YANDEX.GO",
    "25.01.26 + 5 000,00 \u20b8 Пополнение Иван И.",
    "05.02.26 - 2 000,00 \u20b8 Покупка ТОО Small Coffee",
    "10.02.26 + 3 000,00 \u20b8 Перевод Петр П.",
]
for line in lines:
    pdf.cell(0, 8, text=line, new_x="LMARGIN", new_y="NEXT")

pdf.output("sample/kaspi_test_statement.pdf")
print("written")
