import json
import subprocess
from pathlib import Path
from typing import Any, List, Tuple

from config import settings


def read_json(json_path: Path) -> Any:
    with json_path.open("r") as file:
        json_content = json.load(file)
    return json_content


def write_json(json_path: Path, json_content: Any) -> None:
    with json_path.open("w") as file:
        json.dump(json_content, file, indent=2)


def get_free_port() -> List[int]:
    config = read_json(settings.config)

    use_port_list = [item["port"] for item in config["inbounds"]]
    port_list = set((range(443, 453)))

    return sorted(port_list.difference(use_port_list))


def get_id() -> str:
    result = subprocess.Popen(
        ["/usr/local/bin/xray", "uuid"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.communicate()[0][:-1]


def get_keys() -> Tuple[str, str]:
    result = subprocess.Popen(
        ["/usr/local/bin/xray", "x25519"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = result.communicate()

    return (stdout.split("\n")[0][13:], stdout.split("\n")[1][12:])


def get_short_ids() -> str:
    result = subprocess.Popen(
        ["openssl", "rand", "-hex", "8"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return result.communicate()[0][:-1]


def xray_restart():
    subprocess.run(["systemctl", "restart", "xray.service"])
