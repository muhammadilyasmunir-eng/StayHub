from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    app_name: str = "StayHub API"
    app_version: str = "1.0.0"
    debug: bool = True

    database_url: str
    secret_key: str

    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    usdt_wallet_address: str = ""
    usdt_network: str = "TRC20"

    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        case_sensitive=False,
    )

settings = Settings()