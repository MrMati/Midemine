# Responsibilities:

# Processing license requests into licenses


# Receiving content keys from packager


# Some management interface

## packager interface might be a part of it

from typing import Optional, Annotated

from pydantic import TypeAdapter, ValidationError
from pydantic_settings import BaseSettings, SettingsConfigDict
import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from fastapi import FastAPI, Header, Request
from fastapi.responses import Response
from fastapi.security.utils import get_authorization_scheme_param

from shared.domain import EntitlementTokenData


app = FastAPI()


def extract_token(authorization_header: Optional[str]) -> Optional[str]:
    scheme, token = get_authorization_scheme_param(authorization_header)
    if scheme.lower() != "bearer" or not token:
        return None
    return token


class Settings(BaseSettings):
    JWT_PUBKEY: str
    model_config = SettingsConfigDict(env_file=(".env", ".env.prod"))


# TODO consider fastapi's DI
settings = Settings()  # type: ignore


@app.post("/acquire_license")
async def acquire_license(
    request: Request,
    auth: Annotated[Optional[str], Header(alias="Authorization")] = None,
):
    license_req = await request.body()
    if (token := extract_token(auth)) is None:
        return Response(status_code=401)

    try:
        token_data_raw = jwt.decode(token, settings.JWT_PUBKEY, algorithms=["EdDSA"])
        token_data = TypeAdapter(EntitlementTokenData).validate_python(token_data_raw)
    except (ExpiredSignatureError, InvalidTokenError):
        return Response(status_code=401)
    except ValidationError:
        return Response(status_code=400)

    if len(license_req) != 3 or not token_data.good:
        return Response(status_code=400)

    return Response(
        content=b"good-license", media_type="application/octet-stream", status_code=200
    )
