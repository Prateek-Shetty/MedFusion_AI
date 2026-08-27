from typing import List

from google import genai

from app.config import settings


class GeminiService:
    """
    Gemini API service with 3-key fallback.

    Key 1 -> Key 2 -> Key 3

    The service only falls back when the current
    Gemini request fails.
    """

    def __init__(self):
        self.model = settings.GEMINI_MODEL

        self.api_keys: List[str] = [
            key
            for key in [
                settings.GEMINI_API_KEY_1,
                settings.GEMINI_API_KEY_2,
                settings.GEMINI_API_KEY_3,
            ]
            if key
        ]

        if not self.api_keys:
            raise RuntimeError(
                "No Gemini API keys configured."
            )

    # ========================================================
    # CLIENT
    # ========================================================

    def _create_client(self, api_key: str):
        return genai.Client(
            api_key=api_key
        )

    # ========================================================
    # TEST
    # ========================================================

    def test_connection(self):

        last_error = None

        for index, api_key in enumerate(
            self.api_keys,
            start=1
        ):

            try:

                print(
                    f"[Gemini] Trying API key {index}..."
                )

                client = self._create_client(
                    api_key
                )

                response = client.models.generate_content(
                    model=self.model,
                    contents=(
                        "Reply with exactly: "
                        "Gemini connection successful."
                    ),
                )

                print(
                    f"[Gemini] API key {index} successful."
                )

                return {
                    "success": True,
                    "key_used": index,
                    "model": self.model,
                    "response": response.text,
                }

            except Exception as error:

                last_error = error

                print(
                    f"[Gemini] API key {index} failed: "
                    f"{type(error).__name__}"
                )

                continue

        raise RuntimeError(
            "All configured Gemini API keys failed."
        ) from last_error


# ============================================================
# SINGLE SERVICE INSTANCE
# ============================================================

gemini_service = GeminiService()