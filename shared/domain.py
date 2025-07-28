from enum import Enum
from typing import List, NewType
from pydantic import BaseModel

class StreamingServiceStatus(BaseModel):
    operational: bool
    status: str


# TODO consider a nested structure with exact media container/encoding info
class MediaType(str, Enum):
    audio = "audio"
    image = "image"
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