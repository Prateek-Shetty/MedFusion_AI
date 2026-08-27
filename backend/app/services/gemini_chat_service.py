from google import genai

from app.config import settings


class GeminiChatService:
    """
    Separate Gemini chatbot.

    IMPORTANT:

    This service uses ONLY:

        GEMINI_API_KEY_3
        GEMINI_MODEL_3

    It does not participate in the analysis
    Gemini fallback system.
    """

    # ========================================================
    # CHATBOT SYSTEM INSTRUCTION
    # ========================================================

    SYSTEM_INSTRUCTION = """
You are the MedFusion AI chatbot.

You are a conversational assistant for a college
project involving brain-scan analysis.

Your job is to:

- Explain medical and brain-related concepts
  in simple language.
- Explain terms that may appear in MedFusion AI
  results.
- Help users understand the purpose of the
  project's AI models.
- Answer general educational questions about MRI,
  CT, brain tumors, segmentation, classification,
  and WHO grading.
- Keep answers concise and easy to understand.

IMPORTANT SAFETY RULES:

You are NOT a doctor.

Do not:

- Diagnose a person.
- Confirm that someone has a disease.
- Prescribe medication.
- Recommend a specific medicine or dosage.
- Give a personalized treatment plan.
- Tell a user to start, stop, or change medication.
- Claim that an AI prediction is a confirmed diagnosis.

If a user asks what medication or treatment they
should take, explain that treatment decisions must
be made by a qualified healthcare professional.

If the user asks about their MedFusion AI scan result,
explain what the reported AI result means, but clearly
state that it is an AI-generated project output and
requires review by a qualified healthcare professional.

Keep responses relatively short unless the user
specifically asks for a detailed explanation.

Do not invent:

- Patient information
- Test results
- Hospital information
- Medical measurements
- Diagnoses
- Treatment information

If you don't know something, say so.

This chatbot is part of a college project and is
intended for educational demonstration purposes.
"""

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):

        # ----------------------------------------------------
        # CHATBOT KEY
        # ----------------------------------------------------

        self.api_key = (
            settings.GEMINI_API_KEY_3
        )

        # ----------------------------------------------------
        # CHATBOT MODEL
        # ----------------------------------------------------

        self.model = (
            settings.GEMINI_MODEL_3
        )

        # ----------------------------------------------------
        # VALIDATE KEY
        # ----------------------------------------------------

        if not self.api_key:

            raise RuntimeError(
                "GEMINI_API_KEY_3 is not configured."
            )

        # ----------------------------------------------------
        # CREATE CLIENT
        # ----------------------------------------------------

        self.client = genai.Client(
            api_key=self.api_key
        )

        print(
            "[Gemini Chat] Chatbot initialized."
        )

        print(
            "[Gemini Chat] Using API key 3."
        )

        print(
            f"[Gemini Chat] Model: {self.model}"
        )

    # ========================================================
    # SEND MESSAGE
    # ========================================================

    def send_message(
        self,
        message: str,
    ):

        # ====================================================
        # VALIDATE MESSAGE
        # ====================================================

        if not message:

            raise ValueError(
                "Message cannot be empty."
            )

        message = message.strip()

        if not message:

            raise ValueError(
                "Message cannot be empty."
            )

        # ====================================================
        # BUILD PROMPT
        # ====================================================

        prompt = (
            self.SYSTEM_INSTRUCTION
            + "\n\n"
            + "USER MESSAGE:\n"
            + message
        )

        # ====================================================
        # GEMINI REQUEST
        # ====================================================

        response = (
            self.client.models.generate_content(
                model=self.model,
                contents=prompt,
            )
        )

        # ====================================================
        # RESPONSE VALIDATION
        # ====================================================

        response_text = (
            response.text
            if response.text
            else ""
        )

        if not response_text:

            raise RuntimeError(
                "Gemini returned an empty response."
            )

        # ====================================================
        # RETURN
        # ====================================================

        return {

            "success":
                True,

            "model":
                self.model,

            "response":
                response_text,
        }


# ============================================================
# SINGLE CHATBOT INSTANCE
# ============================================================

gemini_chat_service = (
    GeminiChatService()
)