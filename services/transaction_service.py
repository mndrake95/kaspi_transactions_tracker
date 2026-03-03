


def filter_by_month(transactions, month):
    result = [t for t in transactions if t["date"].startswith(month)]
    return result

def filter_by_category(transactions, category):
    result = [t for t in transactions if t["category"].startswith(category)]
    return result

def calculate_total(transactions):
    result = sum(t["amount"] for t in transactions)
    return result

def get_totals_by_category(transactions):
    result = sum(t["category"] for t in transactions)