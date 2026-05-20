import pytest
from pathlib import Path

SAMPLE_PDF = Path(__file__).parent.parent / "sample" / "gold_statement.pdf"


@pytest.fixture
def client_with_data(client):
    with open(SAMPLE_PDF, "rb") as f:
        response = client.post("/upload", files={"file": ("gold_statement.pdf", f, "application/pdf")})
    assert response.status_code == 200
    return client, response.json()


# --- POST /upload ---

def test_upload_returns_transaction_list(client):
    with open(SAMPLE_PDF, "rb") as f:
        response = client.post("/upload", files={"file": ("gold_statement.pdf", f, "application/pdf")})
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    assert len(response.json()) > 0


def test_upload_transaction_has_required_fields(client):
    with open(SAMPLE_PDF, "rb") as f:
        response = client.post("/upload", files={"file": ("gold_statement.pdf", f, "application/pdf")})
    tx = response.json()[0]
    assert "id" in tx
    assert "date" in tx
    assert "type" in tx
    assert "description" in tx
    assert "amount" in tx


# --- GET /transactions ---

def test_get_transactions_returns_all(client_with_data):
    client, uploaded = client_with_data
    response = client.get("/transactions")
    assert response.status_code == 200
    assert len(response.json()) == len(uploaded)


def test_get_transactions_filter_by_month(client_with_data):
    client, uploaded = client_with_data
    month = uploaded[0]["date"][:7]
    response = client.get(f"/transactions?month={month}")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert all(t["date"].startswith(month) for t in response.json())


def test_get_transactions_filter_by_type(client_with_data):
    client, uploaded = client_with_data
    tx_type = uploaded[0]["type"]
    response = client.get(f"/transactions?type={tx_type}")
    assert response.status_code == 200
    assert len(response.json()) > 0
    assert all(t["type"] == tx_type for t in response.json())


# --- PATCH /transactions/{id} ---

def test_patch_transaction_updates_category(client_with_data):
    client, uploaded = client_with_data
    tx_id = uploaded[0]["id"]
    response = client.patch(f"/transactions/{tx_id}", json={"category": "Food"})
    assert response.status_code == 200
    assert response.json()["category"] == "Food"
    assert response.json()["id"] == tx_id


def test_patch_transaction_not_found_returns_404(client):
    response = client.patch("/transactions/999999", json={"category": "Food"})
    assert response.status_code == 404


# --- GET /analytics ---

def test_get_analytics_has_required_keys(client_with_data):
    client, _ = client_with_data
    response = client.get("/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "by_category" in data
    assert "by_month" in data


def test_get_analytics_by_category_is_dict_of_floats(client_with_data):
    client, _ = client_with_data
    data = client.get("/analytics").json()
    assert isinstance(data["by_category"], dict)
    assert all(isinstance(v, float) for v in data["by_category"].values())


def test_get_analytics_by_month_is_dict_of_floats(client_with_data):
    client, _ = client_with_data
    data = client.get("/analytics").json()
    assert isinstance(data["by_month"], dict)
    assert all(isinstance(v, float) for v in data["by_month"].values())


def test_get_rules_returns_empty_list(client):
    response = client.get("/rules")
    assert response.status_code == 200
    assert response.json() == []


def test_post_rule_creates_rule(client):
    response = client.post("/rules", json={"keyword": "YANDEX", "category": "Transport"})
    assert response.status_code == 201
    assert response.json()["keyword"] == "YANDEX"
    assert response.json()["category"] == "Transport"
    assert isinstance(response.json()["id"], int)

def test_get_rules_returns_created_rules(client):
    client.post("/rules", json={"keyword": "YANDEX", "category": "Transport"})
    response = client.get("/rules")
    assert len(response.json()) == 1
    assert response.json()[0]["keyword"] == "YANDEX"


def test_delete_rule_removes_it(client):
    rule = client.post("/rules", json={"keyword": "YANDEX", "category": "Transport"}).json()
    response = client.delete(f"/rules/{rule['id']}")
    assert response.status_code == 200
    assert client.get("/rules").json() == []

def test_delete_rule_not_found_returns_404(client):
    response = client.delete("/rules/999999")
    assert response.status_code == 404
