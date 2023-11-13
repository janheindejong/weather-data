"""Responsible for instantiating and tying everything together to run as ASGI webapp"""

import os
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import (
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm,
)

from .adapters import (
    RawWeatherData,
    WebAppWeatherAdapter,
)
from .drivers import SQLiteConnection
from .entities import Scope
from .exceptions import AuthorizationError, DatabaseIntegrityError
from .gateways import SQLConnection, SQLWeatherDbGateway
from .interactors import (
    AverageWeatherQuery,
    CheckPermissionInteractor,
    CreateTokenInteractor,
    LatestWeatherQuery,
    TimeSeriesWeatherQuery,
    WeatherInteractor,
)

DB_PATH = os.getenv("DB_URL", "./data/db.sqlite")


oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={
        "weather:read": "Read weather data.",
        "weather:write": "Post weather data.",
    },
)

app = FastAPI(title="Greenhouse climate API")


def sql_connection() -> SQLiteConnection:
    if not DB_PATH:
        raise RuntimeError("Please set DB_URL environment variable")
    return SQLiteConnection(DB_PATH)


def interactor(
    conn: SQLConnection = Depends(sql_connection),
) -> WebAppWeatherAdapter:
    gateway = SQLWeatherDbGateway(conn)
    interactor = WeatherInteractor(gateway)
    adapted_interactor = WebAppWeatherAdapter(interactor)
    return adapted_interactor


def read_access(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        CheckPermissionInteractor().check_read_access(token)
    except AuthorizationError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err),
            headers={"WWW-Authenticate": "Bearer"},
        ) from err


def write_access(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        CheckPermissionInteractor().check_write_access(token)
    except AuthorizationError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err),
            headers={"WWW-Authenticate": "Bearer"},
        ) from err


@app.post("/token")
def create_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """Login to create access token"""
    try:
        token = CreateTokenInteractor().create_token(
            form_data.username, form_data.password, [Scope(s) for s in form_data.scopes]
        )
    except AuthorizationError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(err),
            headers={"WWW-Authenticate": "Bearer"},
        ) from err
    return {"token_type": "bearer", "access_token": token}


@app.post("/weather", status_code=201, dependencies=[Depends(write_access)])
def post_weather(
    payload: list[RawWeatherData],
    interactor: WebAppWeatherAdapter = Depends(interactor),
):
    """
    Ingress weather data

    Weather data is expected to be of the form:

    ```json
    [
        {
            "ts": "2023-01-01T00:00:00+00:00"
            "rows": [
                ["external_temperature_c", 1.23],
                ["wind_speed_unmuted_m_s", 1.23],
                ["wind_speed_m_s", 1.23],
                ["wind_direction_degrees", 1.23],
                ["radiation_intensity_unmuted_w_m2", 1.23],
                ["radiation_intensity_w_m2", 1.23],
                ["standard_radiation_intensity_w_m2", 1.23],
                ["radiation_sum_j_cm2", 1.23],
                ["radiation_from_plant_w_m2", 1.23],
                ["precipitation", 1.23],
                ["relative_humidity_perc", 1.23],
                ["moisture_deficit_g_kg", 1.23],
                ["moisture_deficit_g_m3", 1.23],
                ["dew_point_temperature_c", 1.23],
                ["abs_humidity_g_kg", 1.23],
                ["enthalpy_kj_kg", 1.23],
                ["enthalpy_kj_m3", 1.23],
                ["atmospheric_pressure_hpa", 1.23]
            ]
        }
    ]
    ```

    Other fields or keys will be ignored.
    """
    try:
        interactor.load(payload)
    except DatabaseIntegrityError as err:
        raise HTTPException(409, "Can't upload the same timestamp twice") from err


@app.get("/weather/latest", dependencies=[Depends(read_access)])
def get_weather_latest(
    tz_offset_seconds: timedelta = timedelta(seconds=0),
    interactor: WebAppWeatherAdapter = Depends(interactor),
):
    """
    Get latest weather data

    Parameters:
    - **tz_offset_seconds**: timezone for presented output
    """
    query = LatestWeatherQuery(tz_offset=tz_offset_seconds)
    return interactor.get(query)


@app.get("/weather/average", dependencies=[Depends(read_access)])
def get_weather_average(
    after: datetime,
    tz_offset_seconds: timedelta = timedelta(seconds=0),
    interactor: WebAppWeatherAdapter = Depends(interactor),
):
    """
    Get average weather data since given point in time

    Parameters:
    - **after**: start of average
    - **tz_offset_seconds**: timezone for presented output
    """
    query = AverageWeatherQuery(after=after, tz_offset=tz_offset_seconds)
    return interactor.get(query)


@app.get("/weather/timeseries", dependencies=[Depends(read_access)])
def get_weather_timeseries(
    after: datetime,
    before: datetime,
    interval_seconds: timedelta,
    tz_offset_seconds: timedelta = timedelta(seconds=0),
    interactor: WebAppWeatherAdapter = Depends(interactor),
):
    """
    Timeseries over weather data, resampled to given interval

    Parameters:
    - **after**: start of time series
    - **before**: end of time series
    - **interval_seconds**: bucket size
    - **tz_offset_seconds**: timezone for presented output
    """
    query = TimeSeriesWeatherQuery(
        after=after,
        before=before,
        interval=interval_seconds,
        tz_offset=tz_offset_seconds,
    )
    return interactor.get(query)
