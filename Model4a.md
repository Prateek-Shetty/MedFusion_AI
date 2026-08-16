# Model 4A — MRI Tumor Segmentation

## Overview

Model 4A is the MRI tumor segmentation component of the brain-tumor analysis system.

It takes a **2D MRI brain image** and produces a pixel-level tumor segmentation. The segmentation is then used to calculate tumor location and geometric measurements.

**Final architecture:** EfficientNet backbone + Attention U-Net style decoder.

> **Official scope:** Model 4A is trained and validated for **MRI** tumor segmentation. The CT experiments performed during development were out-of-domain experiments and are not validated CT performance.

---

## Architecture

```text
2D MRI
256 × 256 × 3
      │
      ▼
Input preprocessing
      │
      ▼
EfficientNet backbone
      │
      ▼
Feature extraction
      │
      ▼
Attention mechanisms
      │
      ▼
U-Net-style decoder
      │
      ▼
Skip connections
      │
      ▼
Segmentation head
      │
      ▼
256 × 256 × 1 probability map
      │
      ▼
Thresholding
      │
      ▼
Binary tumor mask
```

### Input

```text
Shape : 256 × 256 × 3
dtype : float32
```

Grayscale MRI images are converted to the 3-channel representation required by the model.

### Output

```text
Shape : 256 × 256 × 1
```

The output is a pixel-wise tumor probability map.

---

## What Model 4A Produces

From the predicted segmentation, the system can produce:

1. Tumor mask
2. Binary segmentation mask
3. Tumor boundary
4. Bounding box
5. Tumor centroid/location
6. Tumor area
7. Tumor width
8. Tumor height
9. Tumor percentage of image
10. Prediction confidence
11. Visualization overlay
12. CSV measurement report
13. JSON measurement report

---

# Dataset

## BRISC 2025

Model 4A was developed using the BRISC 2025 segmentation dataset.

Initial audited dataset:

```text
Total paired samples : 4793
Original train       : 3933
Original test        : 860
```

The dataset contains paired MRI images and segmentation masks.

---

# Dataset Cleaning and Safety

The dataset underwent:

- Image/mask pairing verification
- Dimension checks
- Invalid image/mask checks
- Empty-mask checks
- Duplicate detection
- Cross-split leakage checks
- Visual mask inspection
- Mask encoding analysis

Duplicate records were removed before the final training split.

Final dataset:

```text
Train       : 3318
Validation  : 586
Test        : 853
-------------------
Total       : 4757
```

The final dataset was checked for ID leakage and image/mask pairing integrity.

---

# Mask Processing

The original BRISC masks contained multiple grayscale values.

The final foreground rule was:

```text
pixel >= 246 → tumor foreground
pixel <  246 → background
```

Processed masks were converted to:

```text
Background = 0
Tumor      = 255
```

Final mask values:

```text
{0, 255}
```

---

# MRI Preprocessing

All images and masks were converted to:

```text
256 × 256
```

Final processed dataset:

```text
Images : 4757
Masks  : 4757
```

Pairing, dimensions, binary masks, and empty-mask checks passed.

---

# Internal Test Performance

The corrected internal evaluation used:

```text
Test samples : 851
```

| Metric | Result |
|---|---:|
| Mean Dice | **0.8466** |
| Median Dice | **0.9289** |
| Mean IoU | **0.7735** |
| Median IoU | **0.8673** |
| Mean Precision | **0.8632** |
| Mean Recall | **0.8648** |

Dice distribution:

```text
Dice < 0.50       : 59
Dice 0.50–0.70    : 60
Dice 0.70–0.80    : 65
Dice >= 0.80      : 667
```

The corrected evaluation is the official internal test result.

---

# Important Evaluation Note

An earlier test evaluation produced zero Dice because the inference preprocessing was inconsistent with the model's expected input pipeline.

A diagnostic check confirmed that the model itself could produce meaningful probability maps when the correct raw-input path was used.

The corrected full test evaluation produced:

```text
Mean Dice : 0.8466
Mean IoU  : 0.7735
```

---

# Tumor Measurement Pipeline

The predicted mask is converted into geometric measurements.

## Area

```text
area_pixels = number of tumor pixels
```

This is a pixel-based area measurement.

A physical area in mm² requires reliable image pixel-spacing metadata.

## Bounding Box

```text
x_min
y_min
x_max
y_max
```

Then:

