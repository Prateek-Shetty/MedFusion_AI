from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import io

from app.models.model4_segmentation import predict_model4


router = APIRouter(
    prefix="/model4",
    tags=["Model 4A"]
)


@router.post("/segment")
async def segment_mri(
    file: UploadFile = File(...)
):
    """
    Segment the tumor region from an MRI image.

    Returns:
    - tumor detection
    - tumor area
    - tumor percentage
    - bounding box
    - centroid
    - width / height
    - boundary pixels
    - segmentation confidence
    - binary mask
    - tumor-highlighted MRI overlay
    """

    try:

        # ----------------------------------------------------
        # Validate file
        # ----------------------------------------------------

        if not file.content_type:
            raise HTTPException(
                status_code=400,
                detail="Invalid image file."
            )

        if not file.content_type.startswith(
            "image/"
        ):
            raise HTTPException(
                status_code=400,
                detail="Only image files are supported."
            )

        # ----------------------------------------------------
        # Read image
        # ----------------------------------------------------

        contents = await file.read()

        if not contents:
            raise HTTPException(
                status_code=400,
                detail="Empty image file."
            )

        # ----------------------------------------------------
        # Open image
        # ----------------------------------------------------

        try:

            image = Image.open(
                io.BytesIO(contents)
            )

            image.load()

        except Exception:

            raise HTTPException(
                status_code=400,
                detail="Unable to read image."
            )

        # ----------------------------------------------------
        # Model 4A prediction
        # ----------------------------------------------------

        result = predict_model4(
            image
        )

        # ----------------------------------------------------
        # Response
        # ----------------------------------------------------

        return result

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Model 4A prediction failed: {str(e)}"
        )