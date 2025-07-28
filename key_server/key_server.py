
# Responsibilities:

# Processing license requests into licenses


# Receiving content keys from packager


# Some management interface

## packager interface might be a part of it


from fastapi import FastAPI, Header, Request
from fastapi.responses import Response
from typing import Annotated

app = FastAPI()

@app.post("/acquire_license")
async def acquire_license(request: Request, authorization: Annotated[str | None, Header()] = None):
    license_req = await request.body()
    if authorization is None or authorization != "Bearer good-jwt": # TODO use JWT library
        return Response(status_code=401)
    
    if len(license_req) != 3:
        return Response(status_code=400)
    
    return Response(content = b"good-license", media_type="application/octet-stream", status_code=200)