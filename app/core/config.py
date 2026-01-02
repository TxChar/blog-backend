import hashlib

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Literal
from pydantic import BaseModel, Field, SecretStr

DEV_PRIVATE_KEY = "53896c44216ef5e80a7a9dc46397f9a1ee663ad2f4e0af78e74ea15d920ec9c9"
DEV_PUBLIC_KEY = "5473a0654e21df90e0944dd40b82bb631d9a779a6d9c6beee493d47581f43847"


def calculate_file_checksum(filepath, algorithm: str = "sha256") -> str:
    """
    Calculates the checksum of a file using the specified algorithm.

    Args:
        filepath (str): The path to the file.
        algorithm (str): The hashing algorithm to use (e.g., 'md5', 'sha1', 'sha256').

    Returns:
        str: The hexadecimal representation of the file's checksum.

    Raises:
        ValueError: If the algorithm is not supported by hashlib.
        FileNotFoundError: If the file does not exist.
    """
    try:
        hash_func = getattr(hashlib, algorithm)()
    except AttributeError:
        raise ValueError(
            f"Unsupported algorithm: {algorithm}. Use one of {hashlib.algorithms_available}"
        )

    with open(filepath, "rb") as f:
        for chunk in iter(lambda: f.read(2048), b""):
            hash_func.update(chunk)
    return hash_func.hexdigest()


def compare_checksums(private_key_file_path: str, public_key_file_path: str):
    """ """
    if (calculate_file_checksum(private_key_file_path) == DEV_PRIVATE_KEY) and (
        calculate_file_checksum(public_key_file_path) == DEV_PUBLIC_KEY
    ):
        print(
            "\033[91mUse DEV keys only allowed for environment LOCAL and DEV. Create a new PRIVATE and PUBLIC key pair for STAGING or PROD\033[0m"
        )
        return False


def mask_secret(secret: str) -> str:
    """Mask secret values, showing only first char and last 3 chars."""
    if not secret:
        return ""
    if len(secret) <= 4:
        return "*" * len(secret)
    return f"{secret[:2]}****{secret[-2:]}"


class Settings(BaseSettings):
    """Application configuration settings"""

    model_config = SettingsConfigDict(
        env_file=(".env", ".env.local"),
        env_prefix="APP_",
        env_nested_delimiter="__",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "MyBlog Backend"
    version: str = "LOCAL"
    environment: Literal["LOCAL", "DEV", "STAGING", "PROD"] = "LOCAL"
    host: str = "0.0.0.0"
    port: int = 8000

    log_level: Literal["DEBUG", "ERROR",
                       "WARNING", "INFO", "CRITICAL"] = "DEBUG"

    allow_origins: List[str] = Field(default_factory=lambda: ["*"])

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

    def validation_check(self) -> None:
        settings_dict = dict(self.model_dump().items())
        if settings_dict["environment"] != "LOCAL":
            if settings_dict["version"] == "DEV":
                print("\033[91mVersion DEV is only allowed for LOCAL\033[0m")
                return False
            if settings_dict["allow_origins"] == ["*"]:
                print(
                    "\033[91mallow_origins ['*'] is only allowed for LOCAL\033[0m")
                return False

        if settings_dict["environment"] not in ["DEV", "LOCAL"]:
            return compare_checksums(
                settings_dict["jwt_private_key_path"],
                settings_dict["jwt_public_key_path"],
            )
        return True

    def pretty_print(self) -> None:
        """Print settings with secrets masked."""

        def serialize_value(v):
            if isinstance(v, SecretStr):
                return mask_secret(v.get_secret_value())
            if isinstance(v, dict):
                return {k: serialize_value(v[k]) for k in v.keys()}
            return v

        def print_nested(key, value, indent=0):
            prefix = " " * indent
            if isinstance(value, dict):
                print(f"{prefix}{key}:")
                for k, v in value.items():
                    print_nested(k, v, indent + 4)
            else:
                print(f"{prefix}{key}: {value}")

        data = {k: serialize_value(v) for k, v in self.model_dump().items()}
        print("=== Application Settings ===")
        for k, v in data.items():
            print_nested(k, v)
        print("============================")


settings = Settings()
