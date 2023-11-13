"""Holds key entities (i.e. the data objects)"""
from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel


class Scope(str, Enum):
    READ = "weather:read"
    WRITE = "weather:write"


class Token(BaseModel):
    sub: str
    scopes: list[Scope]
    exp: datetime


class WeatherData(BaseModel):

    timestamp: datetime
    external_temperature_c: float
    wind_speed_unmuted_m_s: float
    wind_speed_m_s: float
    wind_direction_degrees: float
    radiation_intensity_unmuted_w_m2: float
    radiation_intensity_w_m2: float
    standard_radiation_intensity_w_m2: float
    radiation_sum_j_cm2: float
    radiation_from_plant_w_m2: float
    precipitation: float
    relative_humidity_perc: float
    moisture_deficit_g_kg: float
    moisture_deficit_g_m3: float
    dew_point_temperature_c: float
    abs_humidity_g_kg: float
    enthalpy_kj_kg: float
    enthalpy_kj_m3: float
    atmospheric_pressure_hpa: float

    def __lt__(self, o: WeatherData):
        return self.timestamp < o.timestamp
