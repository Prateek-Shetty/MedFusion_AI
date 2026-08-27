from pathlib import Path
import os

from dotenv import load_dotenv


# ============================================================
# BACKEND ROOT DIRECTORY
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv(
    BASE_DIR / ".env"
)


# ============================================================
# SETTINGS
# ============================================================

class Settings:

    # ========================================================
    # APPLICATION
    # ========================================================

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

    # ========================================================
    # SERVER
    # ========================================================

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

    # ========================================================
    # UPLOAD
    # ========================================================

    MAX_UPLOAD_SIZE_MB: int = int(
        os.getenv(
            "MAX_UPLOAD_SIZE_MB",
            "10"
        )
    )

    # ========================================================
    # GEMINI API KEYS
    # ========================================================

    GEMINI_API_KEY_1: str = os.getenv(
        "GEMINI_API_KEY_1",
        ""
    )

    GEMINI_API_KEY_2: str = os.getenv(
        "GEMINI_API_KEY_2",
        ""
    )

    GEMINI_API_KEY_3: str = os.getenv(
        "GEMINI_API_KEY_3",
        ""
    )

    # ========================================================
    # GEMINI MODELS
    #
    # Each API key has its own model configuration.
    # ========================================================

    GEMINI_MODEL_1: str = os.getenv(
        "GEMINI_MODEL_1",
        "gemini-2.5-flash"
    )

    GEMINI_MODEL_2: str = os.getenv(
        "GEMINI_MODEL_2",
        "gemini-3.6-flash"
    )

    GEMINI_MODEL_3: str = os.getenv(
        "GEMINI_MODEL_3",
        "gemini-3.6-flash"
    )


# ============================================================
# SINGLE SETTINGS INSTANCE
# ============================================================

settings = Settings()