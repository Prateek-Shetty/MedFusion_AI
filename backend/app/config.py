from pathlib import Path
import os

from dotenv import load_dotenv


# Backend root directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from .env
load_dotenv(BASE_DIR / ".env")


class Settings:
    APP_NAME: str = os.getenv(
        "APP_NAME",
        "MedFusion AI Backend"
    )

    APP_VERSION: str = os.getenv(
        "APP_VERSION",
        "1.0.0"
    )

    ENVIRONMENT: str = os.getenv(
        "ENVIRONMENT",
        "development"
    )

    HOST: str = os.getenv(
        "HOST",
        "127.0.0.1"
    )

    PORT: int = int(
        os.getenv(
            "PORT",
            "8000"
        )
    )

    MAX_UPLOAD_SIZE_MB: int = int(
        os.getenv(
            "MAX_UPLOAD_SIZE_MB",
            "10"
        )
    )


settings = Settings()