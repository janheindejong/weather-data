"""Responsible for business logic"""

from datetime import datetime, timedelta, timezone, tzinfo
from typing import Iterable, Literal, Protocol

from jose import JWTError, jwt
from pydantic import BaseModel, validator

from .entities import Scope, Token, WeatherData
from .exceptions import AuthorizationError


class WeatherDbGateway(Protocol):
    """Interface for getting weather data from database"""

    def load(self, weather: Iterable[WeatherData]) -> None:
        ...

    def get_latest(
        self,
        tz: tzinfo = timezone.utc,
    ) -> WeatherData:
        ...

    def get_between(
        self,
        after: datetime,
        before: datetime,
        interval: timedelta,
        tz: tzinfo = timezone.utc,
    ) -> list[WeatherData]:
        ...

    def get_average_since(
        self, since: datetime, tz: tzinfo = timezone.utc
    ) -> WeatherData:
        ...


class LatestWeatherQuery(BaseModel):

    tz_offset: timedelta = timedelta(seconds=0)
    kind: Literal["latest"] = "latest"


class AverageWeatherQuery(BaseModel):

    after: datetime
    tz_offset: timedelta = timedelta(seconds=0)
    kind: Literal["average"] = "average"


class TimeSeriesWeatherQuery(BaseModel):

    after: datetime
    before: datetime
    interval: timedelta
    tz_offset: timedelta = timedelta(seconds=0)
    kind: Literal["timeseries"] = "timeseries"

    @validator("before")
    def before_must_be_later(cls, v, values, **kwargs):
        if not v > values["after"]:
            raise ValueError("`before` must be greater than `after`")
        return v


class WeatherInteractor:
    """Responsible for business logic; pretty thin, since most is pushed to DB"""

    def __init__(self, weather_db_gateway: WeatherDbGateway) -> None:
        self._weather_db_gateway = weather_db_gateway

    def load(self, data: Iterable[WeatherData]) -> None:
        self._weather_db_gateway.load(data)

    def get(
        self, query: LatestWeatherQuery | AverageWeatherQuery | TimeSeriesWeatherQuery
    ) -> list[WeatherData]:
        tz = timezone(query.tz_offset)
        if query.kind == "latest":
            return [self._weather_db_gateway.get_latest(tz=tz)]
        elif query.kind == "average":
            return [self._weather_db_gateway.get_average_since(query.after, tz=tz)]
        elif query.kind == "timeseries":
            return self._weather_db_gateway.get_between(
                query.after, query.before, query.interval, tz=tz
            )


# In a real-world scenario, this key would not be here...
_SECRET_KEY = "1a03ad0460438cff99ec8ccb88201e858b1de2699357965a54aa6ca60cc1ae87"
_ALGORITHM = "HS256"


class CreateTokenInteractor:
    """Reponsible for creating tokens; raises AuthenticationError and
    AuthorizationError

    Note that this is a bit of a dummy class; in a real-world scenario, creating
    tokens would probably not be part of this service.
    """

    _EXPIRATION_MINUTES = 15
    _fake_user_db = [
        {
            "id": 1,
            "email": "john@company.com",
            "hashed_pw": "password1",
            "privileges": ["weather:read", "weather:write"],
        },
        {
            "id": 2,
            "email": "pete@company.com",
            "hashed_pw": "password2",
            "privileges": ["weather:read"],
        },
    ]

    def create_token(self, email: str, password: str, scopes: list[Scope]) -> str:
        user = self._get_user(email, password)
        self._check_privileges(user, scopes)
        exp = self._get_expiration_date()
        token = Token(sub=email, scopes=scopes, exp=exp)
        encrypted_token = self._encrypt_token(token)
        return encrypted_token

    def _get_user(self, email: str, password: str) -> dict:
        hashed_pw = self._hash_password(password)
        for user in self._fake_user_db:
            if user["email"] == email and user["hashed_pw"] == hashed_pw:
                return user
        raise AuthorizationError("Incorrect credentials")

    def _check_privileges(self, user: dict, scopes: list[Scope]):
        for scope in scopes:
            if scope not in user["privileges"]:
                raise AuthorizationError(
                    f"User doesn't have privilege for scope '{scope}'"
                )

    def _get_expiration_date(self) -> datetime:
        return datetime.utcnow() + timedelta(minutes=self._EXPIRATION_MINUTES)

    def _hash_password(self, pw: str) -> str:
        # For security reasons, this should have some nice hashing algorithm.
        # However, since this is a dummy class anyway, I didn't bother.
        return pw

    def _encrypt_token(self, token: Token) -> str:
        return jwt.encode(token.dict(), _SECRET_KEY, algorithm=_ALGORITHM)


class CheckPermissionInteractor:
    """Responsible for checking permissions; raises AuthorizationError"""

    def check_read_access(self, token: str):
        decrypted_token = self._decrypt_token(token)
        if Scope.READ not in decrypted_token.scopes:
            raise AuthorizationError("Not privileged to read")

    def check_write_access(self, token: str):
        decrypted_token = self._decrypt_token(token)
        if Scope.WRITE not in decrypted_token.scopes:
            raise AuthorizationError("Not privileged to write")

    def _decrypt_token(self, token: str | bytes) -> Token:
        try:
            decrypted_token = jwt.decode(token, _SECRET_KEY, algorithms=[_ALGORITHM])
        except JWTError as err:
            raise AuthorizationError("Couldn't verify token") from err
        return Token.parse_obj(decrypted_token)
