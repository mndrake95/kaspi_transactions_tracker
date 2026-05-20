def filter_by_month(transactions, month):
    return [t for t in transactions if t["date"].startswith(month)]


def filter_by_category(transactions, category):
    return [t for t in transactions if t["category"] == category]


def calculate_total(transactions):
    return sum(t["amount"] for t in transactions)


def group_by_category(transactions):
    result = {}
    for t in transactions:
        result[t["category"]] = result.get(t["category"], 0) + t["amount"]
    return result


def group_by_month(transactions):
    result = {}
    for t in transactions:
        month = t["date"][:7]
        result[month] = result.get(month, 0) + t["amount"]
    return result
