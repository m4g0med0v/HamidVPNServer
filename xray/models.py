from dataclasses import dataclass
from typing import Any, List


@dataclass
class Log:
    access: str
    error: str
    loglevel: str


@dataclass
class Client:
    id: str
    email: str
    flow: str
    limit: int


@dataclass
class Settings:
    clients: List[Client]
    decryption: str


@dataclass
class RealitySettings:
    dest: str
    serverNames: List[str]
    privateKey: str
    shortIds: List[str]


@dataclass
class StreamSettings:
    network: str
    security: str
    realitySettings: RealitySettings


@dataclass
class Sniffing:
    enabled: bool
    destOverride: List[str]
    routeOnly: bool


@dataclass
class Inbound:
    port: int
    protocol: str
    settings: Settings
    streamSettings: StreamSettings
    sniffing: Sniffing


@dataclass
class Outbound:
    protocol: str
    tag: str


@dataclass
class Config:
    log: Log
    inbounds: List[Inbound]
    outbounds: List[Outbound]


@dataclass
class User:
    uuid: str
    shortuuid: str
    email: str
    link: str


@dataclass
class XrayResponse:
    status: str
    context: Any
