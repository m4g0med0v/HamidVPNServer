from authx import AuthX, AuthXConfig

from src.config import settings

config = AuthXConfig()
config.JWT_SECRET_KEY = settings.api.jwt_secret_key
config.JWT_ACCESS_COOKIE_NAME = "access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]

security = AuthX(config=config)
