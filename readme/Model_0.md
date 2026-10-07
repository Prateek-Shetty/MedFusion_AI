# BrainAI Model 0 — Brain MRI/CT Gatekeeper

## Overview
BrainAI Model 0 is a two-stage deep-learning gatekeeper for 2D images.

**Final output**
- `1` = Brain MRI or Brain CT → ACCEPT
- `0` = Everything else → REJECT

## Architecture

```text
INPUT 2D IMAGE
      |
      v
Stage 1: MRI/CT vs OTHER
      |
      +-- OTHER ------> 0 REJECT
      |
      +-- MRI/CT -----> Stage 2: BRAIN vs NOT BRAIN
                            |
                            +-- NOT BRAIN --> 0 REJECT
                            |
                            +-- BRAIN -----> 1 ACCEPT
```

## Models

Both stages use:
- MobileNetV2, ImageNet pretrained
- `include_top=False`
- Input: `224 x 224 x 3`
- GlobalAveragePooling2D
- Dropout: `0.30`
- Dense(1, sigmoid)
- Binary cross-entropy
- Adam, learning rate `0.001`
- Frozen MobileNetV2 backbone during initial training
- Total parameters: `2,259,265`
- Trainable parameters: `1,281`

## Datasets

### Brain MRI — BRISC 2025
- 6,000 images
- Glioma, meningioma, no tumor, pituitary

### Brain CT — Head CT Hemorrhage
- 200 images
- 100 hemorrhage
- 100 non-hemorrhage

### Kidney CT — Axial CT Imaging Dataset
- 3,364 original images
- Used as NOT-BRAIN examples
- Augmented dataset was not used

### CIFAR-100
- 2,000 images
- Used as non-medical/OTHER examples for Stage 1

## Stage 1 Dataset
Task: `MRI/CT vs OTHER`

Total: **11,564**
- MRI: 6,000
- Brain CT: 200
- Kidney CT: 3,364
- CIFAR-100: 2,000

Split:
- Train: 9,251
- Validation: 1,156
- Test: 1,157

### Stage 1 Test Results
- Accuracy: **99.91%**
- AUC: **1.0000**
- Precision: **100.00%**
- Recall: **99.84%**
- Loss: **0.0066**

Source-wise:
- Brain CT: 23 samples, **95.65% accuracy**
- Brain MRI: 597 samples, **100.00% accuracy**
- OTHER: 537 samples, **100.00% accuracy**

## Stage 2 Dataset
Task: `BRAIN vs NOT BRAIN`

Total: **9,564**
- Brain MRI: 6,000
- Brain CT: 200
- Kidney CT: 3,364

Split:
- Train: 7,651
- Validation: 956
- Test: 957

### Stage 2 Test Results
- Accuracy: **99.79%**
- AUC: **1.0000**
- Precision: **99.84%**
- Recall: **99.84%**
- Loss: **0.0156**

Source-wise:
- Brain CT: 24 samples, **95.83% accuracy**
- Brain MRI: 596 samples, **100.00% accuracy**
- Kidney CT: 337 samples, **99.70% accuracy**

## Training and Checkpointing
Training used:
- TensorFlow/Keras 2.21.0
- NVIDIA T4 GPU
- Complete `.keras` checkpoint after every epoch
- Best complete `.keras` model
- ReduceLROnPlateau
- EarlyStopping
- Training histories saved to Drive

Stage 1 best model:
`models/stage1/stage1_best.keras`

Stage 2 best model:
`models/stage2/stage2_best.keras`

## Final Pipeline Files

Google Drive location:

```text
/content/drive/MyDrive/BrainAI/model0_final/models/model0_pipeline/
```

Files:

```text
model0_pipeline/
├── stage1.keras
├── stage2.keras
└── config.json
```

- `stage1.keras` = MRI/CT vs OTHER
- `stage2.keras` = BRAIN vs NOT BRAIN
- `config.json` = model settings, thresholds, preprocessing, and output definitions

The inference code uses:

```python
model0_predict(image_path)
```

with a `0.5` threshold for each stage.

## Expected Behavior

| Input | Expected output |
|---|---:|
| Brain MRI | 1 |
| Brain CT | 1 |
| Kidney CT | 0 |
| Aadhaar/document | 0 |
| Normal photograph | 0 |
| Other non-medical image | 0 |

## Important Limitations

This is a **student/research prototype gatekeeper**, not a clinically validated medical diagnostic system.

A verified knee-MRI dataset was not incorporated into the final training set. Therefore, do not claim that rejection of every knee MRI, PET, ultrasound, chest X-ray, or other modality has been comprehensively validated.

The train/validation/test splits were image-level rather than patient/study-level. For production medical ML, patient-level or study-level splitting and external validation are recommended.

The very high reported accuracy should therefore be interpreted in the context of these datasets and splits.

## Medical Safety

Model 0 does **not** diagnose tumors, hemorrhage, disease severity, treatment, or prognosis. It only gates whether an image is likely to be a brain MRI/CT image.

It should not replace a radiologist, physician, or clinical diagnostic system.

## Final Performance

| Component | Task | Accuracy | AUC | Precision | Recall |
|---|---|---:|---:|---:|---:|
| Stage 1 | MRI/CT vs OTHER | **99.91%** | **1.0000** | **100.00%** | **99.84%** |
| Stage 2 | BRAIN vs NOT BRAIN | **99.79%** | **1.0000** | **99.84%** | **99.84%** |

## Project Status

- [x] Dataset preparation
- [x] Stage 1 training
- [x] Stage 1 test evaluation
- [x] Stage 1 source-wise evaluation
- [x] Stage 2 training
- [x] Stage 2 test evaluation
- [x] Stage 2 source-wise evaluation
- [x] Complete `.keras` checkpoints
- [x] Final two-stage pipeline
- [x] Configuration file
- [x] Inference function
- [x] Real-image end-to-end testing

## One-Line Project Description

> BrainAI Model 0 is a two-stage MobileNetV2-based image gatekeeper that accepts brain MRI/CT images and rejects images that are non-MRI/CT or non-brain images.

**Version:** Model 0 v1.0  
**Status:** Trained and end-to-end tested  
**Output:** `1 = Brain MRI/CT`, `0 = Reject`
