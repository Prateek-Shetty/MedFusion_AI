# ============================================================
# MODEL 5 — WHO GRADE CLASSIFIER
# RandomForest + MRI metadata
# ============================================================

import os
import joblib
import pandas as pd


# ============================================================
# CONFIG
# ============================================================

MODEL_NAME = "Model 5"
MODEL_VERSION = "WHO Grade Classifier"

CLASSES = [1, 2, 3]

FEATURES = [
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

    if not os.path.exists(MODEL_PATH):

        raise FileNotFoundError(
            f"Model 5 checkpoint not found:\n"
            f"{MODEL_PATH}"
        )

    model = joblib.load(
        MODEL_PATH
    )

    print(
        "[Model 5] Model loaded successfully."
    )

    print(
        "[Model 5] RandomForestClassifier"
    )

    return model


# ============================================================
# GLOBAL MODEL
# ============================================================

model5 = load_model()


# ============================================================
# VALIDATE INPUT
# ============================================================

def validate_metadata(metadata):

    missing = [
        feature
        for feature in FEATURES
        if feature not in metadata
    ]

    if missing:

        raise ValueError(
            "Missing Model 5 features: "
            + ", ".join(missing)
        )


# ============================================================
# PREDICTION
# ============================================================

def predict_model5(metadata):

    validate_metadata(
        metadata
    )

    # Keep exactly the feature order used
    # during training.
    data = {
        feature: [
            metadata[feature]
        ]
        for feature in FEATURES
    }

    dataframe = pd.DataFrame(
        data
    )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    prediction = model5.predict(
        dataframe
    )

    predicted_grade = int(
        prediction[0]
    )

    # --------------------------------------------------------
    # Probabilities
    # --------------------------------------------------------

    probabilities_raw = (
        model5.predict_proba(
            dataframe
        )[0]
    )

    probabilities = {}

    for class_value, probability in zip(
        model5.classes_,
        probabilities_raw
    ):

        probabilities[
            f"Grade {int(class_value)}"
        ] = round(
            float(probability) * 100,
            2
        )

    confidence = float(
        max(probabilities_raw)
    ) * 100

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    return {

        "who_grade":
            predicted_grade,

        "confidence_percent":
            round(
                confidence,
                2
            ),

        "probabilities":
            probabilities,
    }


# ============================================================
# MODEL INFORMATION
# ============================================================

def get_model5_info():

    return {

        "model":
            MODEL_NAME,

        "version":
            MODEL_VERSION,

        "classifier":
            "RandomForestClassifier",

        "n_estimators":
            400,

        "classes":
            CLASSES,

        "features":
            FEATURES,

        "checkpoint":
            MODEL_PATH,
    }