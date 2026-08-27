import sys
from pathlib import Path

# Make app importable when running:
# python tests/test_all_gemini.py
sys.path.insert(
    0,
    str(Path(__file__).resolve().parents[1])
)

from google import genai

from app.config import settings


TESTS = [
    (
        "KEY 1",
        settings.GEMINI_API_KEY_1,
        settings.GEMINI_MODEL_1,
    ),
    (
        "KEY 2",
        settings.GEMINI_API_KEY_2,
        settings.GEMINI_MODEL_2,
    ),
    (
        "KEY 3",
        settings.GEMINI_API_KEY_3,
        settings.GEMINI_MODEL_3,
    ),
]


PROMPT = """
You are being tested as part of the MedFusion AI college project.

Explain in 3 short points:

1. What is an MRI?
2. What is a CT scan?
3. What is the main difference between MRI and CT?

Keep the answer concise.
"""


def main():

    print("=" * 70)
    print("MEDFUSION AI — ALL 3 GEMINI API KEY TEST")
    print("=" * 70)

    results = []

    for name, api_key, model in TESTS:

        print()
        print("-" * 70)
        print(name)
        print("Model:", model)

        if not api_key:

            print("STATUS: FAILED")
            print("Reason: API key not configured.")

            results.append(
                (name, model, False)
            )

            continue

        try:

            client = genai.Client(
                api_key=api_key
            )

            print("Sending prompt...")

            response = client.models.generate_content(
                model=model,
                contents=PROMPT,
            )

            text = (
                response.text
                if response.text
                else ""
            )

            print()
            print("STATUS: SUCCESS")
            print("RESPONSE:")
            print(text)

            results.append(
                (name, model, True)
            )

        except Exception as error:

            print()
            print("STATUS: FAILED")
            print(
                "ERROR TYPE:",
                type(error).__name__
            )
            print(
                "ERROR:",
                str(error)
            )

            results.append(
                (name, model, False)
            )

    print()
    print("=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)

    for name, model, success in results:

        status = (
            "PASS"
            if success
            else "FAIL"
        )

        print(
            f"{name:<8} | "
            f"{model:<22} | "
            f"{status}"
        )

    print("=" * 70)


if __name__ == "__main__":
    main()