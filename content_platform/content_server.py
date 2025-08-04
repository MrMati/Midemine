# Responsibilities:

# - Provide info about available content and details
# - Serve content

# Management interface

from fastapi import FastAPI
from fastapi.responses import Response, StreamingResponse
from datetime import datetime, timedelta, timezone
import jwt

from shared.domain import (
    StreamingServiceStatus,
    EntitlementMessage,
    EntitlementResponse,
    JWT,
    EntitlementTokenData,
)
from .deps import CatalogRepoDep, AssetDataRepoDep, SettingsDep

app = FastAPI()


@app.get("/")
def root():
    return Response("Welcome to content platform\n***In construction***")


@app.get("/status", status_code=200)
def get_status():
    return StreamingServiceStatus(operational=True, status="OK")


@app.get("/catalog/{asset_id}", status_code=200)
def read_catalog_item(asset_id: str, catalog_repo: CatalogRepoDep):
    return catalog_repo.get_asset_info(asset_id) or Response(status_code=404)


@app.get("/assets/{asset_id}", status_code=200)
def read_alternatives(asset_id: str, asset_data_repo: AssetDataRepoDep):
    if (stream := asset_data_repo.get_asset_stream(asset_id)) is None:
        return Response(status_code=404)

    return StreamingResponse(stream, media_type="application/octet-stream")


def create_access_token(data: dict, expires_delta: timedelta, jwt_privkey: str) -> JWT:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode.update({"exp": expire})
    encoded_token = jwt.encode(to_encode, jwt_privkey, algorithm="EdDSA")
    return JWT(encoded_token)


@app.post("/entitlement", status_code=200)
def get_entitlement(
    entl_msg: EntitlementMessage, catalog_repo: CatalogRepoDep, settings: SettingsDep
):
    if not catalog_repo.check_asset_exists(
        entl_msg.asset_id
    ) or entl_msg.usage_type not in ["playback", "offline"]:
        return Response(status_code=406)

    # TODO different usage types have different needs

    token_data = EntitlementTokenData(good=True).model_dump()

    encoded_entl_msg = create_access_token(
        data=token_data,
        expires_delta=timedelta(minutes=30),  # FIXME magic number
        jwt_privkey=settings.JWT_PRIVKEY,
    )

    return EntitlementResponse(claims=[], token=encoded_entl_msg)
