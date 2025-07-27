from typing import Optional


class MidemineCDM:
    def __init__(self):
        self.license_data = None

    # part of future tamper protection mechanisms
    def check_env(self) -> bool:
        return True

    # TODO add session management

    def get_license_request(self, asset_id: str, key_id: str) -> bytes:
        return bytes([1, 2, 3])

    def insert_license(self, license: bytes) -> None:
        self.license_data = license

    # TODO add output/decoding settings

    def decrypt_content(self, content: bytes) -> Optional[bytes]:
        if self.license_data is None:
            return None
        return bytes(map(lambda x: x ^ 0x55, content))
