# ============================================================
# MEDFUSION AI — COMPLETE ANALYSIS PIPELINE
#
# MRI:
#   Model 1
#      ↓
#   Model 2A
#      ↓
#   Model 3
#      ↓
#   Model 4A
#      ↓
#   Google Maps — Neurosurgery Hospital
#      ↓
#   Gemini
#
# CT:
#   Model 1
#      ↓
#   Model 2B
#      ↓
#   Model 4A
#      ↓
#   Google Maps — Neurosurgery Hospital
#      ↓
#   Gemini
#
# Model 5 has been completely removed.
#
# Supported input:
#   JPG / JPEG / PNG / BMP / TIF / TIFF
#
# ============================================================

from pathlib import Path
from typing import Any, Dict, Optional

from PIL import Image


# ============================================================
# MODELS
# ============================================================

from app.models.modality_model import ModalityModel
from app.models.mri_detector import MRITumorDetector
from app.models.ct_detector import CTTumorDetector

from app.models.model3_classifier import (
    predict_model3,
)

from app.models.model4_segmentation import (
    predict_model4,
)


# ============================================================
# SERVICES
# ============================================================

from app.services.gemini_service import (
    gemini_service,
)

from app.services.places_service import (
    places_service,
)


# ============================================================
# PIPELINE
# ============================================================


