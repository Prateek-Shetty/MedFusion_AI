from pathlib import Path
import shutil
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.mri_detector import MRITumorDetector


router = APIRouter(
    prefix="/api/v1/mri",
    tags=["MRI"],
)


# ------------------------------------------------------------
# Load Model 2A once when the backend starts
# ------------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parents[3]

MODEL_PATH = (
    BACKEND_DIR
    / "models"
    / "BrainTumor_MRI_Detector_Best.pth"
)

mri_model = MRITumorDetector(
    MODEL_PATH
)


# ------------------------------------------------------------
# MRI tumor detection
# ------------------------------------------------------------

@router.post("/detect")
async def detect_mri_tumor(
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

        # ----------------------------------------------------
        # Save uploaded image temporarily
        # ----------------------------------------------------

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

        # ----------------------------------------------------
        # Run Model 2A
        # ----------------------------------------------------

        result = mri_model.predict(
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
            detail=f"MRI model inference failed: {str(error)}",
        )

    finally:

        # ----------------------------------------------------
        # Remove temporary file
        # ----------------------------------------------------

        if temp_path is not None and temp_path.exists():
            temp_path.unlink()