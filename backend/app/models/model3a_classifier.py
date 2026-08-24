# ============================================================
# MODEL 3A — BRAIN TUMOR MRI CLASSIFIER
# ============================================================
#
# Architecture : EfficientNet-B0
# Version      : V1
# Test Accuracy: 92.08%
#
# Classes:
#   0 -> glioma
#   1 -> meningioma
#   2 -> pituitary
#
# IMPORTANT:
# Model 3A is called only AFTER the upstream pipeline has
# established that a tumor is present.
#
# Therefore:
#   - We NEVER return "no tumor"
#   - If classification confidence is too low, we return:
#       tumor_present = True
#       tumor_type    = "undetermined"
#
# ============================================================

import os
from typing import Dict, Any

import torch
import torch.nn as nn

from torchvision import models, transforms

from PIL import Image


# ============================================================
# MODEL CONFIGURATION
# ============================================================

MODEL_NAME = "Model 3A"
MODEL_VERSION = "V1"

CLASSES = [
    "glioma",
    "meningioma",
    "pituitary",
]

CLASS_TO_INDEX = {
    "glioma": 0,
    "meningioma": 1,
    "pituitary": 2,
}

INDEX_TO_CLASS = {
    0: "glioma",
    1: "meningioma",
    2: "pituitary",
}


# ============================================================
# CONFIDENCE CONFIGURATION
# ============================================================

# If the model's highest probability is below this value,
# we do NOT force a tumor type.
#
# The pipeline still knows that a tumor is present because
# Model 3A is only called after tumor detection.
#
# This can be calibrated later using the validation set.

CONFIDENCE_THRESHOLD = 0.60


# ============================================================
# MODEL PATH
# ============================================================

# Current file:
#
# backend/app/models/model3a_classifier.py
#
# Three levels upward:
#
# backend/app/models
# backend/app
# backend
#
# Therefore:
# backend/models/Model3A.pth

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
    "Model3A.pth",
)


# ============================================================
# DEVICE
# ============================================================

DEVICE = torch.device(
    "cuda"
    if torch.cuda.is_available()
    else "cpu"
)


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

# Must match the preprocessing used during V1 training.

TRANSFORM = transforms.Compose([
    transforms.Resize(
        (224, 224)
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[
            0.485,
            0.456,
            0.406,
        ],
        std=[
            0.229,
            0.224,
            0.225,
        ],
    ),
])


# ============================================================
# CREATE MODEL
# ============================================================

def create_model():
    """
    Create the exact EfficientNet-B0 architecture
    used by Model 3A V1.
    """

    model = models.efficientnet_b0(
        weights=None
    )

    # Original EfficientNet-B0 classifier:
    #
    # Dropout(0.2)
    # Linear(1280 -> 1000)
    #
    # Model 3A V1 classifier:
    #
    # Dropout(0.3)
    # Linear(1280 -> 3)

    model.classifier = nn.Sequential(
        nn.Dropout(
            p=0.3
        ),

        nn.Linear(
            in_features=1280,
            out_features=3,
        ),
    )

    return model


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():
    """
    Load Model 3A V1 checkpoint.
    """

    if not os.path.exists(MODEL_PATH):

        raise FileNotFoundError(
            "Model 3A checkpoint not found:\n"
            f"{MODEL_PATH}"
        )

    print(
        f"[Model 3A] Loading checkpoint: "
        f"{MODEL_PATH}"
    )

    model = create_model()

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE,
        weights_only=False,
    )

    # --------------------------------------------------------
    # Support multiple checkpoint formats
    # --------------------------------------------------------

    if isinstance(
        checkpoint,
        dict
    ):

        if "model_state_dict" in checkpoint:

            state_dict = checkpoint[
                "model_state_dict"
            ]

        elif "state_dict" in checkpoint:

            state_dict = checkpoint[
                "state_dict"
            ]

        else:

            # Raw PyTorch state_dict
            state_dict = checkpoint

    else:

        raise RuntimeError(
            "Invalid Model 3A checkpoint format."
        )

    # --------------------------------------------------------
    # Load weights
    # --------------------------------------------------------

    model.load_state_dict(
        state_dict,
        strict=True,
    )

    # --------------------------------------------------------
    # Device
    # --------------------------------------------------------

    model = model.to(
        DEVICE
    )

    # --------------------------------------------------------
    # Evaluation mode
    # --------------------------------------------------------

    model.eval()

    print(
        "[Model 3A] Model loaded successfully."
    )

    print(
        f"[Model 3A] Device: {DEVICE}"
    )

    return model


