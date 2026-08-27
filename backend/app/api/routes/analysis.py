from pathlib import Path
import shutil
import tempfile

from fastapi import (
    APIRouter,
    File,
    Form,
    HTTPException,
    UploadFile,
)

from app.api.routes.modality import modality_model
from app.api.routes.mri import mri_model
from app.api.routes.ct import ct_model

from app.services.analysis_pipeline import (
    AnalysisPipeline,
)


router = APIRouter(
    prefix="/api/v1/analysis",
    tags=["Analysis Pipeline"],
)


# ============================================================
# PIPELINE INSTANCE
# ============================================================

pipeline = AnalysisPipeline(
    modality_model=modality_model,
    mri_model=mri_model,
    ct_model=ct_model,
)


# ============================================================
# COMPLETE ANALYSIS
# ============================================================

@router.post("/full")
async def full_analysis(
    file: UploadFile = File(...),

    # ========================================================
    # USER INFORMATION
    # ========================================================

    age: int | None = Form(None),

    sex_category: str | None = Form(None),

    # ========================================================
    # USER LOCATION
    #
    # These come from browser/device geolocation.
    # ========================================================

    latitude: float | None = Form(None),

    longitude: float | None = Form(None),
):

    # ========================================================
    # FILE VALIDATION
    # ========================================================

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No image provided.",
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

    # ========================================================
    # BASIC USER DATA
    #
    # Only collect information that the frontend actually asks
    # the user for.
    # ========================================================

    patient_data = {}

    if age is not None:
        patient_data["age"] = age

    if sex_category is not None:
        patient_data["sex_category"] = (
            sex_category.strip()
        )

    # ========================================================
    # LOCATION
    #
    # Store coordinates as a structured object.
    #
    # This is preferable to asking the user to type:
    # "Bangalore", "Chennai", etc.
    # ========================================================

    location = None

    if (
        latitude is not None
        and longitude is not None
    ):

        # Basic coordinate validation

        if not (
            -90.0
            <= latitude
            <= 90.0
        ):

            raise HTTPException(
                status_code=400,
                detail="Invalid latitude.",
            )

        if not (
            -180.0
            <= longitude
            <= 180.0
        ):

            raise HTTPException(
                status_code=400,
                detail="Invalid longitude.",
            )

        location = {
            "latitude": latitude,
            "longitude": longitude,
        }

    # ========================================================
    # TEMPORARY IMAGE
    # ========================================================

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

        # ====================================================
        # RUN COMPLETE PIPELINE
        # ====================================================

        result = pipeline.run(
            image_path=temp_path,
            patient_data=patient_data,
            location=location,
        )

        # ====================================================
        # API RESPONSE
        # ====================================================

        return {

            "success":
                True,

            "filename":
                file.filename,

            "patient_data":
                patient_data,

            "location":
                location,

            "pipeline":
                result,
        }

    except HTTPException:

        raise

    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Analysis pipeline failed: "
                f"{str(error)}"
            ),
        )

    finally:

        # ====================================================
        # DELETE TEMPORARY FILE
        # ====================================================

        if (
            temp_path is not None
            and temp_path.exists()
        ):

            try:

                temp_path.unlink()

            except OSError:

                pass