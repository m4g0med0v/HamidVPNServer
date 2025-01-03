from dataclasses import dataclass
from typing import Any, Dict, List

import config


@dataclass
class VlessSettingsClients:
    id: str
    mes_id: int
    mes_name: str
    email: str
    flow: str


@dataclass
class VlessSettings:
    clients: List[VlessSettingsClients]
    decryption: str


@dataclass
class VlessRealitySettings:
    show: bool
    dest: str
    xver: int
    serverNames: List[str]
    privateKey: str
    publicKey: str
    minClientVer: str
    maxClientVer: str
    maxTimeDiff: int | float
    shortIds: List[str]


@dataclass
class VlessStreamSettings:
    network: str
    security: str
    realitySettings: VlessRealitySettings


@dataclass
class VlessSniffing:
    enabled: bool
    destOverride: List[str]


class VlessConfig:
    def __init__(
        self,
        port: int,
        id: str,
        mes_id: str,
        mes_name: str,
        pvk: str,
        pbk: str,
        short_ids: str,
    ) -> None:
        self.port = port
        self.protocol = "vless"
        self.tag = f"vless_tls_{port}"
        self.settings = VlessSettings(
            clients=[
                VlessSettingsClients(
                    id=id,
                    mes_id=mes_id,
                    mes_name=mes_name,
                    email=f"{mes_name}@hamidvpn",
                    flow="xtls-rprx-vision",
                )
            ],
            decryption="none",
        )
        self.streamSettings = VlessStreamSettings(
            network="tcp",
            security="reality",
            realitySettings=VlessRealitySettings(
                show=False,
                dest="cloudflare.com:443",
                xver=0,
                serverNames=["cloudflare.com"],
                privateKey=pvk,
                publicKey=pbk,
                minClientVer="",
                maxClientVer="",
                maxTimeDiff=0,
                shortIds=[short_ids],
            ),
        )
        self.sniffing = VlessSniffing(
            enabled=True, destOverride=["http", "tls"]
        )
        self.link = f"vless://{self.settings.clients[0].id}@{config.settings.server_ip}:{self.port}?security={self.streamSettings.security}&encryption=none&pbk={self.streamSettings.realitySettings.publicKey}&headerType=none&fp=chrome&type={self.streamSettings.network}&flow={self.settings.clients[0].flow}&sni={self.streamSettings.realitySettings.serverNames[0]}&sid={self.streamSettings.realitySettings.shortIds[0]}#HamidVPN [{self.settings.clients[0].mes_id}] [{self.port}]"

    def to_json(self) -> Dict[str, Any]:
        return {
            "port": self.port,
            "protocol": self.protocol,
            "tag": self.tag,
            "settings": {
                "clients": [
                    {
                        "id": item.id,
                        "email": item.email,
                        "flow": item.flow,
                    }
                    for item in self.settings.clients
                ],
                "decryption": self.settings.decryption,
            },
            "streamSettings": {
                "network": self.streamSettings.network,
                "security": self.streamSettings.security,
                "realitySettings": {
                    "show": self.streamSettings.realitySettings.show,
                    "dest": self.streamSettings.realitySettings.dest,
                    "xver": self.streamSettings.realitySettings.xver,
                    "serverNames": self.streamSettings.realitySettings.serverNames,
                    "privateKey": self.streamSettings.realitySettings.privateKey,
                    "minClientVer": self.streamSettings.realitySettings.minClientVer,
                    "maxClientVer": self.streamSettings.realitySettings.maxClientVer,
                    "maxTimeDiff": self.streamSettings.realitySettings.maxTimeDiff,
                    "shortIds": self.streamSettings.realitySettings.shortIds,
                },
            },
            "sniffing": {
                "enabled": self.sniffing.enabled,
                "destOverride": self.sniffing.destOverride,
            },
        }
