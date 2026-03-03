


def filter_by_month(transactions, month):
    result = [t for t in transactions if t["date"].startswith(month)]
    return result

def filter_by_category(transactions, category):
    result = [t for t in transactions if t["category"].startswith(category)]
    return result