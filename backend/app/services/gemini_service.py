from google import genai

from app.config import settings


if not settings.GEMINI_API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is not configured."
    )


client = genai.Client(
    api_key=settings.GEMINI_API_KEY
)


def test_gemini():
    response = client.models.generate_content(
        model=settings.GEMINI_MODEL,
        contents="Reply with exactly: Gemini connection successful."
    )

    return response.text