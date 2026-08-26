from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from PIL import Image
import io
import base64

from app.models.model4_segmentation import predict_model4


router = APIRouter(
    prefix="/model4",
    tags=["Model 4A"]
)


# ============================================================
# FULL SEGMENTATION RESULT
# ============================================================

@router.post("/segment")
async def segment_mri(
    file: UploadFile = File(...)
):

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Only image files are supported."
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Empty image file."
        )

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

    try:

        result = predict_model4(image)

        return result

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Model 4A prediction failed: {str(e)}"
        )


# ============================================================
# HIGHLIGHTED TUMOR IMAGE
# ============================================================

@router.post("/segment/overlay")
async def segment_mri_overlay(
    file: UploadFile = File(...)
):

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Only image files are supported."
        )

    contents = await file.read()

    if not contents:
        raise HTTPException(
            status_code=400,
            detail="Empty image file."
        )

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

    try:

        result = predict_model4(
            image
        )

        overlay_base64 = (
            result["segmentation"]
            ["overlay_png_base64"]
        )

        overlay_bytes = base64.b64decode(
            overlay_base64
        )

        return StreamingResponse(
            io.BytesIO(overlay_bytes),
            media_type="image/png",
            headers={
                "Content-Disposition":
                    "inline; filename=model4_tumor_overlay.png"
            }
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Model 4A overlay generation failed: {str(e)}"
        )


# ============================================================
# BINARY MASK IMAGE
# ============================================================

@router.post("/segment/mask")
async def segment_mri_mask(
    file: UploadFile = File(...)
):

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="Only image files are supported."
        )

    contents = await file.read()

    try:

        image = Image.open(
            io.BytesIO(contents)
        )
        image.load()

        result = predict_model4(
            image
        )

        mask_base64 = (
            result["segmentation"]
            ["mask_png_base64"]
        )

        mask_bytes = base64.b64decode(
            mask_base64
        )

        return StreamingResponse(
            io.BytesIO(mask_bytes),
            media_type="image/png",
            headers={
                "Content-Disposition":
                    "inline; filename=model4_tumor_mask.png"
            }
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Model 4A mask generation failed: {str(e)}"
        )