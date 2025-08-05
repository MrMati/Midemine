from collections.abc import Generator, AsyncGenerator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient, ASGITransport
from asgi_lifespan import LifespanManager

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


@pytest_asyncio.fixture(scope="module")
async def content_platform_client_async() -> AsyncGenerator[AsyncClient, None, None]:
    content_platform_app.dependency_overrides.update(
        {
            platform_get_settings: lambda: MockPlatformSettings(),
            get_catalog_repo: lambda: MockCatalogRepo(),
        }
    )
    transport = ASGITransport(app=content_platform_app)

    async with LifespanManager(content_platform_app):
        async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
            yield ac
