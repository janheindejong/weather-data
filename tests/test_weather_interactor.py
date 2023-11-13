import pathlib
import sqlite3
from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from app.entities import WeatherData
from app.exceptions import DatabaseIntegrityError
from app.interactors import (
    AverageWeatherQuery,
    LatestWeatherQuery,
    TimeSeriesWeatherQuery,
    WeatherInteractor,
)

TZ = timedelta(seconds=7200)


def test_query_validators():
    with pytest.raises(ValidationError):
        TimeSeriesWeatherQuery(
            after=datetime.fromisoformat("2021-05-02T02:00:00+02:00"),
            before=datetime.fromisoformat("2021-05-02T01:00:00+02:00"),
            interval=timedelta(hours=1),
        )


@pytest.mark.usefixtures("prepopulated_db")
def test_load(db_path: pathlib.Path, data: list):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT count(*) FROM weather")
    assert cur.fetchone() == (len(data),)


@pytest.mark.usefixtures("prepopulated_db")
def test_duplicate_entry_raises_error(
    interactor: WeatherInteractor, data: list[WeatherData]
):
    with pytest.raises(DatabaseIntegrityError):
        interactor.load(data[:1])


@pytest.mark.usefixtures("prepopulated_db")
def test_get_latest(interactor: WeatherInteractor, data: list[WeatherData]):
    data.sort()
    assert interactor.get(LatestWeatherQuery(tz_offset=TZ)) == data[-1:]


@pytest.mark.usefixtures("prepopulated_db")
def test_get_average(interactor: WeatherInteractor):
    query = AverageWeatherQuery(
        after=datetime.fromisoformat("2021-05-02T01:00:00+02:00"), tz_offset=TZ
    )
    result = interactor.get(query)
    assert result[0].timestamp.isoformat() == "2021-05-02T01:02:51+02:00"
    assert result[0].wind_direction_degrees == 317.0833333333333


@pytest.mark.usefixtures("prepopulated_db")
def test_get_timeseries(interactor: WeatherInteractor):
    query = TimeSeriesWeatherQuery(
        after=datetime.fromisoformat("2021-05-01T02:00:00+02:00"),
        before=datetime.fromisoformat("2021-05-02T02:00:00+02:00"),
        interval=timedelta(hours=1),
        tz_offset=TZ,
    )
    result = interactor.get(query)
    assert len(result) == 24
    assert result[-1].wind_direction_degrees == 317.0833333333333
