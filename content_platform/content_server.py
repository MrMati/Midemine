# Responsibilities:

# - Provide info about available content and details
# - Serve content

# Management interface

from fastapi import FastAPI
from fastapi.responses import Response, StreamingResponse


from shared.domain import (
    StreamingServiceStatus,
    EntitlementMessage,
    EntitlementResponse,
    JWT,
)
from .repos import CatalogRepo, AssetDataRepo

app = FastAPI()


@app.get("/")
def root():
    return Response("Welcome to content platform\n***In construction***")


@app.get("/status", status_code=200)
def get_status():
    return StreamingServiceStatus(operational=True, status="OK")


@app.get("/catalog/{asset_id}", status_code=200)
def read_catalog_item(asset_id: str):
    return CatalogRepo.get_asset_info(asset_id) or Response(status_code=404)


@app.get("/assets/{asset_id}", status_code=200)
def read_alternatives(asset_id: str):
    if (stream := AssetDataRepo.get_asset_stream(asset_id)) is None:
        return Response(status_code=404)
    
    return StreamingResponse(stream, media_type="application/octet-stream")


@app.post("/entitlement", status_code=200)
def get_entitlement(entl_msg: EntitlementMessage):
    print(entl_msg)
    if not CatalogRepo.check_asset_exists(
        entl_msg.asset_id
    ) or entl_msg.usage_type not in ["playback", "offline"]:
        return Response(status_code=406)
    
    return EntitlementResponse(claims=[], jwt=JWT("good-jwt"))
