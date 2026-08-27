from pathlib import Path
import shutil
import tempfile

from fastapi import APIRouter, File, HTTPException, UploadFile

from app.api.routes.modality import modality_model
from app.api.routes.mri import mri_model
from app.api.routes.ct import ct_model

from app.services.analysis_pipeline import AnalysisPipeline


router = APIRouter(
    prefix="/api/v1/analysis",
    tags=["Analysis Pipeline"],
)


# ============================================================
# PIPELINE
# ============================================================

pipeline = AnalysisPipeline(
    modality_model=modality_model,
    mri_model=mri_model,
    ct_model=ct_model,
)


# ============================================================
# FULL ANALYSIS
# ============================================================

@router.post("/full")
async def full_analysis(
    file: UploadFile = File(...),
):

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="No file provided.",
        )

    # --------------------------------------------------------
    # Allowed formats
    # --------------------------------------------------------

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
        # Save uploaded image
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
        # RUN PIPELINE
        # ----------------------------------------------------

        result = pipeline.run(
            temp_path
        )

        return {
            "success": True,
            "filename": file.filename,
            "pipeline": result,
        }

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Analysis pipeline failed: {str(error)}"
            ),
        )

    finally:

        # ----------------------------------------------------
        # Remove temporary image
        # ----------------------------------------------------

        if (
            temp_path is not None
            and temp_path.exists()
        ):

            temp_path.unlink()