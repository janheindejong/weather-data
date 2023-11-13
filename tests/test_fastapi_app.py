import pathlib
import sqlite3
from typing import Any

import pytest
from fastapi.testclient import TestClient

from app.drivers import SQLiteConnection
from app.main import app, sql_connection


@pytest.fixture
def client(db_path: pathlib.Path):
    client = TestClient(app)

    def get_conn():
        return SQLiteConnection(db_path)

    app.dependency_overrides[sql_connection] = get_conn
    return client


@pytest.fixture
def auth_headers(client: TestClient) -> dict[str, str]:
    login_data = {
        "username": "john@company.com",
        "password": "password1",
        "scope": "weather:read weather:write",
    }
    response = client.post("/token", data=login_data)
    assert response.status_code == 200
    payload = response.json()
    token = payload["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_post(
    client: TestClient,
    raw_data: list[dict[str, Any]],
    db_path: pathlib.Path,
    auth_headers: dict[str, str],
):
    new_datapoint = raw_data[0].copy()
    response = client.post("/weather", json=[new_datapoint], headers=auth_headers)
    assert response.status_code == 201
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT timestamp FROM weather ORDER BY timestamp LIMIT 1;")
    assert cur.fetchone() == (1619856770,)


@pytest.mark.usefixtures("prepopulated_db")
def test_post_twice(
    client: TestClient, raw_data: list[dict], auth_headers: dict[str, str]
):
    response = client.post("/weather", json=raw_data, headers=auth_headers)
    assert response.status_code == 409
    assert response.content == b'{"detail":"Can\'t upload the same timestamp twice"}'


@pytest.mark.usefixtures("prepopulated_db")
def test_weather_get_latest(client: TestClient, auth_headers: dict[str, str]):
    response = client.get(
        "/weather/latest", params={"tz_offset_seconds": 7200}, headers=auth_headers
    )
    data = response.json()
    assert response.status_code == 200
    assert data["timestamp"] == "2021-05-02T01:57:51+02:00"


@pytest.mark.usefixtures("prepopulated_db")
def test_weather_get_average(client: TestClient, auth_headers: dict[str, str]):
    response = client.get(
        "/weather/average",
        params={
            "after": "2021-05-02T01:00:00+02:00",
            "tz_offset_seconds": 7200,
        },
        headers=auth_headers,
    )
    data = response.json()
    assert response.status_code == 200
    assert data["timestamp"] == "2021-05-02T01:02:51+02:00"
    assert data["wind_direction_degrees"] == 317.0833333333333


@pytest.mark.usefixtures("prepopulated_db")
def test_weather_get_timeseries(client: TestClient, auth_headers: dict[str, str]):
    response = client.get(
        "/weather/timeseries",
        params={
            "after": "2021-05-01T02:00:00+02:00",
            "before": "2021-05-02T02:00:00+02:00",
            "interval_seconds": 3600,
            "tz_offset_seconds": 7200,
        },
        headers=auth_headers,
    )
    data = response.json()
    assert response.status_code == 200
    assert len(data["timestamp"]) == 24
    assert data["wind_direction_degrees"][-1] == 317.0833333333333
