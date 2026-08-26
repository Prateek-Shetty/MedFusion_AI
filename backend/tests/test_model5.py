import os
import sys


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

from app.models.model5_who_classifier import (
    predict_model5,
    get_model5_info
)


# ============================================================
# SAMPLE MRI METADATA
# ============================================================
#
# These are TEST VALUES only.
# Do not use them as real patient metadata.
#
# ============================================================

metadata = {

    "age": 45,

    "sex_category": "male",

    "voxel_x_mm": 1.0,

    "voxel_y_mm": 1.0,

    "slice_thickness_mm": 5.0,

    "field_strength_t": 1.5,

    "field_strength_category": "1.5T",

    "resolution_category": "standard",

    "slice_thickness_category": "thick",
}


# ============================================================
# MODEL INFO
# ============================================================

print("=" * 70)
print("MODEL 5 — WHO GRADE CLASSIFIER TEST")
print("=" * 70)

info = get_model5_info()

print("\nModel:")
print(info)


# ============================================================
# PREDICTION
# ============================================================

print("\nPrediction:")
print("-" * 70)

result = predict_model5(
    metadata
)

print(
    "WHO Grade:",
    result["who_grade"]
)

print(
    "Confidence:",
    f"{result['confidence_percent']:.2f}%"
)

print("\nProbabilities:")

for grade, probability in result[
    "probabilities"
].items():

    print(
        f"Grade {grade}: "
        f"{probability:.2f}%"
    )


print("\n" + "=" * 70)
print("MODEL 5 TEST COMPLETE")
print("=" * 70)