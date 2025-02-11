import subprocess

from .models import User, XrayResponse
from .utils import get_short_uuid, get_uuid, load_json, save_json


class Xray:
    CONFIG_PATH = "/usr/local/etc/xray/config.json"
    FREEZE_PATH = "/usr/local/etc/xray/freeze.json"

    def __init__(
        self,
        server_ip: str,
        pbk_key: str,
        config_path: str = CONFIG_PATH,
        freeze_path: str = FREEZE_PATH,
    ):
        self.server_ip = server_ip
        self.pbk_key = pbk_key
        self.config_path = config_path
        self.freeze_path = freeze_path

    def __restart_xray(self) -> None:
        """Перезапускает сервис Xray."""
        try:
            subprocess.run(["systemctl", "restart", "xray"], check=True)
        except subprocess.SubprocessError as e:
            print(f"Ошибка при перезапуске Xray: {e}")

    def __generate_link(self, user_uuid: str, short_uuid: str) -> str:
        return (
            f"vless://{user_uuid}@{self.server_ip}:443?"
            f"security=reality&encryption=none&pbk={self.pbk_key}"
            f"&headerType=none&fp=none&type=tcp&flow=xtls-rprx-vision"
            f"&sni=cloudflare.com&sid={short_uuid}# HamidVPN ☝️"
        )

    def create_link(self, tg_name: str, tg_id: str) -> XrayResponse:
        """Создаёт proxy."""
        config = load_json(self.config_path)
        user_uuid = get_uuid()
        short_uuid = get_short_uuid()
        email = f"{tg_name}.{tg_id}@hamidvpn.org"

        inbound = config["inbounds"][0]
        inbound["settings"]["clients"].append(
            {
                "id": user_uuid,
                "email": f"{tg_name}.{tg_id}@hamidvpn.org",
                "flow": "xtls-rprx-vision",
                "limit": 1,
            }
        )
        inbound["streamSettings"]["realitySettings"]["shortIds"].append(
            short_uuid
        )

        save_json(config, self.config_path)
        # self.__restart_xray()

        return XrayResponse(
            status="ok",
            context=User(
                uuid=user_uuid,
                shortuuid=short_uuid,
                email=email,
                link=self.__generate_link(
                    user_uuid=user_uuid, short_uuid=short_uuid
                ),
            ),
        )

    def delete_link(self, short_id: str) -> XrayResponse:
        """Удаляет proxy."""
        freeze = load_json(self.freeze_path)

        if short_id in freeze:
            freeze.pop(short_id)
            save_json(freeze, self.freeze_path)

            return XrayResponse(
                status="ok",
                context=f"Ссылка {short_id} удалена из freeze.json",
            )

        config = load_json(self.config_path)
        inbound = config["inbounds"][0]
        short_ids = inbound["streamSettings"]["realitySettings"]["shortIds"]

        if short_id not in short_ids:
            return XrayResponse(
                status="error", context=f"Ссылка {short_id} не найдена."
            )

        idx = short_ids.index(short_id)

        inbound["settings"]["clients"].pop(idx)
        short_ids.pop(idx)

        save_json(config, self.config_path)
        # self.__restart_xray()

        return XrayResponse(
            status="ok", context=f"Ссылка {short_id} удалена из config.json"
        )

    def freeze_link(self, short_id: str) -> XrayResponse:
        """Замораживает proxy."""
        config = load_json(self.config_path)
        freeze = load_json(self.freeze_path)
        inbound = config["inbounds"][0]
        short_ids = inbound["streamSettings"]["realitySettings"]["shortIds"]

        if short_id not in short_ids:
            return XrayResponse(
                status="error", context=f"Ссылка {short_id} не найдена."
            )

        idx = short_ids.index(short_id)

        user_config = inbound["settings"]["clients"].pop(idx)
        short_ids.pop(idx)
        freeze[short_id] = user_config

        save_json(freeze, self.freeze_path)
        save_json(config, self.config_path)
        # self.__restart_xray()

        return XrayResponse(
            status="ok", context=f"Ссылка {short_id} перемещена в freeze.json"
        )

    def unfreeze_link(self, short_id: str) -> XrayResponse:
        """Размораживает proxy."""
        config = load_json(self.config_path)
        freeze = load_json(self.freeze_path)
        inbound = config["inbounds"][0]

        if short_id not in freeze:
            return XrayResponse(
                status="error", context=f"Ссылка {short_id} не найдена."
            )

        user_config = freeze.pop(short_id)

        inbound["settings"]["clients"].append(user_config)
        inbound["streamSettings"]["realitySettings"]["shortIds"].append(
            short_id
        )

        save_json(config, self.config_path)
        save_json(freeze, self.freeze_path)
        # self.__restart_xray()

        return XrayResponse(
            status="ok", context=f"Ссылка {short_id} перемещена в config.json"
        )

    def get_config_links(self) -> XrayResponse:
        """Возвращает список действующих proxy по short_id."""
        config = load_json(self.config_path)
        inbound = config["inbounds"][0]
        client_list = inbound["settings"]["clients"]
        short_ids = inbound["streamSettings"]["realitySettings"]["shortIds"]
        users = {}
        for short_id, client in zip(short_ids, client_list):
            users[short_id] = {
                "id": client["id"],
                "email": client["email"],
                "ip": self.server_ip,
                "link": self.__generate_link(
                    user_uuid=client["id"], short_uuid=short_id
                ),
            }

        return XrayResponse(status="ok", context=users)

    def get_freeze_links(self) -> XrayResponse:
        """Возвращает список замороженных proxy по short_id."""
        freeze = load_json(self.freeze_path)
        users = {}
        for short_id in list(freeze.keys()):
            users[short_id] = {
                "id": freeze[short_id]["id"],
                "email": freeze[short_id]["email"],
                "ip": self.server_ip,
                "link": self.__generate_link(
                    user_uuid=freeze[short_id]["id"], short_uuid=short_id
                ),
            }

        return XrayResponse(status="ok", context=users)

    def get_links(self) -> XrayResponse:
        """Возвращает весь список proxy по email."""
        config = load_json(self.config_path)
        freeze = load_json(self.freeze_path)
        inbound = config["inbounds"][0]
        client_list = inbound["settings"]["clients"]
        short_ids = inbound["streamSettings"]["realitySettings"]["shortIds"]
        users = {}
        for short_id, client in zip(short_ids, client_list):
            if not users.get(client["email"]):
                users[client["email"]] = {"config": [], "freeze": []}

            users[client["email"]]["config"].append(
                {
                    "id": client["id"],
                    "shortId": short_id,
                    "ip": self.server_ip,
                    "link": self.__generate_link(
                        user_uuid=client["id"], short_uuid=short_id
                    ),
                }
            )

        for short_id in list(freeze.keys()):
            if not users.get(freeze[short_id]["email"]):
                users[freeze[short_id]["email"]] = {"config": [], "freeze": []}

            users[freeze[short_id]["email"]]["freeze"].append(
                {
                    "id": freeze[short_id]["id"],
                    "shortId": short_id,
                    "ip": self.server_ip,
                    "link": self.__generate_link(
                        user_uuid=freeze[short_id]["id"], short_uuid=short_id
                    ),
                }
            )

        return XrayResponse(status="ok", context=users)


