from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_env: str = "development"
    app_name: str = "CarMarket API"
    api_v1_prefix: str = "/api/v1"
    secret_key: str
    database_url: str
    redis_url: str = "redis://localhost:6379/0"
    cors_origins: str = "http://localhost:3000"

    sms_provider: str = "mock"
    msg91_auth_key: str = ""
    otp_length: int = 6
    otp_expire_minutes: int = 5
    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    s3_endpoint: str = ""
    s3_access_key: str = ""
    s3_secret_key: str = ""
    s3_bucket: str = "carmarket-images"
    s3_public_url: str = ""
    s3_region: str = "us-east-1"

    listing_expiry_days: int = 90

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_development(self) -> bool:
        return self.app_env == "development"


settings = Settings()  # type: ignore[call-arg]
