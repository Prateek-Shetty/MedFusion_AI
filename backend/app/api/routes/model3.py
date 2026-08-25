from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import io

from app.models.model3_classifier import predict_model3


router = APIRouter(
    prefix="/model3",
    tags=["Model 3"],
)


@router.post("/predict")
async def predict(
    file: UploadFile = File(...)
):
    try:
        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="No image provided.",
            )

        image = Image.open(
            io.BytesIO(contents)
        )

        result = predict_model3(image)

        return {
            "tumor_detected": result["tumor_detected"],
            "tumor_type": result["tumor_type"],
            "confidence_percent": result["confidence_percent"],
            "predictions": result["predictions"],
            "message": result["message"],
        }

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )