# ============================================================
# MEDFUSION AI — COMPLETE ANALYSIS PIPELINE
#
# Pipeline:
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
#   Model 5
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
#   Model 5
#      ↓
#   Google Maps — Neurosurgery Hospital
#      ↓
#   Gemini
#
# IMPORTANT:
#
# - Missing Model 5 metadata is NEVER fabricated.
# - Model 4 tumor dimensions are NOT falsely converted into
#   MRI voxel dimensions.
# - Gemini receives only useful structured information.
# - Base64 segmentation images are NOT sent to Gemini.
# - Google Maps searches specifically for Neurosurgery.
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

from app.models.model5_who_classifier import (
    predict_model5,
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
        -> Model 5
        -> Google Maps
        -> Gemini

    CT:

        Model 1
        -> Model 2B
        -> Model 4A
        -> Model 5
        -> Google Maps
        -> Gemini

    Important:

    Model 5 is experimental and requires the exact metadata
    features on which its RandomForest classifier was trained.

    Missing metadata is never invented.

    Model 4 measurements are passed to Gemini as structured
    information, but are NOT falsely mapped to Model 5 MRI
    acquisition metadata.
    """

    # ========================================================
    # MODEL 5 REQUIRED FEATURES
    # ========================================================

    MODEL5_FEATURES = [

        "age",

        "sex_category",

        "voxel_x_mm",

        "voxel_y_mm",

        "slice_thickness_mm",

        "field_strength_t",

        "field_strength_category",

        "resolution_category",

        "slice_thickness_category",
    ]


    # ========================================================
    # CONSTRUCTOR
    # ========================================================

    def __init__(
        self,
        modality_model: ModalityModel,
        mri_model: MRITumorDetector,
        ct_model: CTTumorDetector,
    ):

        self.modality_model = modality_model

        self.mri_model = mri_model

        self.ct_model = ct_model


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
        # Normalize image path
        # ----------------------------------------------------

        image_path = Path(
            image_path
        )


        if not image_path.exists():

            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )


        # ----------------------------------------------------
        # Normalize patient data
        # ----------------------------------------------------

        patient_data = (
            patient_data
            if patient_data is not None
            else {}
        )


        # ====================================================
        # MODEL 1 — MODALITY
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
        ).upper()


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
                "Model 1 returned an unknown modality.",
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
        # MODEL 2A
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
        # NO TUMOR → STOP
        # ====================================================

        if not tumor_detected:

            result["pipeline_status"] = (
                "stopped_no_tumor"
            )

            result["message"] = (
                "No tumor detected by Model 2A. "
                "Pipeline stopped."
            )

            return result


        # ====================================================
        # MODEL 3
        # ====================================================

        with Image.open(
            image_path
        ) as image:

            model3_result = (
                predict_model3(
                    image.convert("RGB")
                )
            )


        result["model3"] = {

            "model":
                "Model 3",

            "result":
                model3_result,
        }


        # ====================================================
        # MODEL 4A
        # ====================================================

        with Image.open(
            image_path
        ) as image:

            model4_result = (
                predict_model4(
                    image.convert("RGB")
                )
            )


        result["model4"] = {

            "model":
                "Model 4A",

            "input_modality":
                "MRI",

            "experimental":
                False,

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

            result["pipeline_status"] = (
                "segmentation_found_no_tumor"
            )

            result["message"] = (
                "Model 2A detected a tumor, but "
                "Model 4A did not produce a "
                "segmented tumor region."
            )

            return result


        # ====================================================
        # MODEL 5
        # ====================================================

        model5_result = (
            self._run_model5(
                patient_data=patient_data,
                model4_result=model4_result,
            )
        )


        result["model5"] = (
            model5_result
        )


        # ====================================================
        # GOOGLE MAPS
        # ====================================================

        places_result = (
            self._run_places(
                location=location
            )
        )


        result["places"] = (
            places_result
        )


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

                model5_result=
                    model5_result,

                location=
                    location,

                places_result=
                    places_result,
            )
        )


        result["gemini"] = (
            gemini_result
        )


        # ====================================================
        # FINAL STATUS
        # ====================================================

        result["pipeline_status"] = (
            "completed"
        )


        result["message"] = (
            "MRI pipeline completed through "
            "Model 4A, Model 5, Google Maps and Gemini."
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
        # MODEL 2B
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
        # NO TUMOR → STOP
        # ====================================================

        if not tumor_detected:

            result["pipeline_status"] = (
                "stopped_no_tumor"
            )

            result["message"] = (
                "No tumor detected by Model 2B. "
                "Pipeline stopped."
            )

            return result


        # ====================================================
        # MODEL 4A
        #
        # Model 4A was trained for MRI.
        # CT usage remains experimental.
        # ====================================================

        with Image.open(
            image_path
        ) as image:

            model4_result = (
                predict_model4(
                    image.convert("RGB")
                )
            )


        result["model4"] = {

            "model":
                "Model 4A",

            "input_modality":
                "CT",

            "training_modality":
                "MRI",

            "experimental":
                True,

            "result":
                model4_result,
        }


        # ====================================================
        # MODEL 5
        # ====================================================

        model5_result = (
            self._run_model5(
                patient_data=patient_data,
                model4_result=model4_result,
            )
        )


        result["model5"] = (
            model5_result
        )


        # ====================================================
        # GOOGLE MAPS
        # ====================================================

        places_result = (
            self._run_places(
                location=location
            )
        )


        result["places"] = (
            places_result
        )


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

                model5_result=
                    model5_result,

                location=
                    location,

                places_result=
                    places_result,
            )
        )


        result["gemini"] = (
            gemini_result
        )


        # ====================================================
        # FINAL STATUS
        # ====================================================

        result["pipeline_status"] = (
            "completed"
        )


        result["message"] = (
            "CT tumor pipeline completed through "
            "Model 4A, Model 5, Google Maps and Gemini."
        )


        return result


    # ========================================================
    # MODEL 5
    # ========================================================

    def _run_model5(
        self,
        patient_data: Dict[str, Any],
        model4_result: Optional[
            Dict[str, Any]
        ] = None,
    ) -> Dict[str, Any]:

        # ====================================================
        # NORMALIZE DATA
        # ====================================================

        if patient_data is None:

            patient_data = {}


        # ====================================================
        # FIND MISSING FEATURES
        #
        # IMPORTANT:
        #
        # We ONLY check the actual features expected by the
        # trained RandomForest model.
        #
        # Model 4 measurements are NOT substituted here.
        # ====================================================

        missing = []

        for feature in self.MODEL5_FEATURES:

            if feature not in patient_data:

                missing.append(
                    feature
                )

                continue


            value = patient_data.get(
                feature
            )


            if value is None:

                missing.append(
                    feature
                )

                continue


            if (
                isinstance(
                    value,
                    str,
                )
                and not value.strip()
            ):

                missing.append(
                    feature
                )


        # ====================================================
        # MODEL 4 MEASUREMENTS
        #
        # Keep them available for the API/Gemini, but DO NOT
        # use them as fake MRI acquisition metadata.
        # ====================================================

        model4_measurements = {}

        if isinstance(
            model4_result,
            dict,
        ):

            measurements = (
                model4_result.get(
                    "measurements"
                )
            )

            if isinstance(
                measurements,
                dict,
            ):

                model4_measurements = (
                    measurements
                )


        # ====================================================
        # MISSING METADATA
        # ====================================================

        if missing:

            return {

                "available":
                    False,

                "status":
                    "missing_metadata",

                "model":
                    "Model 5",

                "classifier":
                    "RandomForestClassifier",

                "experimental":
                    True,

                "prediction":
                    None,

                "required_features":
                    self.MODEL5_FEATURES.copy(),

                "provided_features":
                    list(
                        patient_data.keys()
                    ),

                "missing_features":
                    missing,

                "model4_measurements_available":
                    bool(
                        model4_measurements
                    ),

                "model4_measurements":
                    model4_measurements,

                "message":
                    (
                        "Experimental WHO-grade prediction "
                        "is unavailable because the MRI "
                        "metadata required by the trained "
                        "Model 5 classifier was not supplied. "
                        "Model 4 tumor measurements were not "
                        "incorrectly substituted for MRI "
                        "acquisition metadata."
                    ),
            }


        # ====================================================
        # PREDICTION
        # ====================================================

        try:

            prediction = (
                predict_model5(
                    patient_data
                )
            )


            return {

                "available":
                    True,

                "status":
                    "success",

                "model":
                    "Model 5",

                "classifier":
                    "RandomForestClassifier",

                "experimental":
                    True,

                "prediction":
                    prediction,

                "model4_measurements_available":
                    bool(
                        model4_measurements
                    ),

                "model4_measurements":
                    model4_measurements,
            }


        except Exception as error:

            return {

                "available":
                    False,

                "status":
                    "prediction_failed",

                "model":
                    "Model 5",

                "classifier":
                    "RandomForestClassifier",

                "experimental":
                    True,

                "prediction":
                    None,

                "model4_measurements_available":
                    bool(
                        model4_measurements
                    ),

                "model4_measurements":
                    model4_measurements,

                "error":
                    str(error),

                "message":
                    (
                        "Model 5 could not generate an "
                        "experimental WHO-grade prediction."
                    ),
            }


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
                    (
                        "User location was not provided."
                    ),
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
        # VALIDATE COORDINATES
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
        # CREATE GOOGLE MAPS SEARCH URL
        #
        # IMPORTANT:
        #
        # This used to be:
        #
        #     specialist="hospital"
        #
        # Now it specifically requests Neurosurgery.
        # ====================================================

        try:

            maps_url = (
                places_service.create_maps_search_url(
                    specialist="Neurosurgery",

                    latitude=latitude,

                    longitude=longitude,
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
        model5_result: Dict[str, Any],
        location: Optional[
            Dict[str, float]
        ],
        places_result: Dict[str, Any],
    ) -> Dict[str, Any]:

        # ====================================================
        # EXTRACT ONLY USEFUL MODEL 4 INFORMATION
        #
        # DO NOT send:
        #
        # - mask_png_base64
        # - boundary_png_base64
        # - overlay_png_base64
        #
        # Those are large and unnecessary for the textual
        # Gemini report.
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
        # MODEL 5 SUMMARY
        # ====================================================

        model5_summary = {}


        if isinstance(
            model5_result,
            dict,
        ):

            model5_summary = {

                "available":
                    model5_result.get(
                        "available"
                    ),

                "status":
                    model5_result.get(
                        "status"
                    ),

                "prediction":
                    model5_result.get(
                        "prediction"
                    ),

                "missing_features":
                    model5_result.get(
                        "missing_features",
                        [],
                    ),

                "message":
                    model5_result.get(
                        "message"
                    ),
            }


        # ====================================================
        # MODEL 3 SUMMARY
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
        # This is intentionally much smaller than sending the
        # complete Model 4 response.
        # ====================================================

        pipeline_data = {

            "modality":
                modality,

            "modality_result":
                modality_result,

            "tumor_detection":
                tumor_detection,

            "model3":
                model3_summary,

            "model4":
                model4_summary,

            "model5":
                model5_summary,

            "specialist_search":
                places_summary,
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