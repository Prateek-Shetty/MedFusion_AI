from typing import Any, Dict, List, Tuple
import json
import re

from google import genai
from google.genai import types

from app.config import settings


class GeminiService:
    """
    Gemini analysis/reporting service.

    Gemini receives the available MedFusion pipeline data
    and generates an intelligent educational interpretation.

    API key 1:
        Primary analysis

    API key 2:
        Fallback analysis

    API key 3:
        Reserved exclusively for the chatbot.
    """

    # ========================================================
    # GEMINI SYSTEM INSTRUCTION
    # ========================================================

    SYSTEM_INSTRUCTION = """
You are the intelligent interpretation layer of MedFusion AI, an
academic brain-scan analysis prototype.

Analyze the supplied pipeline data and produce a useful,
patient-friendly explanation. Do not merely repeat model outputs.
Combine the available results from modality detection, tumor
detection, classification, segmentation, measurements, age,
gender, and specialist information.

Use only information supported by the supplied data.

IMPORTANT:
- Interpret the model results instead of copying them.
- Combine Model 2, Model 3 and Model 4 findings when available.
- Do not say a model is unavailable unless its data is genuinely
  absent.
- Do not repeat raw measurements unnecessarily.
- Explain what confidence values mean rather than treating them
  as medical certainty.
- Distinguish AI prediction from confirmed medical diagnosis.

AGE AND GENDER:
Use age and gender as clinical context when relevant.
Do not simply repeat them.
Explain any meaningful  context with respect to age.
Never claim age or gender determines the tumor type or diagnosis.

SPECIALIST:
Use the pipeline's specialist recommendation when available.
Explain briefly why that specialist is relevant and what they
generally evaluate.
If no specialist is supplied, infer a reasonable specialist category
from the findings and clearly present it as general guidance.

NEXT STEP:
Generate a meaningful next-step pathway based on the actual findings.
Where appropriate, discuss specialist review, complete scan/report
review, additional imaging, further testing, pathology, or treatment
planning.

TREATMENT AND MANAGEMENT:
Provide general educational information relevant to the reported
finding or leading tumor classification.
Where appropriate, explain possible approaches such as surveillance,
surgery, radiotherapy, radiosurgery, chemotherapy, targeted therapy,
immunotherapy, or supportive treatment.

If the tumor type is uncertain, make that uncertainty clear and
describe treatment options at an appropriate general level.

SUPPORTIVE GUIDANCE:
Give practical, useful and situation-specific guidance.
Avoid generic repeated advice.
It may include describing the general medicine taken , natural methods etc

OUTPUT:
Return ONLY valid JSON with exactly these fields:

{
  "summary": "",
  "finding_explanation": "",
  "patient_context": "",
  "specialist": "",
  "next_step": "",
  "treatment_information": "",
  "supportive_guidance": [],
  "safety_note": ""
}

Make the content dynamic from the supplied data.

Keep the response concise and suitable for UI cards:
- summary: 2–3 sentences
- finding_explanation: 2–3 sentences
- patient_context: 1–2 sentences
- specialist: 1–2 sentences
- next_step: 2–4 concise steps
- treatment_information: 2–4 sentences
- supportive_guidance: 3 useful points
- safety_note: 1 short sentence

Do not repeat the same information between sections.
Do not add fields.
Do not use Markdown outside the JSON.
Return the complete JSON object.
"""


    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):

        self.credentials: List[
            Tuple[str, str]
        ] = []

        # ----------------------------------------------------
        # PRIMARY
        # ----------------------------------------------------

        if settings.GEMINI_API_KEY_1:

            self.credentials.append(
                (
                    settings.GEMINI_API_KEY_1,
                    settings.GEMINI_MODEL_1,
                )
            )

        # ----------------------------------------------------
        # FALLBACK
        # ----------------------------------------------------

        if settings.GEMINI_API_KEY_2:

            self.credentials.append(
                (
                    settings.GEMINI_API_KEY_2,
                    settings.GEMINI_MODEL_2,
                )
            )

        if not self.credentials:

            raise RuntimeError(
                "No Gemini analysis API keys configured."
            )

        print(
            "[Gemini] Analysis service initialized."
        )

        print(
            "[Gemini] Analysis keys configured: "
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
    # SAFE VALUE
    # ========================================================

    @staticmethod
    def _clean_value(
        value: Any,
    ) -> Any:

        if value is None:
            return None

        if isinstance(
            value,
            (str, int, float, bool),
        ):
            return value

        if isinstance(
            value,
            dict,
        ):

            return {
                str(key):
                    GeminiService._clean_value(
                        item
                    )
                for key, item in value.items()
            }

        if isinstance(
            value,
            list,
        ):

            return [
                GeminiService._clean_value(
                    item
                )
                for item in value
            ]

        return str(value)


    # ========================================================
    # BUILD GEMINI PAYLOAD
    # ========================================================

    def _build_gemini_payload(
        self,
        pipeline_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Preserve all useful pipeline information.

        We deliberately do NOT reduce the model outputs to
        a handful of manually selected fields.

        Gemini should receive the available analysis context
        and determine what is relevant.
        """

        cleaned_data = (
            self._clean_value(
                pipeline_data
            )
        )

        if not isinstance(
            cleaned_data,
            dict,
        ):

            raise RuntimeError(
                "Pipeline data must be a JSON object."
            )

        return cleaned_data


    # ========================================================
    # EXTRACT JSON
    # ========================================================

    @staticmethod
    def _extract_json(
        response_text: str,
    ) -> Dict[str, Any]:

        text = (
            response_text
            or ""
        ).strip()

        if not text:

            raise RuntimeError(
                "Gemini returned an empty response."
            )

        # ----------------------------------------------------
        # Remove markdown fences
        # ----------------------------------------------------

        text = re.sub(
            r"^```(?:json)?\s*",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"\s*```$",
            "",
            text,
            flags=re.IGNORECASE,
        )

        text = text.strip()

        # ----------------------------------------------------
        # Direct JSON
        # ----------------------------------------------------

        try:

            parsed = json.loads(
                text
            )

            if isinstance(
                parsed,
                dict,
            ):

                return parsed

        except json.JSONDecodeError:
            pass

        # ----------------------------------------------------
        # Extract JSON object
        # ----------------------------------------------------

        first_brace = text.find("{")

        last_brace = text.rfind("}")

        if (
            first_brace != -1
            and last_brace != -1
            and last_brace > first_brace
        ):

            candidate = text[
                first_brace:
                last_brace + 1
            ]

            try:

                parsed = json.loads(
                    candidate
                )

                if isinstance(
                    parsed,
                    dict,
                ):

                    return parsed

            except json.JSONDecodeError:
                pass

        print(
            "[Gemini] Invalid JSON response preview:"
        )

        print(
            text[:1000]
        )

        raise RuntimeError(
            "Gemini returned invalid JSON."
        )


    # ========================================================
    # GENERATE REPORT
    # ========================================================

    def generate_report(
        self,
        pipeline_data: Dict[str, Any],
    ):

        # ====================================================
        # BUILD PAYLOAD
        # ====================================================

        gemini_payload = (
            self._build_gemini_payload(
                pipeline_data
            )
        )


        # ====================================================
        # PROMPT
        # ====================================================

        prompt = (
            self.SYSTEM_INSTRUCTION
            + "\n\n"
            + "MEDFUSION PIPELINE DATA:\n"
            + json.dumps(
                gemini_payload,
                indent=2,
                default=str,
            )
        )


        last_error = None


        # ====================================================
        # PRIMARY + FALLBACK
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
                    "[Gemini] Generating report "
                    f"using key {index} "
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

                        config=types.GenerateContentConfig(

                            temperature=0.35,

                            max_output_tokens=2500,

                            response_mime_type=(
                                "application/json"
                            ),
                        ),
                    )
                )


                response_text = (
                    response.text
                    if response.text
                    else ""
                ).strip()


                if not response_text:

                    raise RuntimeError(
                        "Gemini returned an empty response."
                    )


                print(
                    "[Gemini] Response received."
                )

                print(
                    "[Gemini] Response length: "
                    f"{len(response_text)} characters."
                )


                # =================================================
                # PARSE
                # =================================================

                structured = (
                    self._extract_json(
                        response_text
                    )
                )


                # =================================================
                # NORMALIZE
                # =================================================

                structured = (
                    self._normalize_response(
                        structured
                    )
                )


                print(
                    "[Gemini] Report generated "
                    f"successfully using key {index}."
                )


                return {

                    "success":
                        True,

                    "key_used":
                        index,

                    "model":
                        model,

                    "structured":
                        structured,

                    "report":
                        response_text,
                }


            except Exception as error:

                last_error = error

                print(
                    "[Gemini] Key "
                    f"{index} failed: "
                    f"{type(error).__name__}: "
                    f"{error}"
                )

                continue


        # ====================================================
        # ALL FAILED
        # ====================================================

        raise RuntimeError(
            "All configured Gemini analysis "
            "API keys failed."
        ) from last_error


    # ========================================================
    # NORMALIZE RESPONSE
    # ========================================================

    @staticmethod
    def _normalize_response(
        data: Any,
    ) -> Dict[str, Any]:

        if not isinstance(
            data,
            dict,
        ):

            raise RuntimeError(
                "Gemini response must be a JSON object."
            )


        # ----------------------------------------------------
        # GUIDANCE
        # ----------------------------------------------------

        guidance = data.get(
            "supportive_guidance",
            [],
        )


        if not isinstance(
            guidance,
            list,
        ):

            guidance = [
                str(guidance)
            ]


        guidance = [
            str(item).strip()
            for item in guidance
            if str(item).strip()
        ]


        # ----------------------------------------------------
        # RETURN
        # ----------------------------------------------------

        return {

            "summary":
                str(
                    data.get(
                        "summary",
                        "",
                    )
                ).strip(),


            "finding_explanation":
                str(
                    data.get(
                        "finding_explanation",
                        "",
                    )
                ).strip(),


            "patient_context":
                str(
                    data.get(
                        "patient_context",
                        "",
                    )
                ).strip(),


            "specialist":
                str(
                    data.get(
                        "specialist",
                        "",
                    )
                ).strip(),


            "next_step":
                str(
                    data.get(
                        "next_step",
                        "",
                    )
                ).strip(),


            "treatment_information":
                str(
                    data.get(
                        "treatment_information",
                        "",
                    )
                ).strip(),


            "supportive_guidance":
                guidance,


            "safety_note":
                str(
                    data.get(
                        "safety_note",
                        "",
                    )
                ).strip(),
        }


# ============================================================
# SINGLE SERVICE INSTANCE
# ============================================================

gemini_service = GeminiService()