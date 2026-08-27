from pathlib import Path

from PIL import Image

from app.models.modality_model import ModalityModel
from app.models.mri_detector import MRITumorDetector
from app.models.ct_detector import CTTumorDetector
from app.models.model3_classifier import predict_model3
from app.models.model4_segmentation import predict_model4

class AnalysisPipeline:
    """
    MedFusion AI analysis pipeline.

    Current stages:

        Model 1
            ↓
        MRI / CT
            ↓
        Model 2A / Model 2B
            ↓
        Tumor / No Tumor
            ↓
        MRI + Tumor -> Model 3

    Later stages:
        Model 4
        Model 5
        Gemini
        Hospital recommendation
    """

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
    # FULL PIPELINE
    # ========================================================

    def run(
        self,
        image_path: Path,
    ):

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        # ====================================================
        # MODEL 1 — MODALITY
        # ====================================================

        modality_result = self.modality_model.predict(
            image_path
        )

        modality = modality_result[
            "predicted_modality"
        ]

        # ====================================================
        # MRI BRANCH
        # ====================================================

        if modality == "MRI":

            # ------------------------------------------------
            # MODEL 2A — MRI TUMOR DETECTOR
            # ------------------------------------------------

            tumor_result = self.mri_model.predict(
                image_path
            )

            predicted_class = tumor_result[
                "predicted_class"
            ]

            tumor_detected = (
                str(predicted_class).lower()
                == "tumor"
            )

            result = {
                "pipeline_stage": "tumor_detection",
                "completed": True,

                "modality": modality_result,

                "tumor_detection": {
                    "model": "Model 2A",
                    "type": "MRI Tumor Detector",
                    **tumor_result,
                },

                "tumor_detected": tumor_detected,
            }

            # ------------------------------------------------
            # NO TUMOR → STOP
            # ------------------------------------------------

            if not tumor_detected:

                result["pipeline_status"] = (
                    "stopped_no_tumor"
                )

                return result

            # ------------------------------------------------
            # MODEL 3 — MRI TUMOR CLASSIFICATION
            # ------------------------------------------------

            with Image.open(image_path) as image:

                image = image.convert("RGB")

                model3_result = predict_model3(
                    image
                )

            result["model3"] = {
                "model": "Model 3",
                "version": "V2",
                "architecture": "DenseNet169",
                **model3_result,
            }

            # ------------------------------------------------
            # Continue to Model 4
            # ------------------------------------------------

            result["pipeline_stage"] = (
                "model3_classification"
            )

            result["pipeline_status"] = (
                "tumor_detected_continue"
            )

            return result

        # ====================================================
        # CT BRANCH
        # ====================================================

        elif modality == "CT":

            # ------------------------------------------------
            # MODEL 2B — CT TUMOR DETECTOR
            # ------------------------------------------------

            tumor_result = self.ct_model.predict(
                image_path
            )

            predicted_class = tumor_result[
                "predicted_class"
            ]

            tumor_detected = (
                str(predicted_class).lower()
                == "tumor"
            )

            result = {
                "pipeline_stage": "tumor_detection",
                "completed": True,

                "modality": modality_result,

                "tumor_detection": {
                    "model": "Model 2B",
                    "type": "CT Tumor Detector",
                    **tumor_result,
                },

                "tumor_detected": tumor_detected,
            }

            # ------------------------------------------------
            # NO TUMOR → STOP
            # ------------------------------------------------

            if not tumor_detected:

                result["pipeline_status"] = (
                    "stopped_no_tumor"
                )

                return result

            # ------------------------------------------------
            # CT TUMOR → MODEL 4 NEXT
            # ------------------------------------------------

            result["pipeline_stage"] = (
                "tumor_detection"
            )

            result["pipeline_status"] = (
                "tumor_detected_continue"
            )

            return result

        # ====================================================
        # UNKNOWN MODALITY
        # ====================================================

        else:

            return {
                "pipeline_stage": "modality_detection",
                "completed": False,

                "modality": modality_result,

                "pipeline_status": (
                    "stopped_unknown_modality"
                ),
            }