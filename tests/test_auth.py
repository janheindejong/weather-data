import pytest

from app.entities import Scope
from app.exceptions import AuthorizationError
from app.interactors import CheckPermissionInteractor, CreateTokenInteractor

token_interactor = CreateTokenInteractor()
permissions_interactor = CheckPermissionInteractor()


@pytest.fixture
def read_token() -> str:
    return token_interactor.create_token("pete@company.com", "password2", [Scope.READ])


@pytest.fixture
def write_token() -> str:
    return token_interactor.create_token("john@company.com", "password1", [Scope.WRITE])


def test_multiple_scopes():
    token_interactor.create_token(
        "john@company.com", "password1", [Scope.READ, Scope.WRITE]
    )


def test_authentication_fails():
    with pytest.raises(AuthorizationError):
        token_interactor.create_token("carl@company.com", "mypw", ["weather:read"])


def test_incorrect_privilege_fails():
    with pytest.raises(AuthorizationError):
        token_interactor.create_token(
            "pete@company.com", "password2", ["weather:write"]
        )


def test_check_read_access(read_token: str):
    permissions_interactor.check_read_access(read_token)


def test_check_read_access_fails(write_token: str):
    with pytest.raises(AuthorizationError):
        permissions_interactor.check_read_access(write_token)


def test_check_write_access(write_token: str):
    permissions_interactor.check_write_access(write_token)


def test_check_write_access_fails(read_token: str):
    with pytest.raises(AuthorizationError):
        permissions_interactor.check_write_access(read_token)