if __name__ == "__main__":
    xray = Xray(
        server_ip="123.123.123.132",
        pbk_key="15678987654323456787654",
        config_path="config.json",
        freeze_path="freeze.json",
    )

    config = load_json("config.json")
    config["inbounds"][0]["settings"]["clients"] = []
    config["inbounds"][0]["streamSettings"]["realitySettings"]["shortIds"] = []
    save_json(config, xray.config_path)

    telegram_usernames = [
        "alpha_wolf",
        "beta_coder",
        "gamma_ray",
        "delta_force",
        "epsilon_hawk",
        "zeta_shadow",
        "eta_master",
        "theta_x",
        "iota_knight",
        "kappa_ninja",
        "lambda_hero",
        "mu_sentinel",
        "nu_guardian",
        "xi_phantom",
        "omicron_vortex",
        "pi_ranger",
        "rho_dragon",
        "sigma_tiger",
        "tau_eagle",
        "upsilon_fox",
        "phi_samurai",
        "chi_sniper",
        "psi_cyber",
        "omega_ghost",
        "stealth_hawk",
        "shadow_warrior",
        "iron_guard",
        "dark_matter",
        "quantum_nexus",
        "cyber_wolf",
        "neo_shadow",
        "hacker_404",
        "echo_blade",
        "phantom_striker",
        "matrix_pilot",
        "nova_falcon",
        "tactical_snake",
        "blackout_x",
        "storm_rider",
        "midnight_raven",
        "venom_knight",
        "frost_reaper",
        "crimson_fang",
        "warp_drive",
        "vortex_coder",
        "silent_assassin",
        "gamma_falcon",
        "cyber_glitch",
        "dark_knight_x",
        "neon_shifter",
    ]

    for idx, name in enumerate(telegram_usernames):
        xray.create_link(tg_id=idx, tg_name=name)

    save_json({}, xray.freeze_path)

    config = load_json(xray.config_path)
    short_ids = config["inbounds"][0]["streamSettings"]["realitySettings"][
        "shortIds"
    ]

    xray.freeze_link(short_ids[5])  # 0
    xray.freeze_link(short_ids[3])  # 1
    xray.freeze_link(short_ids[7])  # 2
    xray.freeze_link(short_ids[10])  # 3
    xray.freeze_link(short_ids[16])  # 4
    xray.freeze_link(short_ids[27])  # 5

    freeze = load_json(xray.freeze_path)
    freeze_list = list(freeze.keys())
    xray.unfreeze_link(freeze_list[2])
    xray.unfreeze_link(freeze_list[3])

    xray.delete_link(short_id=short_ids[0])

    print(xray.get_config_links())
    print()
    print(xray.get_freeze_links())
    print()
    print(xray.get_links())
