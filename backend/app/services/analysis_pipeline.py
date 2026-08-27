from pathlib import Path
from typing import Any, Dict, Optional

from PIL import Image

from app.models.modality_model import ModalityModel
from app.models.mri_detector import MRITumorDetector
from app.models.ct_detector import CTTumorDetector
from app.models.model3_classifier import predict_model3
from app.models.model4_segmentation import predict_model4
from app.models.model5_who_classifier import predict_model5

from app.services.gemini_service import gemini_service
from app.services.places_service import places_service


class AnalysisPipeline:
    """
    MedFusion AI complete pipeline.

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

    If Model 2 detects no tumor:
        Pipeline stops.

    IMPORTANT:
        Model 4A is an MRI segmentation model.

        CT execution of Model 4A is therefore marked
        experimental.

    IMPORTANT:
        Model 5 is experimental and requires the metadata
        on which its classifier was trained.

        We DO NOT invent missing metadata.
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
        patient_data: Optional[Dict[str, Any]] = None,
        location: Optional[Dict[str, float]] = None,
    ) -> Dict[str, Any]:

        image_path = Path(
            image_path
        )

        if not image_path.exists():

            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

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
        location: Optional[Dict[str, float]],
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
        #
        # IMPORTANT:
        # predict_model4() already returns:
        #
        # - mask_png_base64
        # - boundary_png_base64
        # - overlay_png_base64
        #
        # We preserve the complete result.
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
                patient_data
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
                modality_result=modality_result,
                tumor_detection=tumor_detection,
                model3_result=model3_result,
                model4_result=model4_result,
                model5_result=model5_result,
                location=location,
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
            "Model 4A, Model 5 and Gemini."
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
        location: Optional[Dict[str, float]],
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
        # WARNING:
        # Model 4A was trained for MRI.
        # Therefore this remains experimental.
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
                patient_data
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
                modality_result=modality_result,
                tumor_detection=tumor_detection,
                model3_result=None,
                model4_result=model4_result,
                model5_result=model5_result,
                location=location,
            )
        )

        result["gemini"] = (
            gemini_result
        )

        result["pipeline_status"] = (
            "completed"
        )

        result["message"] = (
            "CT tumor pipeline completed through "
            "Model 4A, Model 5 and Gemini."
        )

        return result

    # ========================================================
    # MODEL 5
    # ========================================================

    def _run_model5(
        self,
        patient_data: Dict[str, Any],
    ) -> Dict[str, Any]:

        # ====================================================
        # FIND MISSING FEATURES
        # ====================================================

        missing = [

            feature

            for feature
            in self.MODEL5_FEATURES

            if (
                feature
                not in patient_data
            )

        ]

        # ====================================================
        # MISSING METADATA
        # ====================================================

        if missing:

            return {

                "available":
                    False,

                "status":
                    "missing_metadata",

                "experimental":
                    True,

                "required_features":
                    self.MODEL5_FEATURES,

                "provided_features":
                    list(
                        patient_data.keys()
                    ),

                "missing_features":
                    missing,

                "message":
                    (
                        "Model 5 was not executed because "
                        "its required trained features were "
                        "not supplied. Missing metadata was "
                        "not fabricated."
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
            }

        except Exception as error:

            return {

                "available":
                    False,

                "status":
                    "prediction_failed",

                "experimental":
                    True,

                "error":
                    str(error),
            }

    # ========================================================
    # GOOGLE MAPS
    # ========================================================

    @staticmethod
    def _run_places(
        location: Optional[Dict[str, float]],
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

        if latitude is None or longitude is None:

            return {

                "available":
                    False,

                "status":
                    "invalid_location",

                "maps_search_url":
                    None,

                "message":
                    "Valid latitude and longitude are required.",
            }

        # ====================================================
        # CREATE GOOGLE MAPS SEARCH URL
        # ====================================================

        try:

            maps_url = (
                places_service.create_maps_search_url(
                    specialist="hospital",
                    latitude=float(latitude),
                    longitude=float(longitude),
                )
            )

            return {

                "available":
                    True,

                "status":
                    "success",

                "search_type":
                    "hospital",

                "maps_search_url":
                    maps_url,
            }

        except Exception as error:

            return {

                "available":
                    False,

                "status":
                    "maps_url_generation_failed",

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
        model3_result: Optional[Dict[str, Any]],
        model4_result: Dict[str, Any],
        model5_result: Dict[str, Any],
        location: Optional[Dict[str, float]],
    ) -> Dict[str, Any]:

        # ====================================================
        # DATA SENT TO GEMINI
        # ====================================================

        pipeline_data = {

            "modality":
                modality,

            "modality_result":
                modality_result,

            "tumor_detection":
                tumor_detection,

            "model3":
                model3_result,

            # IMPORTANT:
            # This contains the Model 4 visual outputs.
            "model4":
                model4_result,

            "model5":
                model5_result,
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
# NOTE:
# `location` is still accepted by `_run_gemini()` so the
# existing pipeline call structure is preserved.
#
# It is intentionally NOT included in `pipeline_data`.
# Google Maps handles location separately.
# ============================================================