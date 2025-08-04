from datetime import timedelta

from fastapi.testclient import TestClient

from .conftest import OverridePlatformSettings

from content_platform.content_server import create_access_token
from shared.domain import EntitlementTokenData


def do_license_acquire(
    key_server_client: TestClient,
    expect_status: int = 200,
    bad_token_format: bool = False,
    good: bool = True,
    delta_minutes: int = 30,
    bad_lic_req: bool = False,
    auth_type: str = "Bearer",
) -> None:
    token_data = EntitlementTokenData(good=good).model_dump()

    encoded_entl_msg = create_access_token(
        data={} if bad_token_format else token_data,
        expires_delta=timedelta(minutes=delta_minutes),
        jwt_privkey=OverridePlatformSettings().JWT_PRIVKEY,
    )

    license_request = bytes([1]) if bad_lic_req else bytes([1, 2, 3])

    response = key_server_client.post(
        "/acquire_license",
        content=license_request,
        headers={"Authorization": f"{auth_type} {encoded_entl_msg}"},
    )

    assert response.status_code == expect_status

    if expect_status == 200:
        assert response.content == b"good-license"


def test_license_acquire_success(key_server_client: TestClient):
    do_license_acquire(key_server_client)


def test_license_acquire_bad_token_format(key_server_client: TestClient):
    do_license_acquire(key_server_client, bad_token_format=True, expect_status=400)


def test_license_acquire_bad_token_values(key_server_client: TestClient):
    do_license_acquire(key_server_client, good=False, expect_status=400)


def test_license_acquire_expired(key_server_client: TestClient):
    do_license_acquire(key_server_client, delta_minutes=-1, expect_status=401)


def test_license_acquire_bad_lic_req(key_server_client: TestClient):
    do_license_acquire(key_server_client, bad_lic_req=True, expect_status=400)


def test_license_acquire_bad_auth(key_server_client: TestClient):
    do_license_acquire(key_server_client, auth_type="Token", expect_status=401)