```text
width  = x_max - x_min + 1
height = y_max - y_min + 1
```

## Centroid

The centroid represents the center of the predicted tumor region:

```text
centroid_x
centroid_y
```

Coordinates are in the processed 256 × 256 image coordinate system.

## Boundary

The tumor boundary is extracted from the binary segmentation mask and can be overlaid on the MRI.

## Tumor Percentage

```text
tumor_percentage =
    tumor_pixels / total_image_pixels × 100
```

This is the percentage of the processed image occupied by the predicted tumor.

---

# Example Output

A successful segmentation can produce output such as:

```text
Tumor detected : YES

Area           : 1765 pixels²
Image occupied : 2.6932%

Bounding box:
    x = 107 → 158
    y = 29  → 80

Width          : 52 pixels
Height         : 52 pixels

Centroid:
    X = 131.44
    Y = 52.90

Boundary pixels: 155

Mean confidence: 0.9939
Max confidence : 0.999979
```

---

# External MRI Test

A new MRI image outside the BRISC test set was tested.

The model generated:

- Tumor mask
- Binary segmentation
- Boundary
- Bounding box
- Centroid
- Area
- Width
- Height
- Tumor percentage
- Confidence
- Visualization
- CSV
- JSON

A small number of external images does not constitute clinical validation.

---

# CT Experiment

CT images were also tested experimentally.

The model generated segmentation outputs for the tested CT images, but this does **not** establish CT capability.

```text
Training domain : MRI
Validated domain: MRI
CT validation   : Not performed
```

Therefore Model 4A should **not** be described as a validated MRI+CT segmentation model.

A dedicated CT-trained segmentation model should be developed if reliable CT segmentation is required.

---

# Final Model

Final exported model:

```text
Model4A_MRI_Tumor_Segmentation_Final.keras
```

Google Drive:

```text
/content/drive/MyDrive/Model4A/exports/
```

Export size:

```text
41.85 MB
```

SHA-256:

```text
91df39fa7610d5f09ab99eb178e78b0718e3c90f983930a6845a79b51ce6e4cb
```

Supporting files:

```text
Model4A_Final_Metadata.json
Model4A_Final_Validation.json
```

Recommended local directory:

```text
Model4A/
├── Model4A_MRI_Tumor_Segmentation_Final.keras
├── Model4A_Final_Metadata.json
└── Model4A_Final_Validation.json
```

---

# Model 3B + Model 4A

The two models have separate responsibilities:

```text
                 Brain MRI
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
      Model 3B             Model 4A
  Classification         Segmentation
          │                   │
          ▼                   ▼
     Tumor type        Tumor localization
                         + measurements
```

Model 3B identifies the tumor class.

Model 4A identifies the tumor region and calculates its geometric measurements.

---

# Development Pipeline

```text
Step 1
BRISC acquisition
        ↓
Step 1C
Dataset audit
        ↓
Step 2
Visual mask audit
        ↓
Step 3
Duplicate + mask encoding analysis
        ↓
Step 4-FIX
Duplicate-safe dataset split
        ↓
Step 5
Mask normalization + preprocessing
        ↓
Step 6
Visual preprocessing validation
        ↓
Step 7
Dataset safety validation
        ↓
Training
        ↓
Step 9
Corrected internal test
        ↓
Step 10
Tumor measurement extraction
        ↓
Step 11
Final validation + export
```

---

# Final Status

```text
Architecture validation       ✅
Dataset acquisition           ✅
Dataset audit                 ✅
Duplicate handling            ✅
Leakage checks                ✅
Mask normalization            ✅
MRI preprocessing             ✅
Visual validation             ✅
Training                      ✅
Internal testing              ✅
External MRI testing          ✅
Tumor measurements            ✅
Bounding box                  ✅
Centroid                      ✅
Boundary                      ✅
Final export                  ✅
Metadata                      ✅
Checksum                      ✅
```

## MODEL 4A — COMPLETE

Final deliverable:

```text
Model4A_MRI_Tumor_Segmentation_Final.keras
```

---

# Limitations

Model 4A is a **research/development segmentation model**, not a clinically validated diagnostic system.

It does not independently provide:

- Tumor diagnosis
- Tumor grade
- Histopathological classification
- Prognosis
- Treatment recommendations
- Validated CT segmentation
- Physical tumor volume without appropriate imaging metadata

Predictions should not be used alone for medical diagnosis or treatment decisions.
