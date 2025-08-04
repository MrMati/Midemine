import functools
import inspect
import asyncio

from fastapi.testclient import TestClient
import pytest

from player.player import ContentClientAsync


@pytest.mark.asyncio
async def test_asset_info_get(content_platform_client: TestClient):
    content_client = ContentClientAsync("")

    # NOTE: nasty hack, but allows to avoid reimplementing ...ClientAsync
    content_platform_client.request = async_wrap(content_platform_client.request)
    content_client.client = content_platform_client

    asset_info = await content_client.asset_info("1")
    assert asset_info is not None
    # TODO assert content when repo mocking done


def async_wrap(sync_func):
    assert not inspect.iscoroutinefunction(sync_func)

    @functools.wraps(sync_func)
    async def wrapper(*args, **kwargs):
        loop = asyncio.get_running_loop()
        return await loop.run_in_executor(
            None, functools.partial(sync_func, *args, **kwargs)
        )

    return wrapper
