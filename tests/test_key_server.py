from datetime import timedelta

from fastapi.testclient import TestClient
import pytest

from .conftest import MockPlatformSettings

from content_platform.content_server import create_access_token
from shared.domain import EntitlementTokenData


@pytest.mark.parametrize(
    "bad_token_format,good,delta_minutes,bad_lic_req,auth_type,expect_status",
    [
        (False, True, 30, False, "Bearer", 200),
        (True, True, 30, False, "Bearer", 400),
        (False, False, 30, False, "Bearer", 400),
        (False, True, -1, False, "Bearer", 401),
        (False, True, 30, True, "Bearer", 400),
        (False, True, 30, False, "Token", 401),
    ],
    ids=[
        "success",
        "bad_token_format",
        "bad_token_data",
        "expired",
        "bad_lic_req",
        "bad_auth_type",
    ],
)
def test_license_acquire(
    key_server_client: TestClient,
    bad_token_format: bool,
    good: bool,
    delta_minutes: int,
    bad_lic_req: bool,
    auth_type: str,
    expect_status: int,
) -> None:
    token_data = EntitlementTokenData(good=good).model_dump()

    encoded_entl_msg = create_access_token(
        data={} if bad_token_format else token_data,
        expires_delta=timedelta(minutes=delta_minutes),
        jwt_privkey=MockPlatformSettings().JWT_PRIVKEY,
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
