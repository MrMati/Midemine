from typing import Annotated
from functools import lru_cache

from fastapi import Depends

from .repos import CatalogRepo, AssetDataRepo, RealCatalogRepo, RealAssetDataRepo
from .config import Settings


# TODO repo contructors will take params like session/path
# TODO check if using lru_cache on repos is a good idea


def get_catalog_repo():
    return RealCatalogRepo()


def get_asset_data_repo():
    return RealAssetDataRepo()


CatalogRepoDep = Annotated[CatalogRepo, Depends(get_catalog_repo)]

AssetDataRepoDep = Annotated[AssetDataRepo, Depends(get_asset_data_repo)]


@lru_cache
def get_settings():
    print("makin settings")
    return Settings()


SettingsDep = Annotated[Settings, Depends(get_settings)]
