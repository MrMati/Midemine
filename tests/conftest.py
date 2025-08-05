from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from content_platform.content_server import app as content_platform_app
from content_platform.deps import (
    get_settings as platform_get_settings,
    get_catalog_repo,
)

from key_server.key_server import app as key_server_app
from key_server.key_server import get_settings as key_server_get_settings

from .mocks import MockPlatformSettings, MockKeyServerSettings, MockCatalogRepo


@pytest.fixture(scope="module")
def content_platform_client() -> Generator[TestClient, None, None]:
    content_platform_app.dependency_overrides.update(
        {
            platform_get_settings: lambda: MockPlatformSettings(),
            get_catalog_repo: lambda: MockCatalogRepo(),
        }
    )
    with TestClient(content_platform_app) as c:
        yield c


@pytest.fixture(scope="module")
def key_server_client() -> Generator[TestClient, None, None]:
    key_server_app.dependency_overrides[key_server_get_settings] = (
        lambda: MockKeyServerSettings()
    )
    with TestClient(key_server_app) as c:
        yield c
