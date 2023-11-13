"""Responsible for transforming data between interactors and interface"""

from datetime import datetime
from typing import Any, Generator, Iterable

from pydantic import BaseModel

from .entities import WeatherData
from .interactors import (
    AverageWeatherQuery,
    LatestWeatherQuery,
    TimeSeriesWeatherQuery,
    WeatherInteractor,
)


class RawWeatherData(BaseModel):
    ts: datetime | str
    rows: list[tuple[str, Any]]

    def transform(self) -> WeatherData:
        # Format timestamp
        if isinstance(self.ts, str):
            ts = datetime.fromisoformat(self.ts)
        else:
            ts = self.ts
        # Map rows to dict
        kwargs = {**{"timestamp": ts}, **dict(self.rows)}
        return WeatherData(**kwargs)


class CliWeatherAdapter:
    def __init__(self, interactor: WeatherInteractor) -> None:
        self._interactor = interactor

    def load(self, paths: Iterable[str]):
        self._interactor.load(self._open_files(paths))

    @classmethod
    def _open_files(cls, paths: Iterable[str]) -> Generator[WeatherData, None, None]:
        for path in paths:
            data = RawWeatherData.parse_file(path)
            yield data.transform()


class WebAppWeatherAdapter:
    def __init__(self, interactor: WeatherInteractor) -> None:
        self._interactor = interactor

    def load(self, data: Iterable[RawWeatherData]):
        parsed_data = map(lambda x: x.transform(), data)
        self._interactor.load(parsed_data)

    def get(
        self, query: LatestWeatherQuery | AverageWeatherQuery | TimeSeriesWeatherQuery
    ) -> dict:
        result = self._interactor.get(query)
        if query.kind == "timeseries":
            return self._pivot_timeseries(result)
        else:
            return result[0].dict()

    def _pivot_timeseries(self, data: list[WeatherData]) -> dict[str, list]:
        out: dict[str, list] = {key: [] for key in WeatherData.__fields__}
        for entry in data:
            d = entry.dict()
            for key in WeatherData.__fields__:
                out[key].append(d[key])
        return out