class AnalysisPipeline:
    """
    MedFusion AI complete analysis pipeline.

    MRI:

        Model 1
        -> Model 2A
        -> Model 3
        -> Model 4A
        -> Neurosurgery Hospital Search
        -> Gemini

    CT:

        Model 1
        -> Model 2B
        -> Model 4A
        -> Neurosurgery Hospital Search
        -> Gemini

    Model 5 has intentionally been removed.
    """

    # ========================================================
    # CONSTRUCTOR
    # ========================================================

    def __init__(
        self,
        modality_model: ModalityModel,
        mri_model: MRITumorDetector,
        ct_model: CTTumorDetector,
    ):

        self.modality_model = (
            modality_model
        )

        self.mri_model = (
            mri_model
        )

        self.ct_model = (
            ct_model
        )

    # ========================================================
    # MAIN PIPELINE
    # ========================================================

    def run(
        self,
        image_path: Path,
        patient_data: Optional[
            Dict[str, Any]
        ] = None,
        location: Optional[
            Dict[str, float]
        ] = None,
    ) -> Dict[str, Any]:

        # ----------------------------------------------------
        # NORMALIZE IMAGE PATH
        # ----------------------------------------------------

        image_path = Path(
            image_path
        )

        if not image_path.exists():

            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        # ----------------------------------------------------
        # NORMALIZE PATIENT DATA
        # ----------------------------------------------------

        patient_data = (
            patient_data
            if patient_data is not None
            else {}
        )

        # ====================================================
        # MODEL 1 — MODALITY CLASSIFICATION
        # ====================================================

        modality_result = (
            self.modality_model.predict(
                image_path
            )
        )

        modality = str(
            modality_result.get(
                "predicted_modality",
                "",
            )
        ).upper().strip()

        # ====================================================
        # MRI
        # ====================================================

        if modality == "MRI":

            return self._run_mri_pipeline(
                image_path=image_path,
                modality_result=modality_result,
                patient_data=patient_data,
                location=location,
            )

        # ====================================================
        # MR FALLBACK
        # ====================================================

        if modality == "MR":

            modality_result = {
                **modality_result,
                "predicted_modality": "MRI",
            }

            return self._run_mri_pipeline(
                image_path=image_path,
                modality_result=modality_result,
                patient_data=patient_data,
                location=location,
            )

        # ====================================================
        # CT
        # ====================================================

        if modality == "CT":

            return self._run_ct_pipeline(
                image_path=image_path,
                modality_result=modality_result,
                patient_data=patient_data,
                location=location,
            )

        # ====================================================
        # UNKNOWN MODALITY
        # ====================================================

        return {

            "pipeline_status":
                "stopped_unknown_modality",

            "modality":
                modality_result,

            "message":
                (
                    "Model 1 returned an unknown "
                    "modality."
                ),

        }

    # ========================================================
    # MRI PIPELINE
    # ========================================================

    def _run_mri_pipeline(
        self,
        image_path: Path,
        modality_result: Dict[str, Any],
        patient_data: Dict[str, Any],
        location: Optional[
            Dict[str, float]
        ],
    ) -> Dict[str, Any]:

        # ====================================================
        # MODEL 2A — MRI TUMOR DETECTION
        # ====================================================

        tumor_detection = (
            self.mri_model.predict(
                image_path
            )
        )

        predicted_class = str(
            tumor_detection.get(
                "predicted_class",
                "",
            )
        ).strip().lower()

        tumor_detected = (
            predicted_class == "tumor"
        )

        # ====================================================
        # INITIAL RESULT
        # ====================================================

        result = {

            "pipeline_status":
                None,

            "modality":
                modality_result,

            "model2": {

                "model":
                    "Model 2A",

                "type":
                    "MRI Tumor Detector",

                "result":
                    tumor_detection,

            },

            "tumor_detected":
                tumor_detected,

        }

        # ====================================================
        # NO TUMOR
        # ====================================================

        if not tumor_detected:

            result[
                "pipeline_status"
            ] = "stopped_no_tumor"

            result[
                "message"
            ] = (
                "No tumor detected by Model 2A. "
                "Pipeline stopped."
            )

            return result

        # ====================================================
        # MODEL 3
        # ====================================================

        try:

            with Image.open(
                image_path
            ) as image:

                model3_result = (
                    predict_model3(
                        image.convert(
                            "RGB"
                        )
                    )
                )

        except Exception as error:

            result[
                "model3"
            ] = {

                "model":
                    "Model 3",

                "status":
                    "failed",

                "error":
                    str(error),

            }

            result[
                "pipeline_status"
            ] = "model3_failed"

            result[
                "message"
            ] = (
                "Model 3 failed during classification."
            )

            return result

        result[
            "model3"
        ] = {

            "model":
                "Model 3",

            "status":
                "success",

            "result":
                model3_result,

        }

        # ====================================================
        # MODEL 4A — SEGMENTATION
        # ====================================================

        try:

            with Image.open(
                image_path
            ) as image:

                model4_result = (
                    predict_model4(
                        image.convert(
                            "RGB"
                        )
                    )
                )

        except Exception as error:

            result[
                "model4"
            ] = {

                "model":
                    "Model 4A",

                "status":
                    "failed",

                "error":
                    str(error),

            }

            result[
                "pipeline_status"
            ] = "model4_failed"

            result[
                "message"
            ] = (
                "Model 4A failed during segmentation."
            )

            return result

        result[
            "model4"
        ] = {

            "model":
                "Model 4A",

            "input_modality":
                "MRI",

            "experimental":
                False,

            "status":
                "success",

            "result":
                model4_result,

        }

        # ====================================================
        # MODEL 4 SAFETY CHECK
        # ====================================================

        model4_tumor_detected = (
            model4_result.get(
                "tumor_detected",
                False,
            )
        )

        if not model4_tumor_detected:

            result[
                "pipeline_status"
            ] = (
                "segmentation_found_no_tumor"
            )

            result[
                "message"
            ] = (
                "Model 2A detected a tumor, but "
                "Model 4A did not produce a "
                "segmented tumor region."
            )

            return result

        # ====================================================
        # GOOGLE MAPS — NEUROSURGERY
        # ====================================================

        places_result = (
            self._run_places(
                location=location
            )
        )

        result[
            "places"
        ] = places_result

        # ====================================================
        # GEMINI
        # ====================================================

        gemini_result = (
            self._run_gemini(

                modality="MRI",

                modality_result=
                    modality_result,

                tumor_detection=
                    tumor_detection,

                model3_result=
                    model3_result,

                model4_result=
                    model4_result,

                location=
                    location,

                places_result=
                    places_result,

                patient_data=
                    patient_data,

            )
        )

        result[
            "gemini"
        ] = gemini_result

        # ====================================================
        # FINAL STATUS
        # ====================================================

        result[
            "pipeline_status"
        ] = "completed"

        result[
            "message"
        ] = (
            "MRI pipeline completed through "
            "Model 4A, Neurosurgery search and Gemini."
        )

        return result

    # ========================================================
    # CT PIPELINE
    # ========================================================

    def _run_ct_pipeline(
        self,
        image_path: Path,
        modality_result: Dict[str, Any],
        patient_data: Dict[str, Any],
        location: Optional[
            Dict[str, float]
        ],
    ) -> Dict[str, Any]:

        # ====================================================
        # MODEL 2B — CT TUMOR DETECTION
        # ====================================================

        tumor_detection = (
            self.ct_model.predict(
                image_path
            )
        )

        predicted_class = str(
            tumor_detection.get(
                "predicted_class",
                "",
            )
        ).strip().lower()

        tumor_detected = (
            predicted_class == "tumor"
        )

        # ====================================================
        # INITIAL RESULT
        # ====================================================

        result = {

            "pipeline_status":
                None,

            "modality":
                modality_result,

            "model2": {

                "model":
                    "Model 2B",

                "type":
                    "CT Tumor Detector",

                "result":
                    tumor_detection,

            },

            "tumor_detected":
                tumor_detected,

        }

        # ====================================================
        # NO TUMOR
        # ====================================================

        if not tumor_detected:

            result[
                "pipeline_status"
            ] = "stopped_no_tumor"

            result[
                "message"
            ] = (
                "No tumor detected by Model 2B. "
                "Pipeline stopped."
            )

            return result

        # ====================================================
        # MODEL 4A
        #
        # Model 4A was trained for MRI.
        #
        # CT execution is therefore marked experimental.
        # ====================================================

        try:

            with Image.open(
                image_path
            ) as image:

                model4_result = (
                    predict_model4(
                        image.convert(
                            "RGB"
                        )
                    )
                )

        except Exception as error:

            result[
                "model4"
            ] = {

                "model":
                    "Model 4A",

                "status":
                    "failed",

                "error":
                    str(error),

            }

            result[
                "pipeline_status"
            ] = "model4_failed"

            result[
                "message"
            ] = (
                "Model 4A failed during segmentation."
            )

            return result

        result[
            "model4"
        ] = {

            "model":
                "Model 4A",

            "input_modality":
                "CT",

            "training_modality":
                "MRI",

            "experimental":
                True,

            "status":
                "success",

            "result":
                model4_result,

        }

        # ====================================================
        # GOOGLE MAPS — NEUROSURGERY
        # ====================================================

        places_result = (
            self._run_places(
                location=location
            )
        )

        result[
            "places"
        ] = places_result

        # ====================================================
        # GEMINI
        # ====================================================

        gemini_result = (
            self._run_gemini(

                modality="CT",

                modality_result=
                    modality_result,

                tumor_detection=
                    tumor_detection,

                model3_result=
                    None,

                model4_result=
                    model4_result,

                location=
                    location,

                places_result=
                    places_result,

            )
        )

        result[
            "gemini"
        ] = gemini_result

        # ====================================================
        # FINAL STATUS
        # ====================================================

        result[
            "pipeline_status"
        ] = "completed"

        result[
            "message"
        ] = (
            "CT pipeline completed through "
            "Model 4A, Neurosurgery search and Gemini."
        )

        return result

    # ========================================================
    # GOOGLE MAPS
    # ========================================================

    @staticmethod
    def _run_places(
        location: Optional[
            Dict[str, float]
        ],
    ) -> Dict[str, Any]:

        # ====================================================
        # LOCATION NOT PROVIDED
        # ====================================================

        if not location:

            return {

                "available":
                    False,

                "status":
                    "location_not_provided",

                "search_type":
                    "Neurosurgery",

                "maps_search_url":
                    None,

                "message":
                    "User location was not provided.",

            }

        # ====================================================
        # GET COORDINATES
        # ====================================================

        latitude = location.get(
            "latitude"
        )

        longitude = location.get(
            "longitude"
        )

        if (
            latitude is None
            or longitude is None
        ):

            return {

                "available":
                    False,

                "status":
                    "invalid_location",

                "search_type":
                    "Neurosurgery",

                "maps_search_url":
                    None,

                "message":
                    (
                        "Valid latitude and longitude "
                        "are required."
                    ),

            }

        # ====================================================
        # CONVERT COORDINATES
        # ====================================================

        try:

            latitude = float(
                latitude
            )

            longitude = float(
                longitude
            )

        except (
            TypeError,
            ValueError,
        ):

            return {

                "available":
                    False,

                "status":
                    "invalid_location",

                "search_type":
                    "Neurosurgery",

                "maps_search_url":
                    None,

                "message":
                    (
                        "Latitude and longitude must "
                        "be valid numbers."
                    ),

            }

        # ====================================================
        # VALIDATE LATITUDE
        # ====================================================

        if not (
            -90.0
            <= latitude
            <= 90.0
        ):

            return {

                "available":
                    False,

                "status":
                    "invalid_latitude",

                "search_type":
                    "Neurosurgery",

                "maps_search_url":
                    None,

                "message":
                    "Invalid latitude.",

            }

        # ====================================================
        # VALIDATE LONGITUDE
        # ====================================================

        if not (
            -180.0
            <= longitude
            <= 180.0
        ):

            return {

                "available":
                    False,

                "status":
                    "invalid_longitude",

                "search_type":
                    "Neurosurgery",

                "maps_search_url":
                    None,

                "message":
                    "Invalid longitude.",

            }

        # ====================================================
        # CREATE NEUROSURGERY SEARCH
        # ====================================================

        try:

            maps_url = (
                places_service.create_maps_search_url(

                    specialist=
                        "Neurosurgery",

                    latitude=
                        latitude,

                    longitude=
                        longitude,

                )
            )

            return {

                "available":
                    True,

                "status":
                    "success",

                "search_type":
                    "Neurosurgery hospital",

                "maps_search_url":
                    maps_url,

            }

        except Exception as error:

            return {

                "available":
                    False,

                "status":
                    "maps_url_generation_failed",

                "search_type":
                    "Neurosurgery hospital",

                "maps_search_url":
                    None,

                "error":
                    str(error),

            }

    # ========================================================
    # GEMINI
    # ========================================================

    @staticmethod
    def _run_gemini(
    modality: str,
    modality_result: Dict[str, Any],
    tumor_detection: Dict[str, Any],
    model3_result: Optional[
        Dict[str, Any]
    ],
    model4_result: Dict[str, Any],
    patient_data: Optional[
        Dict[str, Any]
    ],
    location: Optional[
        Dict[str, float]
    ],
    places_result: Dict[str, Any],
    ) -> Dict[str, Any]:

        # ====================================================
        # MODEL 4 SUMMARY
        #
        # Do NOT send huge base64 images to Gemini.
        # ====================================================

        model4_summary = {}

        if isinstance(
            model4_result,
            dict,
        ):

            model4_summary = {

                "tumor_detected":
                    model4_result.get(
                        "tumor_detected"
                    ),

                "input_image":
                    model4_result.get(
                        "input_image"
                    ),

                "processed_image":
                    model4_result.get(
                        "processed_image"
                    ),

                "measurements":
                    model4_result.get(
                        "measurements",
                        {},
                    ),

                "model":
                    model4_result.get(
                        "model"
                    ),

            }

        # ====================================================
        # MODEL 3
        # ====================================================

        model3_summary = (
            model3_result
            if model3_result is not None
            else None
        )

        # ====================================================
        # GOOGLE MAPS SUMMARY
        # ====================================================

        places_summary = {

            "available":
                places_result.get(
                    "available"
                ),

            "status":
                places_result.get(
                    "status"
                ),

            "search_type":
                places_result.get(
                    "search_type"
                ),

            "maps_search_url":
                places_result.get(
                    "maps_search_url"
                ),

        }

        # ====================================================
        # COMPACT GEMINI PAYLOAD
        #
        # Model 5 is intentionally NOT included.
        # ====================================================

        pipeline_data = {
    "patient": {
        "age": patient_data.get("age")
        if isinstance(patient_data, dict)
        else None,

        "sex_category": patient_data.get(
            "sex_category"
        )
        if isinstance(patient_data, dict)
        else None,
    },

    "scan": {
        "modality": modality,
        "modality_result": modality_result,
    },

    "tumor_detection": tumor_detection,

    "model3": model3_summary,

    "model4": model4_summary,

    "specialist_search": places_summary,
}

        # ====================================================
        # GEMINI
        # ====================================================

        try:

            return (
                gemini_service.generate_report(
                    pipeline_data
                )
            )

        except Exception as error:

            return {

                "success":
                    False,

                "status":
                    "gemini_failed",

                "error":
                    str(error),

            }


# ============================================================
# END OF ANALYSIS PIPELINE
# ============================================================