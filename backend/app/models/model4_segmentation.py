# ============================================================
# MODEL 4A — MRI TUMOR SEGMENTATION
# EfficientNet-B0 + Attention U-Net
# ============================================================

import os
import io
import base64

import numpy as np
import tensorflow as tf

from PIL import Image


# ============================================================
# CONFIGURATION
# ============================================================

MODEL_NAME = "Model 4A"
MODEL_VERSION = "Final"
ARCHITECTURE = "EfficientNetB0_AttentionUNet"

INPUT_SIZE = 256
MASK_THRESHOLD = 0.50


# ============================================================
# MODEL PERFORMANCE
# ============================================================

TEST_SAMPLES = 851

MEAN_DICE = 0.8466
MEDIAN_DICE = 0.9289
MEAN_IOU = 0.7735
MEDIAN_IOU = 0.8673
MEAN_PRECISION = 0.8632
MEAN_RECALL = 0.8648


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
    "Model4A_MRI_Tumor_Segmentation_Final.keras",
)


# ============================================================
# LOAD MODEL
# ============================================================

def load_model():

    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model 4A checkpoint not found:\n"
            f"{MODEL_PATH}"
        )

    model = tf.keras.models.load_model(
        MODEL_PATH,
        compile=False
    )

    print(
        "[Model 4A] Model loaded successfully."
    )

    print(
        f"[Model 4A] Architecture: {ARCHITECTURE}"
    )

    print(
        f"[Model 4A] Input: {model.input_shape}"
    )

    print(
        f"[Model 4A] Output: {model.output_shape}"
    )

    return model


# ============================================================
# GLOBAL MODEL
# ============================================================

model4 = load_model()


# ============================================================
# IMAGE PREPROCESSING
# ============================================================

def preprocess_image(image: Image.Image):

    image = image.convert("RGB")

    original_width, original_height = image.size

    resized = image.resize(
        (
            INPUT_SIZE,
            INPUT_SIZE
        ),
        Image.Resampling.BILINEAR
    )

    # IMPORTANT:
    #
    # Model 4A contains its own preprocessing layers.
    # Therefore we DO NOT apply ImageNet normalization here.
    #
    image_array = np.asarray(
        resized,
        dtype=np.float32
    )

    image_array = np.expand_dims(
        image_array,
        axis=0
    )

    return (
        image_array,
        original_width,
        original_height
    )


# ============================================================
# MASK CREATION
# ============================================================

def create_masks(prediction):

    probability_mask = prediction[
        0, :, :, 0
    ]

    binary_mask = (
        probability_mask >= MASK_THRESHOLD
    ).astype(np.uint8)

    return (
        probability_mask,
        binary_mask
    )


# ============================================================
# TUMOR AREA
# ============================================================

def calculate_area(binary_mask):

    return int(
        np.sum(binary_mask)
    )


# ============================================================
# TUMOR PERCENTAGE
# ============================================================

def calculate_tumor_percentage(
    binary_mask
):

    total_pixels = (
        binary_mask.shape[0]
        * binary_mask.shape[1]
    )

    tumor_pixels = int(
        np.sum(binary_mask)
    )

    if total_pixels == 0:
        return 0.0

    return (
        tumor_pixels
        / total_pixels
        * 100.0
    )


# ============================================================
# BOUNDING BOX
# ============================================================

def calculate_bounding_box(
    binary_mask
):

    ys, xs = np.where(
        binary_mask == 1
    )

    if len(xs) == 0:

        return None

    x_min = int(np.min(xs))
    x_max = int(np.max(xs))

    y_min = int(np.min(ys))
    y_max = int(np.max(ys))

    width = (
        x_max - x_min + 1
    )

    height = (
        y_max - y_min + 1
    )

    return {
        "x_min": x_min,
        "y_min": y_min,
        "x_max": x_max,
        "y_max": y_max,
        "width": int(width),
        "height": int(height),
    }


# ============================================================
# CENTROID
# ============================================================

