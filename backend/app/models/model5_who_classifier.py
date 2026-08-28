# ============================================================
# MODEL 5 — WHO GRADE CLASSIFIER
# RandomForest + MRI metadata
#
# IMPORTANT:
# Model 5 WHO-grade prediction is EXPERIMENTAL.
# It must NOT be treated as a confirmed clinical diagnosis.
#
# FIXES:
# 1. Missing metadata no longer crashes the entire pipeline.
# 2. Missing metadata is NEVER invented.
# 3. WHO prediction is performed only when ALL required
#    trained features are actually available.
# 4. Model is loaded only once at application startup.
# 5. Prediction output contains an explicit availability/status.
# 6. pandas DataFrame is created only when prediction is possible.
# ============================================================

import os
from typing import Any, Dict, List

import joblib
import pandas as pd


# ============================================================
# CONFIG
# ============================================================

MODEL_NAME = "Model 5"

MODEL_VERSION = "WHO Grade Classifier"

CLASSIFIER_TYPE = "RandomForestClassifier"

MODEL_STATUS = "experimental"

CLASSES = [1, 2, 3]


# ============================================================
# FEATURES
#
# These MUST remain in exactly the same order expected by the
# trained RandomForest model.
# ============================================================

FEATURES: List[str] = [
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


# ============================================================
# MODEL PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.dirname(
            os.path.abspath(__file__)
        )
    )
)

MODEL_PATH = os.path.join(
    BASE_DIR,
    "models",
    "Model5_WHO_Grade_Classifier.joblib",
)


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():
    """
    Load the trained Model 5 RandomForest classifier.

    The model is loaded once when this module is imported.
    """

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "Model 5 checkpoint not found:\n"
            f"{MODEL_PATH}"
        )

    model = joblib.load(
        MODEL_PATH
    )

    print(
        "[Model 5] Model loaded successfully."
    )

    print(
        "[Model 5] Classifier: "
        f"{CLASSIFIER_TYPE}"
    )

    print(
        "[Model 5] Status: "
        f"{MODEL_STATUS}"
    )

    return model


# ============================================================
# GLOBAL MODEL
# ============================================================

# Load once.
# Do NOT load the .joblib file for every prediction.
model5 = load_model()


# ============================================================
# METADATA HELPERS
# ============================================================

def get_missing_features(
    metadata: Dict[str, Any],
) -> List[str]:
    """
    Return Model 5 features that are missing or unusable.

    None and empty-string values are treated as unavailable.

    We intentionally do NOT invent default values.
    """

    if not isinstance(metadata, dict):
        return FEATURES.copy()

    missing = []

    for feature in FEATURES:

        if feature not in metadata:
            missing.append(feature)
            continue

        value = metadata.get(feature)

        if value is None:
            missing.append(feature)
            continue

        if isinstance(value, str) and not value.strip():
            missing.append(feature)

    return missing


# ============================================================
# VALIDATE INPUT
# ============================================================

def validate_metadata(
    metadata: Dict[str, Any],
) -> None:
    """
    Strict validation helper.

    This function is retained for callers that explicitly want
    strict validation.

    The main prediction function does NOT use this to crash
    the pipeline. It handles missing metadata gracefully.
    """

    if not isinstance(metadata, dict):
        raise ValueError(
            "Model 5 metadata must be a dictionary."
        )

    missing = get_missing_features(
        metadata
    )

    if missing:
        raise ValueError(
            "Missing Model 5 features: "
            + ", ".join(missing)
        )


# ============================================================
# MODEL 5 AVAILABILITY CHECK
# ============================================================

def is_model5_available(
    metadata: Dict[str, Any],
) -> bool:
    """
    Return True only when every required trained feature
    is available.

    No metadata is inferred or fabricated.
    """

    missing = get_missing_features(
        metadata
    )

    return len(missing) == 0


# ============================================================
# BUILD MODEL INPUT
# ============================================================

def _build_dataframe(
    metadata: Dict[str, Any],
) -> pd.DataFrame:
    """
    Build the one-row DataFrame in the exact feature order
    used during Model 5 training.
    """

    data = {
        feature: [
            metadata[feature]
        ]
        for feature in FEATURES
    }

    return pd.DataFrame(
        data,
        columns=FEATURES,
    )


# ============================================================
# UNAVAILABLE RESULT
# ============================================================

