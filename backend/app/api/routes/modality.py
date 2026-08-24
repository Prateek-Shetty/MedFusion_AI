from pathlib import Path
import shutil
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.models.modality_model import ModalityModel


router = APIRouter(
    prefix="/api/v1/modality",
    tags=["Modality"],
)


# ------------------------------------------------------------
# Load Model 1 once when the backend starts
# ------------------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parents[3]

MODEL_PATH = (
    BACKEND_DIR
    / "models"
    / "BrainScan_Modality_Model.pth"
)

modality_model = ModalityModel(
    MODEL_PATH
)


# ------------------------------------------------------------
# Prediction endpoint
# ------------------------------------------------------------

@router.post("/predict")
async def predict_modality(
    file: UploadFile = File(...)
):

    # Check that a file was provided
    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided.",
        )

    # Allow common image formats
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

    # --------------------------------------------------------
    # Save uploaded image temporarily
    # --------------------------------------------------------

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

        # ----------------------------------------------------
        # Run Model 1
        # ----------------------------------------------------

        result = modality_model.predict(
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
            detail=f"Model inference failed: {str(error)}",
        )

    finally:

        # ----------------------------------------------------
        # Delete temporary uploaded image
        # ----------------------------------------------------

        if temp_path is not None and temp_path.exists():
            temp_path.unlink()