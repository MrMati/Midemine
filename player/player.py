import sys
import asyncio

import httpx
from enum import Enum
from typing import Any, List, TypeVar, Optional, NewType, AsyncIterable
from pydantic import BaseModel, TypeAdapter

from cdm import MidemineCDM

# TODO use logging library, but pls not the builtin one


class StreamingServiceStatus(BaseModel):
    operational: bool
    status: str


# TODO consider a nested structure with exact media container/encoding info
class MediaType(str, Enum):
    audio = "audio"
    video = "video"


class MediaAssetInfo(BaseModel):
    id: str
    name: str
    description: str
    media_type: MediaType
    encryption_type: str  # TODO proper enum


class EntitlementMessage(BaseModel):
    asset_id: str
    usage_type: str  # TODO proper enum


# TODO placeholder - use pyjwt
JWT = NewType("JWT", str)


class EntitlementResponse(BaseModel):
    claims: List[str]  # TODO proper types
    jwt: JWT


T = TypeVar("T")


class StreamingClientAsync:
    def __init__(self, base_url: str):
        self.client = httpx.AsyncClient(base_url=base_url, timeout=10)

    # NOTE move to separate inheritable class instead of copying
    async def _request(self, method: str, path: str, model: Any, **kwargs) -> T:
        r = await self.client.request(method, path, **kwargs)
        r.raise_for_status()  # FIXME keep connection abstraction hidden from class user
        return TypeAdapter(model).validate_python(r.json())

    async def check_connection(self) -> Optional[StreamingServiceStatus]:
        # NOTE dont use such constructions much
        try:
            return await self._request("GET", "/status", StreamingServiceStatus)
        except (httpx.HTTPStatusError, httpx.RequestError):
            return None

    async def asset_info(self, asset: str) -> MediaAssetInfo:
        return await self._request("GET", f"/catalog/{asset}", MediaAssetInfo)

    async def fetch_asset(self, asset: str) -> Optional[bytes]:
        r = await self.client.request("GET", f"/assets/{asset}")
        if not r.is_success:
            return None
        return r.content

    # FIXME probably wrong
    async def fetch_asset_streaming(self, asset: str) -> AsyncIterable[bytes]:
        r = await self.client.stream("GET", f"/assets/{asset}")
        if not r.is_success:
            return None
        return r.iter_bytes()

    async def get_entitlement_jwt(
        self, entitlement_msg: EntitlementMessage
    ) -> EntitlementResponse:
        return await self._request(
            "GET", "/entitlement", EntitlementResponse, json=entitlement_msg
        )

    async def close(self):
        await self.client.aclose()


class LicenseClientAsync:
    def __init__(self, base_url: str):
        self.client = httpx.AsyncClient(base_url=base_url, timeout=10)

    # license_req is an unparseable binary blob, so just passing it through
    async def acquire_license(self, license_req: bytes, jwt: JWT) -> Optional[bytes]:
        # NOTE make generic function with auth support if used more
        headers = {"Authorization": f"Bearer {jwt}"}
        r = await self.client.request(
            "POST", "/acquire_license", content=license_req, headers=headers
        )
        if not r.is_success:
            return None
        return r.content

    async def close(self):
        await self.client.aclose()


async def playback_not_encrypted(
    service_client: StreamingClientAsync, asset_info: MediaAssetInfo
):
    print(f"Playing {asset_info.name}")
    content = await service_client.fetch_asset_streaming(asset_info.name)
    if content is None:
        print(f"Cannot fetch asset {asset_info.name}")
        return

    print(len(content))

    print(f"Playback of {asset_info.name} finished")


async def playback_encrypted(
    service_url: str, service_client: StreamingClientAsync, asset_info: MediaAssetInfo
):
    print(f"Playing {asset_info.name}")

    cdm_adapter = MidemineCDM()

    # FIXME ensure CDM gets killed on early exit
    cdm_init_task = asyncio.create_task(cdm_adapter.check_env())

    entitlement_msg = EntitlementMessage(asset_id=asset_info.id, usage_type="playback")
    entitlement_response = await service_client.get_entitlement_jwt(entitlement_msg)
    if entitlement_response is None:
        print(f"Cannot get entitlement for asset {asset_info.name}")
        return

    # TODO parse JWT in entitlement_response to get stuff like key id
    asset_key_id = "abcd"

    license_client = LicenseClientAsync(service_url)

    await cdm_init_task

    license_req = cdm_adapter.get_license_request(asset_info.id, asset_key_id)

    license = await license_client.acquire_license(
        license_req, entitlement_response.jwt
    )
    if license is None:
        print(f"Cannot acquire license for asset {asset_info.name}")
        return

    lic_parse_result = cdm_adapter.insert_license(license)
    if not lic_parse_result.ok:
        print(f"Cannot parse license for asset {asset_info.name}")
        return

    content = await service_client.fetch_asset_streaming(asset_info.name)
    if content is None:
        print(f"Cannot fetch asset {asset_info.name}")
        return

    decrypted_content = cdm_adapter.decrypt_content(content)

    print(len(decrypted_content))

    print(f"Protected playback of {asset_info.name} finished")

    # TODO cdm session stuff
    # cdm_adapter.close_session()


async def app(service_url: str, asset: str):
    # check service connectivity
    # fetch asset existence/info
    # download asset
    # display if not encrypted

    # otherwise:

    # init CDM in bg
    # 1. exchange entitlement message for JWT with service
    # 2. (wait for CDM)get license req from CDM
    # 3. send license req + JWT to license server
    # 4  pass acquired license to CDM
    # 5. CDM does its thing
    # 6. playback starts

    service_client = StreamingClientAsync(service_url)
    status = await service_client.check_connection()
    if status is None:
        print(f"Cannot connect to streaming service at {service_url}")
        return
    if not status.operational:
        print(f"Streaming service at {service_url} is not operational")
        return

    asset_info = await service_client.asset_info(asset)
    if asset_info is None:
        print(f"Asset {asset} does not exist")

    if asset_info.encryption_type == "none":
        await playback_not_encrypted(service_client, asset_info)
        return

    await playback_encrypted(service_url, service_client, asset_info)


def main():
    # TODO use argparse or cli library
    if len(sys.argv) < 3:
        print("Usage: ./player <host> <media_asset>")
        return

    asyncio.run(app(sys.argv[1], sys.argv[2]))


if __name__ == "__main__":
    main()
