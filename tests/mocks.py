from pydantic_settings import BaseSettings

from typing import Optional

from content_platform.repos import CatalogRepo, MediaAssetInfo
from shared.domain import MediaType


class MockPlatformSettings(BaseSettings):
    JWT_PRIVKEY: str = """-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEINjcD5Bwor22UjQX4Oyxb2NIZIQ5OMLnbl++U48bP7aP
-----END PRIVATE KEY-----"""


class MockKeyServerSettings(BaseSettings):
    JWT_PUBKEY: str = """-----BEGIN PUBLIC KEY-----
MCowBQYDK2VwAyEAb0hwPBogIMrp59wT4HDO/L1x4MOQmcJUZSFyLnLY88c=
-----END PUBLIC KEY-----"""


class MockCatalogRepo(CatalogRepo):
    catalog = {
        "1": MediaAssetInfo(
            id="1",
            name="ONE",
            description="ONE-vid-none",
            media_type=MediaType.video,
            encryption_type="none",
        ),
        "2": MediaAssetInfo(
            id="2",
            name="TWO",
            description="TWO-img-cenc",
            media_type=MediaType.image,
            encryption_type="cenc",
        ),
    }

    def check_asset_exists(self, asset_id: str) -> bool:
        return asset_id in self.catalog

    def get_asset_info(self, asset_id: str) -> Optional[MediaAssetInfo]:
        return self.catalog.get(asset_id)