def calculate_centroid(
    binary_mask
):

    ys, xs = np.where(
        binary_mask == 1
    )

    if len(xs) == 0:

        return None

    return {
        "x": round(
            float(np.mean(xs)),
            2
        ),
        "y": round(
            float(np.mean(ys)),
            2
        ),
    }


# ============================================================
# BOUNDARY EXTRACTION
# ============================================================

def calculate_boundary(
    binary_mask
):

    mask = binary_mask.astype(
        bool
    )

    if not np.any(mask):
        return np.zeros_like(
            binary_mask,
            dtype=np.uint8
        )

    # --------------------------------------------------------
    # Erosion using neighboring pixels.
    # No OpenCV dependency required.
    # --------------------------------------------------------

    padded = np.pad(
        mask,
        1,
        mode="constant",
        constant_values=False
    )

    eroded = (
        padded[1:-1, 1:-1]
        &
        padded[:-2, 1:-1]
        &
        padded[2:, 1:-1]
        &
        padded[1:-1, :-2]
        &
        padded[1:-1, 2:]
    )

    boundary = (
        mask & ~eroded
    ).astype(
        np.uint8
    )

    return boundary


# ============================================================
# CONFIDENCE
# ============================================================

def calculate_confidence(
    probability_mask,
    binary_mask
):

    tumor_probabilities = (
        probability_mask[
            binary_mask == 1
        ]
    )

    if len(tumor_probabilities) == 0:

        return {
            "mean": 0.0,
            "max": 0.0
        }

    return {
        "mean": round(
            float(
                np.mean(
                    tumor_probabilities
                )
            ) * 100,
            2
        ),
        "max": round(
            float(
                np.max(
                    tumor_probabilities
                )
            ) * 100,
            2
        )
    }


# ============================================================
# MASK → BASE64 PNG
# ============================================================

def encode_mask(
    binary_mask
):

    mask_image = (
        binary_mask * 255
    ).astype(
        np.uint8
    )

    image = Image.fromarray(
        mask_image,
        mode="L"
    )

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="PNG"
    )

    return base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")


# ============================================================
# BOUNDARY → BASE64 PNG
# ============================================================

def encode_boundary(
    boundary
):

    boundary_image = (
        boundary * 255
    ).astype(
        np.uint8
    )

    image = Image.fromarray(
        boundary_image,
        mode="L"
    )

    buffer = io.BytesIO()

    image.save(
        buffer,
        format="PNG"
    )

    return base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")


# ============================================================
# OVERLAY
# ============================================================

def create_overlay(
    original_image,
    binary_mask,
    boundary
):

    image = original_image.convert(
        "RGB"
    )

    image = image.resize(
        (
            INPUT_SIZE,
            INPUT_SIZE
        ),
        Image.Resampling.BILINEAR
    )

    image_array = np.asarray(
        image,
        dtype=np.uint8
    ).copy()

    tumor = (
        binary_mask == 1
    )

    boundary_pixels = (
        boundary == 1
    )

    # --------------------------------------------------------
    # Tumor region overlay
    # --------------------------------------------------------

    image_array[
        tumor, 0
    ] = 255

    image_array[
        tumor, 1
    ] = (
        image_array[
            tumor, 1
        ] * 0.35
    ).astype(np.uint8)

    image_array[
        tumor, 2
    ] = (
        image_array[
            tumor, 2
        ] * 0.35
    ).astype(np.uint8)

    # --------------------------------------------------------
    # Boundary
    # --------------------------------------------------------

    image_array[
        boundary_pixels
    ] = [
        255,
        255,
        255
    ]

    overlay = Image.fromarray(
        image_array
    )

    buffer = io.BytesIO()

    overlay.save(
        buffer,
        format="PNG"
    )

    return base64.b64encode(
        buffer.getvalue()
    ).decode("utf-8")


# ============================================================
# PREDICTION
# ============================================================

