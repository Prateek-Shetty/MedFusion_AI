import sys
from pathlib import Path

from PIL import Image


# ============================================================
# ADD BACKEND DIRECTORY TO PYTHON PATH
# ============================================================

BACKEND_DIR = Path(__file__).resolve().parents[1]

sys.path.insert(
    0,
    str(BACKEND_DIR)
)


# ============================================================
# IMPORT MODEL 0
# ============================================================

from app.models.gatekeeper import gatekeeper_predict


# ============================================================
# TEST IMAGE
# ============================================================

IMAGE_PATH = BACKEND_DIR / "test" / "E.jpg"


# ============================================================
# HEADER
# ============================================================

print("\n========================================")
print("MEDFUSION AI MODEL 0 DIAGNOSTIC TEST")
print("========================================")

print(
    "Backend :",
    BACKEND_DIR
)

print(
    "Image   :",
    IMAGE_PATH
)


# ============================================================
# CHECK IMAGE EXISTS
# ============================================================

if not IMAGE_PATH.exists():

    raise FileNotFoundError(
        f"Test image not found: {IMAGE_PATH}"
    )


# ============================================================
# CHECK IMAGE INFORMATION
# ============================================================

image = Image.open(
    IMAGE_PATH
)

print("\nIMAGE INFORMATION")
print("----------------------------")

print(
    "Format :",
    image.format
)

print(
    "Size   :",
    image.size
)

print(
    "Mode   :",
    image.mode
)


# ============================================================
# RUN MODEL 0
# ============================================================

result = gatekeeper_predict(
    IMAGE_PATH
)


# ============================================================
# COMPLETE RAW RESULT
# ============================================================

print("\n========================================")
print("MODEL 0 RAW RESULT")
print("========================================")

for key, value in result.items():

    print(
        f"{key}: {value}"
    )


# ============================================================
# INTERPRETATION
# ============================================================

print("\n========================================")
print("INTERPRETATION")
print("========================================")


# ------------------------------------------------------------
# STAGE 1
# ------------------------------------------------------------

stage1_prob = result[
    "stage1_probability"
]

print(
    f"Stage 1 probability = "
    f"{stage1_prob:.8f}"
)


if stage1_prob >= 0.5:

    print(
        "Stage 1 decision      = MRI/CT"
    )

else:

    print(
        "Stage 1 decision      = OTHER"
    )


# ------------------------------------------------------------
# STAGE 2
# ------------------------------------------------------------

stage2_prob = result[
    "stage2_probability"
]


if stage2_prob is not None:

    print(
        f"Stage 2 probability = "
        f"{stage2_prob:.8f}"
    )

    if stage2_prob >= 0.5:

        print(
            "Stage 2 decision      = BRAIN"
        )

    else:

        print(
            "Stage 2 decision      = NOT BRAIN"
        )

else:

    print(
        "Stage 2 was not executed."
    )


# ============================================================
# FINAL RESULT
# ============================================================

final_prediction = result[
    "final_prediction"
]

print(
    f"\nFINAL OUTPUT = "
    f"{final_prediction}"
)


if final_prediction == 1:

    print(
        "FINAL DECISION = ACCEPT"
    )

else:

    print(
        "FINAL DECISION = REJECT"
    )


# ============================================================
# END
# ============================================================

print(
    "========================================\n"
)