import uuid
from typing import Any

from fastapi import Depends, FastAPI, HTTPException, Response

from src.auth import config, security
from src.config import settings
from src.models import AdminSchema
from xray import Xray
from xray.models import XrayResponse

app = FastAPI()
xray = Xray(
    server_ip=settings.server_ip,
    pbk_key=settings.xray.public_key,
    config_path="config.json",
    freeze_path="freeze.json",
)


@app.post("/api/login")
def login(creds: AdminSchema, response: Response) -> Any:
    if (
        creds.username == settings.api.admin_name
        and creds.password == settings.api.admin_password
    ):
        token = security.create_access_token(uid=str(uuid.uuid4()))
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
        return {"access_token": token}
    raise HTTPException(
        status_code=401, detail="Incorrect username or password"
    )


@app.get("/api/links/", dependencies=[Depends(security.access_token_required)])
def get_links() -> XrayResponse:
    return xray.get_links()


@app.get(
    "/api/links/config", dependencies=[Depends(security.access_token_required)]
)
def get_config_links() -> XrayResponse:
    return xray.get_config_links()


@app.get(
    "/api/links/freeze", dependencies=[Depends(security.access_token_required)]
)
def get_freeze_links() -> XrayResponse:
    return xray.get_freeze_links()


@app.post(
    "/api/links/create_link",
    dependencies=[Depends(security.access_token_required)],
)
def create_link(tg_name: str, tg_id: str) -> XrayResponse:
    return xray.create_link(tg_name=tg_name, tg_id=tg_id)


@app.post(
    "/api/links/delete_link",
    dependencies=[Depends(security.access_token_required)],
)
def delete_link(short_id: str) -> XrayResponse:
    return xray.delete_link(short_id=short_id)


@app.post(
    "/api/links/freeze_link",
    dependencies=[Depends(security.access_token_required)],
)
def freeze_link(short_id: str) -> XrayResponse:
    return xray.freeze_link(short_id=short_id)


@app.post(
    "/api/links/unfreeze_link",
    dependencies=[Depends(security.access_token_required)],
)
def unfreeze_link(short_id: str) -> XrayResponse:
    return xray.unfreeze_link(short_id=short_id)
