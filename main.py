from fastapi import FastAPI, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.cors import CORSMiddleware

from config import settings
from handlers import (
    get_free_port,
    get_id,
    get_keys,
    get_short_ids,
    read_json,
    write_json,
    xray_restart,
)
from models import VlessConfig

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[f"http://{settings.main_server_ip}"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class IPFilterMiddleware(BaseHTTPMiddleware):
    def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        if client_ip != settings.main_server_ip:
            raise HTTPException(
                status_code=403,
                detail="Access denied: unauthorized IP address.",
            )
        return call_next(request)


app.add_middleware(IPFilterMiddleware)


@app.get("/links")
def get_links():
    config = read_json(settings.config)
    return config["inbounds"]


@app.get("/wait_links")
def get_pools():
    wait_list = read_json(settings.wait_list)
    return wait_list


@app.post("/link/create")
def create_link(mes_id, mes_name):
    port_list = get_free_port()

    if not port_list:
        return {"Error": "Нет свободных портов."}

    id = get_id()
    port = port_list[0]
    pvk, pbk = get_keys()
    short_ids = get_short_ids()

    vless_config = VlessConfig(
        port=port,
        id=id,
        mes_id=mes_id,
        mes_name=mes_name,
        pvk=pvk,
        pbk=pbk,
        short_ids=short_ids,
    )

    config = read_json(settings.config)
    config["inbounds"].append(vless_config.to_json())
    write_json(settings.config, config)

    xray_restart()

    return vless_config


@app.delete("/link/delete")
def delete_link(port: int):
    config = read_json(settings.config)

    links = config["inbounds"]
    links = [link for link in links if link.get("port") != port]
    config["inbounds"] = links

    write_json(settings.config, config)

    xray_restart()

    return {"Successful": "Ok"}


@app.post("/link/remove")
def move_link_to_pool(port: int):
    config = read_json(settings.config)

    links = config["inbounds"]
    try:
        link = [link for link in links if link.get("port") == port][0]
    except Exception:
        return {"Error": "Объекта с таким портор не существует."}

    wait_list = read_json(settings.wait_list)
    wait_list.append(link)
    write_json(settings.wait_list, wait_list)

    config["inbounds"] = [link for link in links if link.get("port") != port]

    write_json(settings.config, config)

    xray_restart()

    return {"Successful": "Ok"}


@app.post("/link/add")
def move_link_to_config(port: int):
    wait_list = read_json(settings.wait_list)

    try:
        wait_link = [item for item in wait_list if item.get("port") == port][0]
    except Exception:
        return {"Error": "Объекта с таким портор не существует."}

    config = read_json(settings.config)
    config["inbounds"].append(wait_link)

    write_json(settings.config, config)

    wait_list = [item for item in wait_list if item.get("port") != port]

    write_json(settings.wait_list, wait_list)

    xray_restart()

    return {"Successful": "Ok"}