def predict_model4(
    image: Image.Image
):

    if image is None:
        raise ValueError(
            "No image supplied."
        )

    # --------------------------------------------------------
    # Preprocess
    # --------------------------------------------------------

    (
        input_array,
        original_width,
        original_height
    ) = preprocess_image(
        image
    )

    # --------------------------------------------------------
    # Prediction
    # --------------------------------------------------------

    prediction = model4.predict(
        input_array,
        verbose=0
    )

    # --------------------------------------------------------
    # Masks
    # --------------------------------------------------------

    (
        probability_mask,
        binary_mask
    ) = create_masks(
        prediction
    )

    # --------------------------------------------------------
    # Measurements
    # --------------------------------------------------------

    area_pixels = calculate_area(
        binary_mask
    )

    tumor_percentage = (
        calculate_tumor_percentage(
            binary_mask
        )
    )

    bounding_box = (
        calculate_bounding_box(
            binary_mask
        )
    )

    centroid = (
        calculate_centroid(
            binary_mask
        )
    )

    boundary = calculate_boundary(
        binary_mask
    )

    boundary_pixels = int(
        np.sum(boundary)
    )

    confidence = (
        calculate_confidence(
            probability_mask,
            binary_mask
        )
    )

    tumor_detected = (
        area_pixels > 0
    )

    # --------------------------------------------------------
    # Encoded visual outputs
    # --------------------------------------------------------

    mask_png = encode_mask(
        binary_mask
    )

    boundary_png = encode_boundary(
        boundary
    )

    overlay_png = create_overlay(
        image,
        binary_mask,
        boundary
    )

    # --------------------------------------------------------
    # Result
    # --------------------------------------------------------

    return {

        "tumor_detected":
            tumor_detected,

        "input_image": {
            "width": original_width,
            "height": original_height
        },

        "processed_image": {
            "width": INPUT_SIZE,
            "height": INPUT_SIZE
        },

        "measurements": {

            "area_pixels": area_pixels,

            "tumor_percentage": round(
                tumor_percentage,
                4
            ),

            "bounding_box":
                bounding_box,

            "centroid":
                centroid,

            "width_pixels": (
                bounding_box["width"]
                if bounding_box
                else 0
            ),

            "height_pixels": (
                bounding_box["height"]
                if bounding_box
                else 0
            ),

            "boundary_pixels":
                boundary_pixels,

            "mean_confidence_percent":
                confidence["mean"],

            "max_confidence_percent":
                confidence["max"],
        },

        "segmentation": {

            "threshold":
                MASK_THRESHOLD,

            "mask_size": [
                INPUT_SIZE,
                INPUT_SIZE
            ],

            "mask_png_base64":
                mask_png,

            "boundary_png_base64":
                boundary_png,

            "overlay_png_base64":
                overlay_png,
        },

        "model": {
            "name": MODEL_NAME,
            "version": MODEL_VERSION,
            "architecture": ARCHITECTURE,
        },

        "message": (
            "Tumor region segmented successfully."
            if tumor_detected
            else
            "No tumor region detected."
        ),
    }


# ============================================================
# MODEL INFORMATION
# ============================================================

def get_model4_info():

    return {

        "model":
            MODEL_NAME,

        "version":
            MODEL_VERSION,

        "architecture":
            ARCHITECTURE,

        "input_size": [
            INPUT_SIZE,
            INPUT_SIZE
        ],

        "output_shape": [
            INPUT_SIZE,
            INPUT_SIZE,
            1
        ],

        "activation":
            "sigmoid",

        "mask_threshold":
            MASK_THRESHOLD,

        "test_samples":
            TEST_SAMPLES,

        "mean_dice":
            MEAN_DICE,

        "median_dice":
            MEDIAN_DICE,

        "mean_iou":
            MEAN_IOU,

        "median_iou":
            MEDIAN_IOU,

        "mean_precision":
            MEAN_PRECISION,

        "mean_recall":
            MEAN_RECALL,

        "checkpoint":
            MODEL_PATH,
    }