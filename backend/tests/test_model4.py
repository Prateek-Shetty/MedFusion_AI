import os
import sys
import base64

from PIL import Image


# ============================================================
# PATH
# ============================================================

BACKEND_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(0, BACKEND_DIR)


# ============================================================
# MODEL
# ============================================================

from app.models.model4_segmentation import (
    predict_model4,
    get_model4_info
)


# ============================================================
# TEST IMAGE
# ============================================================

IMAGE_PATH = os.path.join(
    BACKEND_DIR,
    "test",
    "B.jpg"
)

OUTPUT_DIR = os.path.join(
    BACKEND_DIR,
    "test_outputs"
)

os.makedirs(
    OUTPUT_DIR,
    exist_ok=True
)


# ============================================================
# CHECK IMAGE
# ============================================================

if not os.path.exists(IMAGE_PATH):

    print("Test image not found:")
    print(IMAGE_PATH)
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

result = predict_model4(
    image
)


# ============================================================
# SAVE MASK
# ============================================================

mask_path = os.path.join(
    OUTPUT_DIR,
    "model4_tumor_mask.png"
)

with open(
    mask_path,
    "wb"
) as f:

    f.write(
        base64.b64decode(
            result["segmentation"][
                "mask_png_base64"
            ]
        )
    )


# ============================================================
# SAVE BOUNDARY
# ============================================================

boundary_path = os.path.join(
    OUTPUT_DIR,
    "model4_tumor_boundary.png"
)

with open(
    boundary_path,
    "wb"
) as f:

    f.write(
        base64.b64decode(
            result["segmentation"][
                "boundary_png_base64"
            ]
        )
    )


# ============================================================
# SAVE HIGHLIGHTED OVERLAY
# ============================================================

overlay_path = os.path.join(
    OUTPUT_DIR,
    "model4_tumor_highlighted.png"
)

with open(
    overlay_path,
    "wb"
) as f:

    f.write(
        base64.b64decode(
            result["segmentation"][
                "overlay_png_base64"
            ]
        )
    )


# ============================================================
# PRINT RESULTS
# ============================================================

print()
print("=" * 70)
print("MODEL 4A — MRI TUMOR SEGMENTATION")
print("=" * 70)

print(
    "\nTumor detected :",
    result["tumor_detected"]
)

m = result["measurements"]

print("\nMEASUREMENTS")
print("-" * 70)

print(
    f"Area                : "
    f"{m['area_pixels']} pixels²"
)

print(
    f"Tumor percentage    : "
    f"{m['tumor_percentage']:.4f}%"
)

print(
    f"Boundary pixels     : "
    f"{m['boundary_pixels']}"
)

print(
    f"Mean confidence     : "
    f"{m['mean_confidence_percent']:.2f}%"
)

print(
    f"Max confidence      : "
    f"{m['max_confidence_percent']:.2f}%"
)

print("\nBOUNDING BOX")
print("-" * 70)

print(
    m["bounding_box"]
)

print("\nCENTROID")
print("-" * 70)

print(
    m["centroid"]
)

print("\nOUTPUT FILES")
print("-" * 70)

print(
    "Tumor mask     :",
    mask_path
)

print(
    "Tumor boundary :",
    boundary_path
)

print(
    "Highlighted MRI:",
    overlay_path
)

print()
print("=" * 70)
print("MODEL 4A TEST COMPLETE")
print("=" * 70)