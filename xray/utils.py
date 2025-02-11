import json
import subprocess
from typing import Any


def get_short_uuid():
    """Выдает уникальный короткий UUID"""
    result = subprocess.Popen(
        ["openssl", "rand", "-hex", "8"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    answer = result.communicate()
    return answer[0][:-1]


def get_uuid():
    """Выдает уникальный UUID"""
    result = subprocess.Popen(
        ["/usr/local/bin/xray", "uuid"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    answer = result.communicate()
    return answer[0][:-1]


def get_keys():
    """Выдает PrivateKey и PublicKey"""
    result = subprocess.Popen(
        ["/usr/local/bin/xray", "x25519"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    answer = result.communicate()
    return (
        answer[0][:-1]
        .replace("Private key: ", "")
        .replace("Public key: ", "")
        .split("\n")
    )


def load_json(json_path: str) -> Any:
    """Загружает json файл."""
    try:
        with open(json_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise RuntimeError(f"Ошибка загрузки конфигурации: {e}")


def save_json(json_file, json_path) -> None:
    """Сохраняет изменения в json файл."""
    with open(json_path, "w", encoding="utf-8") as file:
        json.dump(json_file, file, indent=4)
