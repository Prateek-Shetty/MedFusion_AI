from pathlib import Path
import shutil
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.ct_detector import CTTumorDetector


router = APIRouter(
    prefix="/api/v1/ct",
    tags=["CT"],
)


# ------------------------------------------------------------
# Load Model 2B once when the backend starts
# ------------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parents[3]

MODEL_PATH = (
    BACKEND_DIR
    / "models"
    / "BrainTumor_CT_Detector_Final.pth"
)

ct_model = CTTumorDetector(
    MODEL_PATH
)


# ------------------------------------------------------------
# CT tumor detection
# ------------------------------------------------------------

@router.post("/detect")
async def detect_ct_tumor(
    file: UploadFile = File(...)
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided.",
        )

    allowed_extensions = {
        ".jpg",
        ".jpeg",
        ".png",
        ".bmp",
        ".tif",
        ".tiff",
    }

    extension = Path(
        file.filename
    ).suffix.lower()

    if extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported image format. "
                "Use JPG, JPEG, PNG, BMP, TIF, or TIFF."
            ),
        )

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=extension,
        ) as temp_file:

            shutil.copyfileobj(
                file.file,
                temp_file,
            )

            temp_path = Path(
                temp_file.name
            )

        result = ct_model.predict(
            temp_path
        )

        return {
            "success": True,
            "filename": file.filename,
            "prediction": result,
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=f"CT model inference failed: {str(error)}",
        )

    finally:

        if temp_path is not None and temp_path.exists():
            temp_path.unlink()