# tests/test_app.py
import os

import pytest

from app.app import app


@pytest.fixture
def client():
    # Set testing environment variables to disable CSRF and rate limiting
    os.environ["TESTING"] = "true"
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    # Disable rate limiter for testing
    from app.app import limiter

    limiter.enabled = False

    with app.test_client() as client:
        yield client


def test_index_get(client):
    response = client.get("/")
    assert response.status_code == 200
    assert (
        b"<!DOCTYPE html>" in response.data
    )  # Assuming the HTML template starts with <!DOCTYPE html>


def test_calculate_post_sumar(client):
    response = client.post("/calculate", data={"num1": "2", "num2": "3", "operacion": "sumar"})
    assert response.status_code == 200
    assert b"5.0" in response.data


def test_calculate_post_restar(client):
    response = client.post("/calculate", data={"num1": "5", "num2": "3", "operacion": "restar"})
    assert response.status_code == 200
    assert b"2.0" in response.data


def test_calculate_post_multiplicar(client):
    response = client.post(
        "/calculate", data={"num1": "2", "num2": "3", "operacion": "multiplicar"}
    )
    assert response.status_code == 200
    assert b"6.0" in response.data


def test_calculate_post_dividir(client):
    response = client.post("/calculate", data={"num1": "6", "num2": "3", "operacion": "dividir"})
    assert response.status_code == 200
    assert b"2.0" in response.data


def test_calculate_post_dividir_by_zero(client):
    response = client.post(
        "/calculate", data={"num1": "6.0", "num2": "0.0", "operacion": "dividir"}
    )
    assert response.status_code == 200
    assert b"Error: No se puede dividir por cero" in response.data


def test_calculate_post_invalid_operation(client):
    response = client.post("/calculate", data={"num1": "6", "num2": "3", "operacion": "invalid"})
    assert response.status_code == 200
    assert b"Error: Datos de entrada inv\xc3\xa1lidos" in response.data


def test_calculate_post_invalid_numbers(client):
    response = client.post("/calculate", data={"num1": "a", "num2": "b", "operacion": "sumar"})
    assert response.status_code == 200
    assert b"Error: Datos de entrada inv\xc3\xa1lidos" in response.data
