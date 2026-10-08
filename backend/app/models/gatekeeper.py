from pathlib import Path

import numpy as np
import tensorflow as tf


# ============================================================
# PATHS
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parents[2]
MODEL_DIR = BACKEND_DIR / "models"

STAGE1_PATH = MODEL_DIR / "stage1.keras"
STAGE2_PATH = MODEL_DIR / "stage2.keras"


# ============================================================
# LOAD MODELS
# ============================================================

print("Loading MedFusion AI Model 0...")

stage1 = tf.keras.models.load_model(
    STAGE1_PATH,
    compile=False
)

stage2 = tf.keras.models.load_model(
    STAGE2_PATH,
    compile=False
)

print("Stage 1 loaded successfully.")
print("Stage 2 loaded successfully.")


# ============================================================
# IMAGE PREPROCESSING
# EXACTLY MATCHES ORIGINAL MODEL 0 NOTEBOOK
# ============================================================

def preprocess_model0_image(image_path):

    img = tf.io.read_file(
        str(image_path)
    )

    img = tf.image.decode_image(
        img,
        channels=3,
        expand_animations=False
    )

    img.set_shape(
        [None, None, 3]
    )

    img = tf.image.resize(
        img,
        (224, 224)
    )

    img = tf.cast(
        img,
        tf.float32
    )

    img = tf.keras.applications.mobilenet_v2.preprocess_input(
        img
    )

    return tf.expand_dims(
        img,
        axis=0
    )


# ============================================================
# COMPLETE MODEL 0 PREDICTION
# ============================================================

def model0_predict(image_path):

    img = preprocess_model0_image(
        image_path
    )

    # ========================================================
    # STAGE 1
    # MRI/CT vs OTHER
    # ========================================================

    stage1_probability = float(
        stage1.predict(
            img,
            verbose=0
        )[0][0]
    )

    print(
        f"\n[Stage 1] MRI/CT probability: "
        f"{stage1_probability:.6f}"
    )

    # --------------------------------------------------------
    # OTHER
    # --------------------------------------------------------

    if stage1_probability < 0.5:

        print(
            "[Model 0] REJECTED at Stage 1"
        )

        return {
            "final_prediction": 0,
            "final_result": "REJECT",

            "stage1_probability":
                stage1_probability,

            "stage1_result":
                "OTHER",

            "stage2_probability":
                None,

            "stage2_result":
                None
        }

    # ========================================================
    # STAGE 2
    # BRAIN vs NOT BRAIN
    # ========================================================

    stage2_probability = float(
        stage2.predict(
            img,
            verbose=0
        )[0][0]
    )

    print(
        f"[Stage 2] Brain probability: "
        f"{stage2_probability:.6f}"
    )

    # --------------------------------------------------------
    # NOT BRAIN
    # --------------------------------------------------------

    if stage2_probability < 0.5:

        print(
            "[Model 0] REJECTED at Stage 2"
        )

        return {
            "final_prediction": 0,
            "final_result": "REJECT",

            "stage1_probability":
                stage1_probability,

            "stage1_result":
                "MRI/CT",

            "stage2_probability":
                stage2_probability,

            "stage2_result":
                "NOT BRAIN"
        }

    # ========================================================
    # BRAIN MRI / CT
    # ========================================================

    print(
        "[Model 0] ACCEPTED: Brain MRI/CT"
    )

    return {
        "final_prediction": 1,
        "final_result": "ACCEPT",

        "stage1_probability":
            stage1_probability,

        "stage1_result":
            "MRI/CT",

        "stage2_probability":
            stage2_probability,

        "stage2_result":
            "BRAIN"
    }


# ============================================================
# BACKWARD COMPATIBILITY
# ============================================================

def gatekeeper_predict(image_path):
    return model0_predict(image_path)