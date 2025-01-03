import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    config: Path
    wait_list: Path
    server_ip: str
    main_server_ip: str


settings = Settings(
    config=Path(os.getenv("CONFIG")),
    wait_list=Path(os.getenv("WAIT_LIST")),
    server_ip=os.getenv("SERVER_IP"),
    main_server_ip=os.getenv("MAIN_SERVER_IP"),
)
