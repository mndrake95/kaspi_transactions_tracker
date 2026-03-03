


def filter_by_month(transactions, month):
    result = [t for t in transactions if t["date"].startswith(month)]
    return result