import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class XraySettings:
    private_key: str
    public_key: str


@dataclass
class ApiSettings:
    admin_name: str
    admin_password: str
    jwt_secret_key: str


@dataclass
class Settings:
    server_ip: str
    xray: XraySettings
    api: ApiSettings


settings = Settings(
    server_ip=os.getenv("SERVER_IP"),
    xray=XraySettings(
        private_key=os.getenv("PRIVATE_KEY"),
        public_key=os.getenv("PUBLIC_KEY"),
    ),
    api=ApiSettings(
        admin_name=os.getenv("ADMIN_NAME"),
        admin_password=os.getenv("ADMIN_PASSWORD"),
        jwt_secret_key=os.getenv("JWT_SECRET_KEY"),
    ),
)
