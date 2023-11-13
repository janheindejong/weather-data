"""Simple CLI for accessing weather data; for now simply for bulk creating
data entries, e.g. for creating dev database"""

import argparse
import os
from typing import Generator

from app.adapters import (
    CliWeatherAdapter,
)
from app.drivers import SQLiteConnection
from app.gateways import SQLWeatherDbGateway
from app.interactors import (
    WeatherInteractor,
)


def get_interactor(db_url: str) -> CliWeatherAdapter:
    conn = SQLiteConnection(db_url)
    gateway = SQLWeatherDbGateway(conn)
    interactor = WeatherInteractor(gateway)
    return CliWeatherAdapter(interactor)


def file_path_generator(path: str) -> Generator[str, None, None]:
    for subdir, _, files in os.walk(path):
        for file in files:
            path = subdir + "/" + file
            print(path)
            yield path


def main():
    parser = argparse.ArgumentParser(
        prog="Greenhouse climate CLI",
        description="Simple CLI for uploading weather data in bulk",
    )

    parser.add_argument("path", help="Path to iteratively traverse for raw data")
    parser.add_argument(
        "--database-url",
        dest="db",
        default="./data/db.sqlite",
        help="URL for database (default ./data/db.sqlite)",
    )
    args = parser.parse_args()
    interactor = get_interactor(args.db)
    interactor.load(file_path_generator(args.path))
