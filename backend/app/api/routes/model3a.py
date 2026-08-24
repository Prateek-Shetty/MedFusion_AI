from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import io

from app.models.model3a_classifier import predict_model3a


router = APIRouter(
    prefix="/model3a",
    tags=["Model 3A"]
)


@router.post("/predict")
async def predict(
    file: UploadFile = File(...)
):
    try:
        contents = await file.read()

        image = Image.open(
            io.BytesIO(contents)
        )

        result = predict_model3a(image)

        return {
            "tumor_present": result["tumor_present"],
            "tumor_type": result["tumor_type"],
            "confidence": result["confidence"],
            "probabilities": result["probabilities"],
        }

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )