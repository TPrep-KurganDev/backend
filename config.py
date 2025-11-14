from pathlib import Path

from pydantic_settings import SettingsConfigDict, BaseSettings
from pydantic import Field, computed_field


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).parent / ".env",
        env_file_encoding="utf-8"
    )

    DB_USER: str = "postgres"
    DB_PASSWORD: str
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "tprep_db"

    SECRET_KEY: str = Field(..., description="Secret key for JWT encoding")
    ALGORITHM: str = Field(default="HS256", description="JWT algorithm")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=60, description="Access token expiry in minutes")

    BCRYPT_SCHEME: str = Field(default="bcrypt", description="Hashing scheme for passwords")

    VAPID_PRIVATE_KEY: str = Field(..., description="VAPID private key for WebPush")
    VAPID_PUBLIC_KEY: str = Field(..., description="VAPID public key for WebPush")
    VAPID_CLAIMS_SUB: str = Field(
        default="mailto:notifications@myapp.com",
        description="Subject email for VAPID claims"
    )

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    @computed_field
    @property
    def VAPID_CLAIMS(self) -> dict[str, str]:
        return {"sub": self.VAPID_CLAIMS_SUB}


settings = Settings()