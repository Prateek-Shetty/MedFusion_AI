from typing import Any

from fastapi import (
    APIRouter,
    HTTPException,
)

from pydantic import BaseModel

from app.services.gemini_chat_service import (
    gemini_chat_service,
)


# ============================================================
# ROUTER
# ============================================================

router = APIRouter(
    prefix="/api/v1/chat",
    tags=["AI Chatbot"],
)


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):
    message: str

    # IMPORTANT:
    # The frontend may send different shapes of analysis data.
    # Do not force it to be a dict.
    analysis_context: Any = None


# ============================================================
# CHAT
# ============================================================

@router.post("")
async def chat(
    request: ChatRequest,
):

    # ========================================================
    # VALIDATE MESSAGE
    # ========================================================

    if not request.message:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    message = request.message.strip()

    if not message:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )


    # ========================================================
    # SEND TO GEMINI
    # ========================================================

    try:

        result = (
            gemini_chat_service.send_message(
                message=message,
                analysis_context=request.analysis_context,
            )
        )

        return result


    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


    except Exception as error:

        print(
            "[Gemini Chat] ERROR:",
            repr(error),
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Chatbot request failed: "
                f"{str(error)}"
            ),
        )