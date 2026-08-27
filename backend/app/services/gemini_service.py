from typing import Any, Dict, List, Tuple

from google import genai

from app.config import settings


class GeminiService:
    """
    Gemini service for the MedFusion analysis pipeline.

    Analysis Gemini configuration:

        API KEY 1 → GEMINI_MODEL_1
        API KEY 2 → GEMINI_MODEL_2

    Key 3 is intentionally reserved exclusively
    for the separate chatbot.
    """

    # ========================================================
    # SYSTEM INSTRUCTION
    # ========================================================

    SYSTEM_INSTRUCTION = """
You are the final reporting assistant for the
MedFusion AI college project.

Generate a SHORT, clear and structured report
using ONLY the supplied pipeline data.

This is an AI/research prototype and NOT a
confirmed medical diagnosis.

DO NOT:
- invent medical information
- invent patient history
- invent laboratory results
- invent pathology
- invent imaging measurements
- prescribe medication
- give drug names
- give dosage
- give frequency
- give treatment duration
- make definitive treatment decisions

Model 5 WHO grade is EXPERIMENTAL.

If Model 5 is available:
report its grade and confidence as an
EXPERIMENTAL AI output.

If Model 5 is unavailable:
write:
"Not available from the current pipeline."

If Model 4 was executed on CT:
explicitly say that the current Model 4A checkpoint
is MRI-based and that the CT segmentation output
is experimental.

Do not hide this limitation.

HOSPITAL RECOMMENDATION:

If a user location is supplied, mention that the
user should look for a nearby hospital with
Neurosurgery or Neuro-oncology services.

Do NOT invent:
- hospital names
- addresses
- distances
- phone numbers
- ratings
- availability

Gemini is not a live hospital database.

The frontend can later use a maps/hospital API
to obtain actual nearby hospitals.

Use EXACTLY these sections:

Scan
Detection
Tumor Type
Tumor Measurements
WHO Grade
Suggested Specialist
Suggested Next Step
Important Note

Keep every section short.

For medication:
DO NOT prescribe medication.

For treatment:
DO NOT give a treatment plan.

The final response must end with:

"Please discuss these findings with a qualified
healthcare professional before making any medical
decision."
"""

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):

        # ----------------------------------------------------
        # KEY + MODEL PAIRS
        # ----------------------------------------------------

        self.credentials: List[
            Tuple[str, str]
        ] = []

        if settings.GEMINI_API_KEY_1:

            self.credentials.append(
                (
                    settings.GEMINI_API_KEY_1,
                    settings.GEMINI_MODEL_1,
                )
            )

        if settings.GEMINI_API_KEY_2:

            self.credentials.append(
                (
                    settings.GEMINI_API_KEY_2,
                    settings.GEMINI_MODEL_2,
                )
            )

        # ----------------------------------------------------
        # REQUIRE AT LEAST ONE KEY
        # ----------------------------------------------------

        if not self.credentials:

            raise RuntimeError(
                "No Gemini analysis API keys configured."
            )

        print(
            "[Gemini] Analysis service initialized."
        )

        print(
            f"[Gemini] Analysis keys configured: "
            f"{len(self.credentials)}"
        )

        for index, (
            _api_key,
            model,
        ) in enumerate(
            self.credentials,
            start=1,
        ):

            print(
                f"[Gemini] Key {index} → {model}"
            )

    # ========================================================
    # CLIENT
    # ========================================================

    @staticmethod
    def _create_client(
        api_key: str,
    ):

        return genai.Client(
            api_key=api_key
        )

    # ========================================================
    # TEST CONNECTION
    # ========================================================

    def test_connection(self):

        last_error = None

        for index, (
            api_key,
            model,
        ) in enumerate(
            self.credentials,
            start=1,
        ):

            try:

                print(
                    f"[Gemini] Testing analysis "
                    f"API key {index}..."
                )

                client = (
                    self._create_client(
                        api_key
                    )
                )

                response = (
                    client.models.generate_content(
                        model=model,
                        contents=(
                            "Reply with exactly: "
                            "Gemini connection successful."
                        ),
                    )
                )

                print(
                    f"[Gemini] API key {index} "
                    "successful."
                )

                return {

                    "success":
                        True,

                    "key_used":
                        index,

                    "model":
                        model,

                    "response":
                        response.text,
                }

            except Exception as error:

                last_error = error

                print(
                    f"[Gemini] Analysis API key "
                    f"{index} failed: "
                    f"{type(error).__name__}: "
                    f"{error}"
                )

        raise RuntimeError(
            "All configured Gemini analysis "
            "API keys failed."
        ) from last_error

    # ========================================================
    # GENERATE FINAL REPORT
    # ========================================================

    def generate_report(
        self,
        pipeline_data: Dict[str, Any],
    ):

        import json

        # ----------------------------------------------------
        # BUILD PROMPT
        # ----------------------------------------------------

        prompt = (
            self.SYSTEM_INSTRUCTION
            + "\n\n"
            + "MEDFUSION PIPELINE DATA:\n"
            + json.dumps(
                pipeline_data,
                indent=2,
                default=str,
            )
        )

        last_error = None

        # ====================================================
        # KEY FALLBACK
        # ====================================================

        for index, (
            api_key,
            model,
        ) in enumerate(
            self.credentials,
            start=1,
        ):

            try:

                print(
                    "[Gemini] Generating final "
                    f"report using API key {index} "
                    f"({model})..."
                )

                client = (
                    self._create_client(
                        api_key
                    )
                )

                response = (
                    client.models.generate_content(
                        model=model,
                        contents=prompt,
                    )
                )

                print(
                    "[Gemini] Final report generated "
                    f"using API key {index}."
                )

                return {

                    "success":
                        True,

                    "key_used":
                        index,

                    "model":
                        model,

                    "report":
                        response.text,
                }

            except Exception as error:

                last_error = error

                print(
                    "[Gemini] Analysis key "
                    f"{index} failed: "
                    f"{type(error).__name__}: "
                    f"{error}"
                )

                # Continue to next analysis key.

                continue

        raise RuntimeError(
            "All configured Gemini analysis "
            "API keys failed."
        ) from last_error


# ============================================================
# SINGLE SERVICE INSTANCE
# ============================================================

gemini_service = GeminiService()