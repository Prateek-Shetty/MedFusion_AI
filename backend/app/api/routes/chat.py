from fastapi import (
    APIRouter,
    HTTPException,
)

from pydantic import BaseModel

from app.services.gemini_chat_service import (
    gemini_chat_service,
)


router = APIRouter(
    prefix="/api/v1/chat",
    tags=["AI Chatbot"],
)


class ChatRequest(BaseModel):

    message: str


@router.post("")
async def chat(
    request: ChatRequest,
):

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

    try:

        result = (
            gemini_chat_service.send_message(
                message
            )
        )

        return result

    except ValueError as error:

        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Chatbot request failed: "
                f"{str(error)}"
            ),
        )