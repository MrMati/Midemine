from httpx import AsyncClient
import pytest

from player.player import ContentClientAsync
from .mocks import MockCatalogRepo


@pytest.mark.parametrize(
    "expect_success,item_id",
    [
        (True, "1"),
        (True, "2"),
        (False, "3"),
    ],
)
@pytest.mark.asyncio
async def test_asset_info_get(
    content_platform_client_async: AsyncClient, expect_success: bool, item_id: str
):
    content_client = ContentClientAsync("")
    content_client.client = content_platform_client_async

    asset_info = await content_client.asset_info(item_id)

    if expect_success:
        assert asset_info == MockCatalogRepo.catalog[item_id]
    else:
        assert asset_info is None