# ============================================================
# GLOBAL MODEL
# ============================================================

model3a = load_model()


# ============================================================
# PREDICTION
# ============================================================

def predict_model3a(
    image: Image.Image,
) -> Dict[str, Any]:
    """
    Run Model 3A prediction.

    Input:
        PIL RGB image

    Output:
        Dictionary containing:

        - model
        - version
        - tumor_present
        - prediction
        - tumor_type
        - confidence
        - probabilities
        - device
        - message
    """

    # --------------------------------------------------------
    # Validate image
    # --------------------------------------------------------

    if image is None:

        raise ValueError(
            "No image supplied."
        )

    # --------------------------------------------------------
    # Convert to RGB
    # --------------------------------------------------------

    image = image.convert(
        "RGB"
    )

    # --------------------------------------------------------
    # Preprocess
    # --------------------------------------------------------

    tensor = TRANSFORM(
        image
    )

    # Add batch dimension
    tensor = tensor.unsqueeze(
        0
    )

    # Move to device
    tensor = tensor.to(
        DEVICE
    )

    # --------------------------------------------------------
    # Inference
    # --------------------------------------------------------

    with torch.no_grad():

        logits = model3a(
            tensor
        )

        probabilities = torch.softmax(
            logits,
            dim=1,
        )[0]

    # --------------------------------------------------------
    # Find highest probability
    # --------------------------------------------------------

    predicted_index = int(
        torch.argmax(
            probabilities
        ).item()
    )

    max_confidence = float(
        probabilities[
            predicted_index
        ].item()
    )

    # --------------------------------------------------------
    # Probability dictionary
    # --------------------------------------------------------

    probability_dict = {
        INDEX_TO_CLASS[index]: round(
            float(
                probabilities[index].item()
            ),
            6,
        )
        for index in range(3)
    }

    # ========================================================
    # LOW CONFIDENCE
    # ========================================================

    if (
        max_confidence
        < CONFIDENCE_THRESHOLD
    ):

        return {
            "model": MODEL_NAME,

            "version": MODEL_VERSION,

            "tumor_present": True,

            "prediction": "tumor_present",

            "tumor_type": "undetermined",

            "confidence": round(
                max_confidence,
                6,
            ),

            "probabilities": probability_dict,

            "device": str(
                DEVICE
            ),

            "message": (
                "Tumor is present, "
                "but the tumor type "
                "could not be determined "
                "with sufficient confidence."
            ),
        }

    # ========================================================
    # CONFIDENT CLASSIFICATION
    # ========================================================

    predicted_class = INDEX_TO_CLASS[
        predicted_index
    ]

    return {
        "model": MODEL_NAME,

        "version": MODEL_VERSION,

        "tumor_present": True,

        "prediction": predicted_class,

        "tumor_type": predicted_class,

        "confidence": round(
            max_confidence,
            6,
        ),

        "probabilities": probability_dict,

        "device": str(
            DEVICE
        ),

        "message": (
            f"Tumor classified as "
            f"{predicted_class}."
        ),
    }


# ============================================================
# MODEL INFORMATION
# ============================================================

def get_model3a_info():
    """
    Return Model 3A metadata.
    """

    return {
        "model": MODEL_NAME,

        "version": MODEL_VERSION,

        "architecture": "EfficientNet-B0",

        "classes": CLASSES,

        "class_to_index": CLASS_TO_INDEX,

        "input_size": [
            224,
            224,
        ],

        "input_channels": 3,

        "preprocessing": (
            "RGB + ImageNet normalization"
        ),

        "confidence_threshold": (
            CONFIDENCE_THRESHOLD
        ),

        "device": str(
            DEVICE
        ),

        "checkpoint": MODEL_PATH,

        "test_accuracy": 0.9208,
    }