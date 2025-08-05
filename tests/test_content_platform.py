from fastapi.testclient import TestClient
import jwt
from pydantic import TypeAdapter
import pytest

from shared.domain import EntitlementMessage, EntitlementResponse, EntitlementTokenData
from .mocks import MockKeyServerSettings, MockCatalogRepo


def test_status(content_platform_client: TestClient) -> None:
    response = content_platform_client.get("/status")
    assert response.status_code == 200
    assert response.json() == {"operational": True, "status": "OK"}


@pytest.mark.parametrize(
    "expect_success,item_id",
    [
        (True, "1"),
        (True, "2"),
        (False, "3"),
    ],
)
def test_catalog_get(
    content_platform_client: TestClient, expect_success: bool, item_id: str
) -> None:
    response = content_platform_client.get(f"/catalog/{item_id}")

    if expect_success:
        assert response.status_code == 200
        assert response.json() == MockCatalogRepo.catalog[item_id].model_dump()
    else:
        assert response.status_code == 404


def test_entitlement_acquire(content_platform_client: TestClient) -> None:
    response = content_platform_client.post(
        "/entitlement",
        json=EntitlementMessage(asset_id="1", usage_type="playback").model_dump(),
    )
    assert response.status_code == 200

    entitlement_response = TypeAdapter(EntitlementResponse).validate_python(
        response.json()
    )
    token_data_raw = jwt.decode(
        entitlement_response.token,
        MockKeyServerSettings().JWT_PUBKEY,
        algorithms=["EdDSA"],
    )
    token_data = TypeAdapter(EntitlementTokenData).validate_python(token_data_raw)

    assert token_data.good is True
