"""Responsible for connecting to database"""

import functools
import os
import sqlite3
from typing import Any, Iterable

from .exceptions import DatabaseError, DatabaseIntegrityError
from .gateways import SQLConnection, SQLCursor


def _sqlite_exception_handler(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except sqlite3.IntegrityError as err:
            raise DatabaseIntegrityError(err) from err
        except sqlite3.Error as err:
            raise DatabaseError(err) from err

    return wrapper


class SQLiteCursor(SQLCursor):
    """Very thin wrapper around sqlite3.Cursor class"""

    def __init__(self, cursor: sqlite3.Cursor) -> None:
        self._cur = cursor

    @_sqlite_exception_handler
    def execute(self, sql: str):
        self._cur = self._cur.execute(sql)

    @_sqlite_exception_handler
    def executemany(self, sql: str, parameters: Iterable):
        self._cur = self._cur.executemany(sql, parameters)

    @_sqlite_exception_handler
    def fetchone(self) -> dict[str, Any] | None:
        return self._cur.fetchone()

    @_sqlite_exception_handler
    def fetchall(self) -> list[dict[str, Any]]:
        return self._cur.fetchall()

    @property
    @_sqlite_exception_handler
    def lastrowid(self) -> int | None:
        return self._cur.lastrowid


class SQLiteConnection(SQLConnection):
    """Very thin wrapper around sqlite3.Connection"""

    def __init__(self, path: str | bytes | os.PathLike) -> None:
        self._conn = sqlite3.connect(path)
        self._conn.row_factory = self._dict_factory

    def cursor(self) -> SQLCursor:
        return SQLiteCursor(self._conn.cursor())

    @_sqlite_exception_handler
    def commit(self):
        self._conn.commit()

    @_sqlite_exception_handler
    def close(self):
        return self._conn.close()

    @staticmethod
    def _dict_factory(cursor, row):
        fields = [column[0] for column in cursor.description]
        return {key: value for key, value in zip(fields, row, strict=True)}