def _unavailable_result(
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Return a safe result when the required Model 5 metadata
    is unavailable.

    This prevents Model 5 from crashing the complete pipeline.
    """

    missing = get_missing_features(
        metadata
    )

    return {
        "available": False,

        "status": "not_available",

        "model": MODEL_NAME,

        "version": MODEL_VERSION,

        "classifier": CLASSIFIER_TYPE,

        "experimental": True,

        "who_grade": None,

        "confidence_percent": None,

        "probabilities": {},

        "missing_features": missing,

        "message": (
            "Experimental WHO-grade prediction is not "
            "available because required MRI metadata "
            "is missing. No missing values were inferred "
            "or invented."
        ),
    }


# ============================================================
# PREDICTION
# ============================================================

def predict_model5(
    metadata: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Predict WHO grade using Model 5.

    IMPORTANT:

    - Prediction occurs only if ALL trained features exist.
    - Missing metadata does NOT crash the pipeline.
    - No metadata is invented.
    - The result is explicitly marked experimental.
    """

    # --------------------------------------------------------
    # Basic input validation
    # --------------------------------------------------------

    if metadata is None:
        metadata = {}

    if not isinstance(metadata, dict):
        return {
            "available": False,

            "status": "invalid_input",

            "model": MODEL_NAME,

            "version": MODEL_VERSION,

            "classifier": CLASSIFIER_TYPE,

            "experimental": True,

            "who_grade": None,

            "confidence_percent": None,

            "probabilities": {},

            "missing_features": FEATURES.copy(),

            "message": (
                "Model 5 requires MRI metadata in "
                "dictionary format."
            ),
        }

    # --------------------------------------------------------
    # Check required metadata
    # --------------------------------------------------------

    missing = get_missing_features(
        metadata
    )

    if missing:
        return _unavailable_result(
            metadata
        )

    # --------------------------------------------------------
    # Build DataFrame
    # --------------------------------------------------------

    try:

        dataframe = _build_dataframe(
            metadata
        )

    except Exception as error:

        return {
            "available": False,

            "status": "input_error",

            "model": MODEL_NAME,

            "version": MODEL_VERSION,

            "classifier": CLASSIFIER_TYPE,

            "experimental": True,

            "who_grade": None,

            "confidence_percent": None,

            "probabilities": {},

            "missing_features": [],

            "message": (
                "Model 5 could not prepare the supplied "
                "metadata for prediction."
            ),

            "error": str(error),
        }

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    try:

        prediction = model5.predict(
            dataframe
        )

        predicted_grade = int(
            prediction[0]
        )

        # ----------------------------------------------------
        # Probabilities
        # ----------------------------------------------------

        probabilities_raw = (
            model5.predict_proba(
                dataframe
            )[0]
        )

        probabilities: Dict[
            str,
            float
        ] = {}

        for class_value, probability in zip(
            model5.classes_,
            probabilities_raw,
        ):

            probabilities[
                f"Grade {int(class_value)}"
            ] = round(
                float(probability) * 100,
                2,
            )

        # ----------------------------------------------------
        # Confidence
        # ----------------------------------------------------

        confidence = (
            float(
                max(probabilities_raw)
            ) * 100
        )

        # ----------------------------------------------------
        # Result
        # ----------------------------------------------------

        return {

            "available":
                True,

            "status":
                "success",

            "model":
                MODEL_NAME,

            "version":
                MODEL_VERSION,

            "classifier":
                CLASSIFIER_TYPE,

            "experimental":
                True,

            "who_grade":
                predicted_grade,

            "confidence_percent":
                round(
                    confidence,
                    2,
                ),

            "probabilities":
                probabilities,

            "missing_features":
                [],

            "message": (
                "Experimental AI-generated WHO-grade "
                "classification. This result is not a "
                "confirmed clinical diagnosis."
            ),
        }

    except Exception as error:

        # ----------------------------------------------------
        # Do not allow Model 5 to destroy the complete
        # MedFusion pipeline.
        # ----------------------------------------------------

        return {

            "available":
                False,

            "status":
                "prediction_error",

            "model":
                MODEL_NAME,

            "version":
                MODEL_VERSION,

            "classifier":
                CLASSIFIER_TYPE,

            "experimental":
                True,

            "who_grade":
                None,

            "confidence_percent":
                None,

            "probabilities":
                {},

            "missing_features":
                [],

            "message": (
                "Model 5 could not generate an experimental "
                "WHO-grade prediction from the supplied "
                "metadata."
            ),

            "error":
                str(error),
        }


# ============================================================
# MODEL INFORMATION
# ============================================================

def get_model5_info() -> Dict[str, Any]:
    """
    Return Model 5 configuration and status information.
    """

    # Get actual number of estimators when available.
    try:
        n_estimators = int(
            model5.n_estimators
        )
    except Exception:
        n_estimators = 400

    return {

        "model":
            MODEL_NAME,

        "version":
            MODEL_VERSION,

        "status":
            MODEL_STATUS,

        "experimental":
            True,

        "classifier":
            CLASSIFIER_TYPE,

        "n_estimators":
            n_estimators,

        "classes":
            CLASSES,

        "features":
            FEATURES.copy(),

        "feature_count":
            len(FEATURES),

        "checkpoint":
            MODEL_PATH,
    }


# ============================================================
# MODEL 5 STATUS
# ============================================================

def get_model5_status() -> Dict[str, Any]:
    """
    Lightweight status endpoint/helper.

    Useful for the API or frontend to determine whether
    Model 5 is available without running a prediction.
    """

    return {

        "model":
            MODEL_NAME,

        "version":
            MODEL_VERSION,

        "status":
            MODEL_STATUS,

        "experimental":
            True,

        "loaded":
            model5 is not None,

        "checkpoint":
            MODEL_PATH,

        "required_features":
            FEATURES.copy(),
    }