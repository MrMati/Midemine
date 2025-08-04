from typing import Optional, AsyncIterator
from abc import ABC, abstractmethod

import aiofiles

from shared.domain import MediaAssetInfo, MediaType

catalog = {
    "1": MediaAssetInfo(
        id="1",
        name="The Matrix",
        description="A computer hacker learns from mysterious rebels about the true nature of his reality and his role in the war against its controllers.",
        media_type=MediaType.video,
        encryption_type="none",
    ),
    "2": MediaAssetInfo(
        id="2",
        name="Imagine Dragons poster",
        description="A band poster featuring the Imagine Dragons band members.",
        media_type=MediaType.image,
        encryption_type="cenc",
    ),
}

asset_filepaths = {
    "1": "matrix.mp4",
    "2": "imagine_dragons.jpg",
}


class CatalogRepo(ABC):
    @abstractmethod
    def check_asset_exists(self, asset_id: str) -> bool:
        pass

    @abstractmethod
    def get_asset_info(self, asset_id: str) -> Optional[MediaAssetInfo]:
        pass


class RealCatalogRepo(CatalogRepo):
    def check_asset_exists(self, asset_id: str) -> bool:
        return asset_id in catalog

    def get_asset_info(self, asset_id: str) -> Optional[MediaAssetInfo]:
        return catalog.get(asset_id)


# TODO move to utils, verify
async def stream_file(path: str) -> AsyncIterator[bytes]:
    async with aiofiles.open(path, mode="rb") as f:
        while chunk := await f.read(1024 * 1024):  # 1MB chunks
            yield chunk


class AssetDataRepo(ABC):
    @abstractmethod
    def get_asset_stream(self, asset_id: str) -> Optional[AsyncIterator[bytes]]:
        pass


class RealAssetDataRepo(AssetDataRepo):
    def get_asset_stream(self, asset_id: str) -> Optional[AsyncIterator[bytes]]:
        if (filepath := asset_filepaths.get(asset_id)) is None:
            return None
        return stream_file(f"assets/{filepath}")
