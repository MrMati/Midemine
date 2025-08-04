from fastapi.testclient import TestClient

from shared.domain import EntitlementMessage


def test_status(content_platform_client: TestClient) -> None:
    response = content_platform_client.get("/status")
    assert response.status_code == 200
    assert response.json() == {"operational": True, "status": "OK"}


def test_catalog_get(content_platform_client: TestClient) -> None:
    response = content_platform_client.get("/catalog/1")
    assert response.status_code == 200
    # TODO assert content


def test_entitlement_acquire(content_platform_client: TestClient) -> None:
    response = content_platform_client.post(
        "/entitlement",
        json=EntitlementMessage(asset_id="1", usage_type="playback").model_dump(),
    )
    assert response.status_code == 200
    # TODO assert jwt content
