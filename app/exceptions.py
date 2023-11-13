"""Contains exceptions used through the app"""


class WeatherAppError(Exception):
    """Base error"""


class AuthorizationError(WeatherAppError):
    """Thrown when not able to authorize action"""


class DatabaseError(WeatherAppError):
    """Thrown when an error arises from a database interaction"""


class DatabaseIntegrityError(WeatherAppError):
    """Thrown when trying to insert data the violates database constraints"""
