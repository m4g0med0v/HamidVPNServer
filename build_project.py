# Создание сервера

# ssh -L 8000:localhost:8000 root@<ip>
# apt update & apt upgrade
# apt install curl mc htop nano git python3.12-venv
# git clone https://github.com/m4g0med0v/HamidVPNServer.git
# cd HamidVPNServer
# python3 -m venv .venv
# source .venv/bin/activate
# pip install -r requirements.txt
# bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install
# systemctl stop xray.service
# cp json_examples/config.json /usr/local/etc/xray/
# cp json_examples/wait_list.json /usr/local/etc/xray/
# systemctl start xray.service
# [create .env]
# uvicorn main:app --reload

# Запуск программы после перезапуска сервера

# cd HamidVPNServer
# source .venv/bin/activate
# uvicorn main:app --port 8000 --host 0.0.0.0 --reload
