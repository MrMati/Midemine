from typing import Optional, AsyncIterable
import asyncio
from pydantic import BaseModel


class LicenseParseResult(BaseModel):
    ok: bool
    msg: Optional[str]


class MidemineCDM:
    def __init__(self):
        self.license_data = None

    # part of future tamper protection mechanisms
    async def check_env(self) -> bool:
        await asyncio.sleep(1)
        return True

    # TODO add session management

    def get_license_request(self, asset_id: str, key_id: str) -> bytes:
        return bytes([1, 2, 3])

    def insert_license(self, license: bytes) -> LicenseParseResult:
        self.license_data = license
        return LicenseParseResult(ok=True, msg=None)

    # TODO add output/decoding settings

    async def decrypt_content(self, content: AsyncIterable[bytes]) -> Optional[AsyncIterable[bytes]]:
        if self.license_data is None:
            return None

        async def _gen():
            async for chunk in content:
                yield bytes(b ^ 0x55 for b in chunk)

        return _gen()