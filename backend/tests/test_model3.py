import os
import sys

from PIL import Image


# ============================================================
# BACKEND PATH
# ============================================================

BACKEND_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(
    0,
    BACKEND_DIR
)


# ============================================================
# MODEL
# ============================================================

from app.models.model3_classifier import (
    predict_model3
)


# ============================================================
# TEST IMAGE
# ============================================================

IMAGE_PATH = os.path.join(
    BACKEND_DIR,
    "test",
    "papi.webp"
)


# ============================================================
# CHECK IMAGE
# ============================================================

if not os.path.exists(
    IMAGE_PATH
):

    print(
        f"Image not found:\n{IMAGE_PATH}"
    )

    sys.exit(1)


# ============================================================
# LOAD IMAGE
# ============================================================

image = Image.open(
    IMAGE_PATH
)


# ============================================================
# PREDICT
# ============================================================

result = predict_model3(
    image
)


# ============================================================
# OUTPUT
# ============================================================

print()
print("=" * 45)
print("MODEL 3")
print("=" * 45)

print(
    f"Tumor detected : "
    f"{result['tumor_detected']}"
)

print(
    f"Tumor type     : "
    f"{result['tumor_type']}"
)

print(
    f"Confidence     : "
    f"{result['confidence_percent']:.2f}%"
)

print()
print("Tumor probabilities")
print("-" * 45)

for tumor, percentage in result[
    "predictions"
].items():

    print(
        f"{tumor:20s} : "
        f"{percentage:.2f}%"
    )

print()
print(
    result["message"]
)

print("=" * 45)