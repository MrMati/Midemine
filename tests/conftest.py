from collections.abc import Generator

import pytest
from pydantic_settings import BaseSettings
from fastapi.testclient import TestClient

from content_platform.content_server import app as content_platform_app
from content_platform.deps import get_settings as platform_get_settings

from key_server.key_server import app as key_server_app
from key_server.key_server import get_settings as key_server_get_settings


class OverridePlatformSettings(BaseSettings):
    JWT_PRIVKEY: str = """-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEINjcD5Bwor22UjQX4Oyxb2NIZIQ5OMLnbl++U48bP7aP
-----END PRIVATE KEY-----"""


class OverrideKeyServerSettings(BaseSettings):
    JWT_PUBKEY: str = """-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAb0hwPBogIMrp59wT4HDO/L1x4MOQmcJUZSFyLnLY88c=
-----END PUBLIC KEY-----"""


@pytest.fixture(scope="module")
def content_platform_client() -> Generator[TestClient, None, None]:
    content_platform_app.dependency_overrides[platform_get_settings] = (
        lambda: OverridePlatformSettings()
    )
    with TestClient(content_platform_app) as c:
        yield c


@pytest.fixture(scope="module")
def key_server_client() -> Generator[TestClient, None, None]:
    key_server_app.dependency_overrides[key_server_get_settings] = (
        lambda: OverrideKeyServerSettings()
    )
    with TestClient(key_server_app) as c:
        yield c
