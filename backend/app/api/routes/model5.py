from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.models.model5_who_classifier import (
    predict_model5,
)


router = APIRouter(
    prefix="/model5",
    tags=["Model 5"]
)


# ============================================================
# REQUEST MODEL
# ============================================================

class Model5Request(BaseModel):

    age: float

    sex_category: str

    voxel_x_mm: float

    voxel_y_mm: float

    slice_thickness_mm: float

    field_strength_t: float

    field_strength_category: str

    resolution_category: str

    slice_thickness_category: str


# ============================================================
# ENDPOINT
# ============================================================

@router.post("/predict")
async def predict_who_grade(
    data: Model5Request
):

    try:

        metadata = data.model_dump()

        result = predict_model5(
            metadata
        )

        return {
            "model": "Model 5",
            "prediction": result
        }

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Model 5 prediction failed: {str(e)}"
        )