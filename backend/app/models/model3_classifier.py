# ============================================================
# MODEL 3 — MULTI-CLASS BRAIN TUMOR CLASSIFIER
# DenseNet169 — V2
# ============================================================

import os
from typing import Dict, Any

import torch
import torch.nn as nn
from torchvision import models, transforms
from PIL import Image


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "Model 3"
MODEL_VERSION = "V2"
ARCHITECTURE = "DenseNet169"

CLASSES = [
    "Astrocitoma",
    "Carcinoma",
    "Ependimoma",
    "Germinoma",
    "Glioblastoma",
    "Meduloblastoma",
    "Meningioma",
    "Neurocitoma",
    "Normal",
    "Oligodendroglioma",
    "Papiloma",
    "Schwannoma",
]

NUM_CLASSES = 12

NORMAL_CLASS = "Normal"

# Model prediction confidence threshold.
# If the model is below this threshold, the tumor type
# is returned as "Undetermined".
CONFIDENCE_THRESHOLD = 0.20


# ============================================================
# CLASS MAPPING
# ============================================================

CLASS_TO_INDEX = {
    name: index
    for index, name in enumerate(CLASSES)
}

INDEX_TO_CLASS = {
    index: name
    for index, name in enumerate(CLASSES)
}


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
    "Model3_V2.pth",
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
# CREATE DENSENET169
# ============================================================

def create_model():

    model = models.densenet169(
        weights=None
    )

    model.classifier = nn.Sequential(
        nn.Dropout(
            p=0.3
        ),
        nn.Linear(
            1664,
            NUM_CLASSES
        ),
    )

    return model


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    if not os.path.exists(MODEL_PATH):

        raise FileNotFoundError(
            f"Model 3 checkpoint not found:\n"
            f"{MODEL_PATH}"
        )

    checkpoint = torch.load(
        MODEL_PATH,
        map_location=DEVICE,
        weights_only=False,
    )

    if not isinstance(
        checkpoint,
        dict
    ):

        raise RuntimeError(
            "Invalid Model 3 checkpoint."
        )

    if "model_state_dict" not in checkpoint:

        raise RuntimeError(
            "model_state_dict not found "
            "inside Model3_V2.pth"
        )

    model = create_model()

    model.load_state_dict(
        checkpoint["model_state_dict"],
        strict=True,
    )

    model = model.to(
        DEVICE
    )

    model.eval()

    print(
        "[Model 3] Model loaded successfully."
    )

    print(
        f"[Model 3] Device: {DEVICE}"
    )

    return model


# ============================================================
# GLOBAL MODEL
# ============================================================

model3 = load_model()


# ============================================================
# PREDICTION
# ============================================================

def predict_model3(
    image: Image.Image,
) -> Dict[str, Any]:

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

    tensor = tensor.unsqueeze(
        0
    )

    tensor = tensor.to(
        DEVICE
    )

    # --------------------------------------------------------
    # Model inference
    # --------------------------------------------------------

    with torch.no_grad():

        logits = model3(
            tensor
        )

        probabilities = torch.softmax(
            logits,
            dim=1
        )[0]

    # --------------------------------------------------------
    # Get highest prediction
    # --------------------------------------------------------

    predicted_index = int(
        torch.argmax(
            probabilities
        ).item()
    )

    predicted_class = INDEX_TO_CLASS[
        predicted_index
    ]

    confidence = float(
        probabilities[
            predicted_index
        ].item()
    )

    # ========================================================
    # ALL CLASS PERCENTAGES
    # ========================================================

    all_predictions = {}

    for index in range(
        NUM_CLASSES
    ):

        class_name = INDEX_TO_CLASS[
            index
        ]

        # Do NOT expose Normal.
        if class_name == NORMAL_CLASS:
            continue

        percentage = (
            float(
                probabilities[index].item()
            )
            * 100
        )

        all_predictions[
            class_name
        ] = round(
            percentage,
            2
        )

    # --------------------------------------------------------
    # Sort highest probability first
    # --------------------------------------------------------

    all_predictions = dict(
        sorted(
            all_predictions.items(),
            key=lambda item: item[1],
            reverse=True,
        )
    )

    # ========================================================
    # NORMAL PREDICTION
    # ========================================================

    if predicted_class == NORMAL_CLASS:

        return {
            "tumor_detected": True,
            "tumor_type": "Undetermined",
            "confidence_percent": round(
                confidence * 100,
                2
            ),
            "predictions": all_predictions,
            "message": (
                "Tumor detected, but the "
                "tumor type could not be determined."
            ),
        }

    # ========================================================
    # LOW CONFIDENCE
    # ========================================================

    if confidence < CONFIDENCE_THRESHOLD:

        return {
            "tumor_detected": True,
            "tumor_type": "Undetermined",
            "confidence_percent": round(
                confidence * 100,
                2
            ),
            "predictions": all_predictions,
            "message": (
                "Tumor detected, but the tumor "
                "type could not be determined "
                "with sufficient confidence."
            ),
        }

    # ========================================================
    # CONFIDENT PREDICTION
    # ========================================================

    return {
        "tumor_detected": True,
        "tumor_type": predicted_class,
        "confidence_percent": round(
            confidence * 100,
            2
        ),
        "predictions": all_predictions,
        "message": (
            f"Tumor detected: {predicted_class}."
        ),
    }


# ============================================================
# MODEL INFORMATION
# ============================================================

def get_model3_info():

    return {
        "model": MODEL_NAME,
        "version": MODEL_VERSION,
        "architecture": ARCHITECTURE,
        "classes": [
            cls
            for cls in CLASSES
            if cls != NORMAL_CLASS
        ],
        "num_classes": NUM_CLASSES,
        "input_size": [
            224,
            224,
        ],
        "input_channels": 3,
        "preprocessing": (
            "RGB + ImageNet normalization"
        ),
        "confidence_threshold": CONFIDENCE_THRESHOLD,
        "device": str(DEVICE),
        "checkpoint": MODEL_PATH,
        "test_accuracy": 0.8834645669291339,
        "test_balanced_accuracy": 0.890063660158899,
        "test_macro_f1": 0.8887707925700914,
    }