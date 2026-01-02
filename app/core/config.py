from typing_extensions import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    app_name: str = "MyBlog Backend"
    environment: str = "development"
    host: str = "0.0.0.0"
    port: int = 8000

    log_level: Literal["DEBUG", "ERROR",
                       "WARNING", "INFO", "CRITICAL"] = "DEBUG"

    mongo_uri: str = "mongodb://localhost:27017"
    mongo_db: str = "myblog"

    # File Paths
    input_path: str = "input/"
    jwt_private_key_path: str = input_path + "keys/private_key.pem"
    jwt_public_key_path: str = input_path + "keys/public_key.pem"

    # JWE Token Settings (RSA-OAEP-256 + A192GCM)
    jwt_algorithm: str = "RSA-OAEP-256"  # JWE key encryption algorithm
    jwt_encryption: str = "A192GCM"       # JWE content encryption algorithm
    access_token_expire_minutes: int = 1440  # 24 hours

    model_config = SettingsConfigDict(
        env_file=".env",
        env_ignore_empty=True,
    )


settings = Settings()
