"""Gateways to database, responsible for turning SQL based data into entities"""

from datetime import datetime, timedelta, timezone, tzinfo
from typing import Any, Iterable, Protocol

from app.entities import WeatherData

from .interactors import WeatherDbGateway


def _load_query(filename: str) -> str:
    with open(filename, "r") as f:
        s = f.read()
    return s


class SQLCursor(Protocol):
    """Stricter implementation of PEP249 Connection object"""

    def execute(self, sql: str):
        ...

    def executemany(self, sql: str, parameters: Iterable):
        ...

    def fetchone(self) -> dict[str, Any] | None:
        ...

    def fetchall(self) -> list[dict[str, Any]]:
        ...

    @property
    def lastrowid(self) -> int | None:
        ...


class SQLConnection(Protocol):
    """Stricter implementation of PEP249 Cursor object"""

    def cursor(self) -> SQLCursor:
        ...

    def commit(self):
        ...


class SQLWeatherDbGateway(WeatherDbGateway):
    """Responsible for turning SQL based data into entities and vice versa"""

    _table_name = "weather"
    _queries = {
        "insert": _load_query("./app/sql/weather_insert.sql"),
        "latest": _load_query("./app/sql/weather_get_latest.sql"),
        "between": _load_query("./app/sql/weather_get_between.sql"),
        "average": _load_query("./app/sql/weather_get_average_since.sql"),
    }

    def __init__(self, conn: SQLConnection):
        self._conn = conn

    def load(self, weather: Iterable[WeatherData]) -> None:
        data_generator = map(lambda x: self._weather_to_row(x), weather)
        cur = self._conn.cursor()
        operation = self._queries["insert"]
        cur.executemany(operation, data_generator)
        self._conn.commit()

    def get_latest(self, tz: tzinfo = timezone.utc) -> WeatherData:
        cur = self._conn.cursor()
        operation = self._queries["latest"]
        cur.execute(operation)
        row = cur.fetchone()
        if not row:
            raise Exception("Couldn't get latest row; is there data at all?")
        return self._row_to_weather(row, tz=tz)

    def get_between(
        self,
        after: datetime,
        before: datetime,
        interval: timedelta,
        tz: tzinfo = timezone.utc,
    ) -> list[WeatherData]:
        cur = self._conn.cursor()
        operation = self._queries["between"].format(
            **{
                "interval_seconds": interval.total_seconds(),
                "timestamp_after": int(after.timestamp()),
                "timestamp_before": int(before.timestamp()),
            }
        )
        cur.execute(operation)
        return [self._row_to_weather(row, tz=tz) for row in cur.fetchall()]

    def get_average_since(
        self, since: datetime, tz: tzinfo = timezone.utc
    ) -> WeatherData:
        cur = self._conn.cursor()
        operation = self._queries["average"].format(
            **{"timestamp_since": int(since.timestamp())}
        )
        cur.execute(operation)
        row = cur.fetchone()
        if not row:
            raise Exception("Couldn't get average; is there data at all?")
        return self._row_to_weather(row, tz=tz)

    @staticmethod
    def _row_to_weather(row: dict[str, Any], tz: tzinfo = timezone.utc) -> WeatherData:
        row = row.copy()  # Prevent side effects
        row["timestamp"] = datetime.fromtimestamp(row["timestamp"], tz=tz)
        return WeatherData(**row)

    @staticmethod
    def _weather_to_row(weather: WeatherData) -> dict[str, Any]:
        d = weather.dict()
        d["timestamp"] = int(weather.timestamp.timestamp())
        return d
