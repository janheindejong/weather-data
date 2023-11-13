import json
import os
import pathlib
from datetime import timedelta
from typing import Any

import pytest

from app.adapters import RawWeatherData
from app.drivers import SQLiteConnection
from app.entities import WeatherData
from app.gateways import SQLWeatherDbGateway
from app.interactors import (
    WeatherInteractor,
)

TZ = timedelta(seconds=7200)


@pytest.fixture(scope="session")
def raw_data() -> list[dict[str, Any]]:
    data = []
    for subdir, _, files in os.walk("./data/may/01"):
        for file in files:
            path = subdir + "/" + file
            with open(path) as f:
                data.append(json.loads(f.read()))
    return data


@pytest.fixture
def data(raw_data: list[dict[str, Any]]) -> list[WeatherData]:
    return [RawWeatherData.parse_obj(d).transform() for d in raw_data]


@pytest.fixture
def db_path(tmpdir: pathlib.Path) -> pathlib.Path:
    path = tmpdir / "db.sqlite"
    conn = SQLiteConnection(path)
    cur = conn.cursor()
    with open("./app/sql/weather_create_table.sql") as f:
        operations = f.read().split(";")
    for operation in operations:
        cur.execute(operation)
    conn.commit()
    conn.close()
    return path


@pytest.fixture
def interactor(db_path: pathlib.Path) -> WeatherInteractor:
    conn = SQLiteConnection(db_path)
    gateway = SQLWeatherDbGateway(conn)
    interactor = WeatherInteractor(gateway)
    return interactor


@pytest.fixture
def prepopulated_db(interactor: WeatherInteractor, data: list[WeatherData]) -> None:
    interactor.load(data)
