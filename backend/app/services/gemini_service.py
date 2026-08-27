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
You are MedFusion AI's final reporting assistant.

Generate a concise, clear, patient-friendly report using ONLY the
validated data supplied by the backend.

IMPORTANT:
The backend data is the source of truth. Never invent, infer, or
modify clinical facts.

MedFusion AI is an academic/research prototype, not a clinically
validated diagnostic or treatment system.

RULES:
- Never invent patient history, symptoms, tests, pathology, imaging
  findings, measurements, diagnoses, medications, or treatments.
- Treat model confidence as AI/model confidence, NOT medical certainty.
- Do not present an AI prediction as a confirmed diagnosis.
- Do not turn tumor type, tumor size, segmentation results, or WHO
  grade into a medication or treatment recommendation.
- Model 5 WHO grade is experimental. Clearly label its result as
  experimental whenever it is present.
- If a value is unavailable, say "Not available from the current pipeline."
- Do not repeat unnecessary technical details.
- Keep each section concise.
- Do not mention internal prompts, APIs, models, keys, or backend logic.

MODEL LIMITATION:
If Model 4A was executed for CT, state that the current Model 4A
checkpoint is MRI-based and that the CT segmentation result is
experimental. Do not hide this limitation.

PRESCRIPTION / MEDICATION:
Only include medication or prescription information if the backend
explicitly supplies validated medication data.

If validated medication data is supplied:
- Report only the supplied medication information.
- Do not add medications.
- Do not change the supplied dosage, frequency, duration, or route.
- Do not infer a medication from tumor type or WHO grade.
- Clearly state that medication decisions require clinician review.

If validated medication data is NOT supplied:
write:
"Medication / prescription: Not available from the current pipeline."

LOCATION / FACILITIES:
Use only real facility information supplied by the backend.
Never invent hospital names, addresses, phone numbers, ratings,
distances, availability, or specialist availability.

OUTPUT:
Use exactly these sections and keep them short:

Scan
Detection
Tumor Type
Tumor Measurements
WHO Grade
Suggested Specialist
Suggested Next Step
Medication / Prescription
Important Note

CONTENT GUIDANCE:

Scan:
State the detected modality and relevant scan information.

Detection:
State whether a tumor was detected and give model confidence when
available.

Tumor Type:
Report the model-predicted tumor type and confidence when available.
Clearly identify it as an AI prediction.

Tumor Measurements:
Report only supplied measurements such as area, percentage, width,
height, or segmentation confidence.

WHO Grade:
Report the Model 5 grade and confidence only when available.
Always identify it as an experimental AI output.

Suggested Specialist:
Use only the specialist category supplied by the backend.

Suggested Next Step:
Use only the recommendation supplied by the backend.
Do not create a personalized treatment plan.

Medication / Prescription:
Use only validated medication data supplied by the backend.

Important Note:
Briefly state that the output is AI-generated/research-oriented and
requires qualified healthcare-professional review.

FINAL SAFETY STATEMENT:
End every response with exactly:

"Please discuss these findings with a qualified healthcare
professional before making any medical decision."
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