import uuid

import pytest

WALLET_UUID = str(uuid.uuid4())
BASE_URL = f"/api/v1/wallets/{WALLET_UUID}"


async def test_get_wallet_not_found(client):
    response = await client.get(BASE_URL)
    assert response.status_code == 404
    assert response.json()["detail"] == "Wallet not found"


async def test_get_wallet_found(client):
    await client.post(
        f"{BASE_URL}/operation",
        json={"amount": 100, "operation_type": "DEPOSIT"},
    )
    response = await client.get(BASE_URL)
    assert response.status_code == 200
    data = response.json()
    assert data["uuid"] == WALLET_UUID
    assert data["balance"] == 100


async def test_deposit_creates_new_wallet(client):
    response = await client.post(
        f"{BASE_URL}/operation",
        json={"amount": 500, "operation_type": "DEPOSIT"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["uuid"] == WALLET_UUID
    assert data["balance"] == 500


async def test_deposit_adds_to_existing_balance(client):
    await client.post(
        f"{BASE_URL}/operation",
        json={"amount": 300, "operation_type": "DEPOSIT"},
    )
    response = await client.post(
        f"{BASE_URL}/operation",
        json={"amount": 200, "operation_type": "DEPOSIT"},
    )
    assert response.status_code == 200
    assert response.json()["balance"] == 500


async def test_withdraw_from_nonexistent_wallet(client):
    response = await client.post(
        f"{BASE_URL}/operation",
        json={"amount": 100, "operation_type": "WITHDRAW"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Недостаточно средств"


async def test_withdraw_with_sufficient_balance(client):
    await client.post(
        f"{BASE_URL}/operation",
        json={"amount": 1000, "operation_type": "DEPOSIT"},
    )
    response = await client.post(
        f"{BASE_URL}/operation",
        json={"amount": 400, "operation_type": "WITHDRAW"},
    )
    assert response.status_code == 200
    assert response.json()["balance"] == 600


async def test_withdraw_with_insufficient_balance(client):
    await client.post(
        f"{BASE_URL}/operation",
        json={"amount": 100, "operation_type": "DEPOSIT"},
    )
    response = await client.post(
        f"{BASE_URL}/operation",
        json={"amount": 200, "operation_type": "WITHDRAW"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Недостаточно средств"


async def test_withdraw_exact_balance(client):
    await client.post(
        f"{BASE_URL}/operation",
        json={"amount": 250, "operation_type": "DEPOSIT"},
    )
    response = await client.post(
        f"{BASE_URL}/operation",
        json={"amount": 250, "operation_type": "WITHDRAW"},
    )
    assert response.status_code == 200
    assert response.json()["balance"] == 0


async def test_negative_amount_rejected(client):
    response = await client.post(
        f"{BASE_URL}/operation",
        json={"amount": -50, "operation_type": "DEPOSIT"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Нельзя указывать отрицательные значения"


async def test_zero_amount_deposit_creates_wallet(client):
    response = await client.post(
        f"{BASE_URL}/operation",
        json={"amount": 0, "operation_type": "DEPOSIT"},
    )
    assert response.status_code == 200
    assert response.json()["balance"] == 0
