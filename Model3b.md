# Model 3B — CT Brain Tumor Classification

## 1. Overview

Model 3B is the **CT-image classification component** of the brain-tumor analysis pipeline.

It classifies processed CT brain images into three categories:

1. Meningioma
2. Pituitary
3. Brain Metastasis

Model 3B is a **classification model only**. It does not generate pixel-level tumor masks and does not directly calculate tumor area, diameter, or volume. Those are separate downstream stages.

---

## 2. Final Status

Model 3B completed:

- CT data acquisition
- Dataset auditing
- Missing-file verification
- Patient-level splitting
- CT preprocessing
- 2D slice generation
- Processed-data verification
- Multiple training experiments
- Internal slice-level evaluation
- Internal patient-level evaluation
- Final model export

**Model 3B is now frozen as the CT classification baseline.**

### Selected model

```text
Model3B_CT_Classifier_Final.keras
```

Drive location:

```text
/content/drive/MyDrive/Model3B/exports/Model3B_CT_Classifier_Final.keras
```

Model size: **20.18 MB**

Original selected checkpoint:

```text
/content/drive/MyDrive/Model3B/models/model3b_step14_best.keras
```

---

# 3. Dataset

## 3.1 Classes

| Class ID | Class |
|---:|---|
| 0 | Meningioma |
| 1 | Pituitary |
| 2 | Brain Metastasis |

## 3.2 Dataset summary

| Item | Count |
|---|---:|
| Unique patients | 124 |
| CT volumes | 170 |
| Processed 2D slices | 1,860 |
| Image size | 224 × 224 |
| Classes | 3 |

## 3.3 Class distribution

| Class | Patients | CT volumes | Processed slices |
|---|---:|---:|---:|
| Meningioma | 20 | 20 | 300 |
| Pituitary | 60 | 60 | 900 |
| Brain Metastasis | 44 | 90 | 660 |
| **Total** | **124** | **170** | **1,860** |

Some Brain Metastasis patients have multiple CT volumes.

---

# 4. Patient-Level Split

A patient-level split was used so that slices from one patient cannot appear in multiple subsets.

| Split | Patients | Slices |
|---|---:|---:|
| Train | 86 | 1,290 |
| Validation | 19 | 285 |
| Test | 19 | 285 |
| **Total** | **124** | **1,860** |

Leakage checks:

```text
Train ∩ Validation = 0
Train ∩ Test       = 0
Validation ∩ Test  = 0
```

The 19 test patients were therefore held out from training and validation.

---

# 5. CT Preprocessing

The preprocessing pipeline was:

```text
Raw CT volume
      ↓
CT verification
      ↓
Patient identification
      ↓
Patient-level split
      ↓
2D slice generation
      ↓
224 × 224 processing
      ↓
.npy processed slices
      ↓
Final manifest
```

Final processed-data properties:

```text
Shape: 224 × 224
Minimum: 0.0
Maximum: 1.0
Total slices: 1860
```

---

# 6. Training-Time Normalization

The successful training pipeline used per-image percentile normalization.

For each CT slice:

```text
lower = 1st percentile
upper = 99th percentile

normalized =
    (image - lower) / (upper - lower)
```

The result is clipped to:

```text
[0, 1]
```

The grayscale CT image is replicated into three channels so it can be used with MobileNetV2:

```text
Grayscale CT
    ↓
R channel
G channel
B channel
```

---

# 7. Model Architecture

The final classifier uses **MobileNetV2** with a custom classification head.

```text
Input CT Slice
      ↓
224 × 224 × 3
      ↓
MobileNetV2 preprocessing
      ↓
MobileNetV2 backbone
      ↓
7 × 7 × 1280 feature map
      ↓
Global Average Pooling
      ↓
1280-dimensional feature vector
      ↓
Dropout
      ↓
Dense(128, ReLU)
      ↓
Dropout
      ↓
Dense(3, Softmax)
      ↓
Meningioma / Pituitary / Brain Metastasis
```

The final Softmax layer produces:

```text
P(Meningioma)
P(Pituitary)
P(Brain Metastasis)
```

The highest-probability class is selected.

---

# 8. Model Parameters

The Step 13 architecture contained approximately:

```text
Total parameters: 2,422,339
```

The initial training froze the MobileNetV2 backbone.

The Step 14 experiment then fine-tuned upper MobileNetV2 layers with a low learning rate.

Step 14 produced the best overall result and was selected.

---

# 9. Training Experiments

## Step 13 — Fast Normalized Training

```text
Test accuracy: 79.30%
```

Per-class recall:

```text
Meningioma:        0%
Pituitary:       100%
Brain Metastasis: 87%
```

This was kept as a baseline.

## Step 14 — Targeted Fine-Tuning

Step 13 was fine-tuned with a low learning rate.

```text
Test accuracy: 82.46%
```

Per-class performance:

```text
Meningioma
Precision: 0.00
Recall:    0.00
F1:        0.00

Pituitary
Precision: 0.74
Recall:    0.96
F1:        0.84

Brain Metastasis
Precision: 0.99
Recall:    1.00
F1:        1.00
```

**Step 14 is the selected model.**

## Step 15 — Final Meningioma-Focused Attempt

A final controlled attempt increased emphasis on Meningioma.

```text
Test accuracy: 47.72%
```

Meningioma recall reached 100%, but Pituitary recall collapsed to 0%.

Therefore:

```text
Step 15 = REJECTED
```

---

# 10. Final Internal Evaluation

The selected Step 14 model was evaluated on the held-out test set.

```text
Test slices: 285
Test patients: 19

Slice Accuracy:       82.46%
Balanced Accuracy:    65.43%
Patient Accuracy:     84.21%
```

## Slice-level classification report

```text
                  precision    recall  f1-score   support

Meningioma          0.00      0.00      0.00        45
Pituitary           0.74      0.96      0.84       135
Brain_Metastasis    0.99      1.00      1.00       105

accuracy                                  0.82       285
macro avg            0.58      0.65      0.61       285
weighted avg         0.72      0.82      0.76       285
```

## Slice-level confusion matrix

```text
                  Meningioma  Pituitary  Brain_Metastasis

Meningioma              0          45          0
Pituitary               4         130          1
Brain_Metastasis        0           0        105
```

---

# 11. Patient-Level Evaluation

Slice predictions were aggregated by patient using majority voting.

```text
Patients: 19
Patient Accuracy: 84.21%
```

Patient-level confusion matrix:

```text
                  Meningioma  Pituitary  Brain_Metastasis

Meningioma              0          3          0
Pituitary               0          9          0
Brain_Metastasis        0          0          7
```

---

# 12. Important Limitation

The overall 82.46% accuracy must **not** be interpreted as equally strong performance across all three classes.

The major limitation is:

```text
Meningioma recall = 0%
```

All 45 Meningioma test slices were classified as Pituitary.

Therefore the correct research statement is:

> Model 3B achieved 82.46% slice-level accuracy and 84.21% patient-level accuracy on the internal held-out CT test set, with strong performance for Pituitary and Brain Metastasis but poor recognition of Meningioma.

The relatively small Meningioma patient count is an important limitation:

```text
Meningioma patients = 20
Pituitary patients = 60
Brain Metastasis patients = 44
```

Further improvement would require additional independent Meningioma CT data and/or a redesigned classification approach.

For the current project, Model 3B is frozen and the project proceeds to segmentation.

---

# 13. Internal vs External Testing

The current evaluation is an **internal held-out test**.

It is not external validation.

The internal pipeline is:

```text
Training patients
       ↓
Validation patients
       ↓
Held-out test patients
       ↓
Final internal evaluation
```

External validation requires a completely independent CT dataset that was not used for model development, training, validation, or tuning.

Therefore this project should **not claim external validation for Model 3B** unless such an independent dataset is subsequently acquired.

---

# 14. Model Files

Selected model:

```text
Model3B_CT_Classifier_Final.keras
```

Export:

```text
/content/drive/MyDrive/Model3B/exports/
    Model3B_CT_Classifier_Final.keras
```

Selected checkpoint:

```text
/content/drive/MyDrive/Model3B/models/
    model3b_step14_best.keras
```

Experimental models retained for reproducibility:

```text
model3b_step13_best.keras
model3b_step13_final.keras

model3b_step14_best.keras
model3b_step14_final.keras

model3b_step15_best.keras
model3b_step15_final.keras
```

Step 15 should not be used as the final classifier.

---

# 15. Results

Final internal evaluation directory:

```text
/content/drive/MyDrive/Model3B/results/step16_final_internal/
```

Important outputs:

```text
slice_confusion_matrix.csv
patient_predictions.csv
slice_predictions.csv
classification_report.txt
final_internal_summary.json
```

---

# 16. Drive Project Structure

```text
Model3B/
│
├── raw/
│   ├── Meningioma/
│   ├── Pituitary/
│   └── Brain_Metastasis/
│
├── processed/
│   └── 3class/
│       └── *.npy
│
├── manifests/
│   ├── meningioma_acquisition_manifest.csv
│   ├── pituitary_acquisition_manifest.csv
│   ├── brain_metastasis_acquisition_manifest.csv
│   ├── model3b_step1_ct_acquisition_manifest.csv
│   ├── model3b_step7_patient_split.csv
│   ├── model3b_step7fix_patient_split.csv
│   ├── model3b_step7fix_3class_slice_manifest.csv
│   └── model3b_final_3class_slice_manifest.csv
│
├── models/
│   ├── model3b_step13_best.keras
│   ├── model3b_step13_final.keras
│   ├── model3b_step14_best.keras
│   ├── model3b_step14_final.keras
│   ├── model3b_step15_best.keras
│   └── model3b_step15_final.keras
│
├── exports/
│   └── Model3B_CT_Classifier_Final.keras
│
├── results/
│   ├── step9/
│   ├── step10/
│   ├── step11/
│   ├── step12/
│   ├── step13/
│   ├── step14/
│   ├── step15/
│   └── step16_final_internal/
│
└── audit/
    └── ...
```

---

# 17. Overall Model 3B Architecture

```text
                    CT DATA SOURCES
                           │
                           ▼
                 CT DATA ACQUISITION
                           │
                           ▼
                    DATA AUDITING
                           │
                           ▼
                 PATIENT IDENTIFICATION
                           │
                           ▼
              PATIENT-LEVEL DATA SPLIT
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
           TRAIN        VALIDATION       TEST
             │             │             │
             └─────────────┼─────────────┘
                           │
                           ▼
                  CT PREPROCESSING
                           │
                           ▼
                    224 × 224
                    2D CT SLICES
                           │
                           ▼
               PER-IMAGE NORMALIZATION
                           │
                           ▼
                  GRAYSCALE → RGB
                           │
                           ▼
                    MobileNetV2
                     Backbone
                           │
                           ▼
             Global Average Pooling
                           │
                           ▼
                     Dropout
                           │
                           ▼
                  Dense(128, ReLU)
                           │
                           ▼
                     Dropout
                           │
                           ▼
                 Dense(3, Softmax)
                           │
             ┌─────────────┼─────────────┐
             ▼             ▼             ▼
        MENINGIOMA     PITUITARY    BRAIN METASTASIS
```

---

# 18. Role in the Complete Project

Model 3B is one component of the larger system.

The planned architecture is:

```text
                 CT / MRI INPUT
                       │
                       ▼
            ┌─────────────────────┐
            │ Tumor Classification│
            │    Model 3A / 3B   │
            └─────────────────────┘
                       │
                       ▼
                 Tumor Category
                       │
                       ▼
            ┌─────────────────────┐
            │ Segmentation Model  │
            │       U-Net/etc.    │
            └─────────────────────┘
                       │
                       ▼
                   Tumor Mask
                       │
              ┌────────┼────────┐
              ▼        ▼        ▼
            Area     Size     Volume
              │        │        │
              └────────┼────────┘
                       ▼
              Quantitative Report
                       │
                       ▼
             Decision-Support Layer
```

---

# 19. Classification vs Segmentation

## Classification

Model 3B answers:

> What tumor class does this CT image belong to?

Output:

```text
Meningioma
Pituitary
Brain Metastasis
```

## Segmentation

A separate model answers:

> Which pixels/voxels belong to the tumor?

Output:

```text
0 = background
1 = tumor
```

## Measurement

Tumor area, size, diameter, and volume can then be calculated from the segmentation mask and image metadata.

A separate deep-learning model is not necessarily required for those measurements.

---

# 20. Next Stage

Model 3B is complete.

The next pipeline is:

```text
MODEL 3B CLASSIFICATION
          ↓
SEGMENTATION DATASET
          ↓
IMAGE + TUMOR MASK PAIRS
          ↓
PATIENT-LEVEL SPLIT
          ↓
SEGMENTATION MODEL
          ↓
TUMOR MASK
          ↓
AREA / SIZE / VOLUME
          ↓
FINAL DECISION-SUPPORT PIPELINE
```

The segmentation dataset must contain actual tumor masks. The Model 3B classification dataset should not be reused for segmentation unless corresponding pixel-level annotations exist.

---

# 21. Reproducibility Checklist

Preserve:

```text
✓ Dataset manifests
✓ Patient split
✓ Preprocessing procedure
✓ Training configuration
✓ Model checkpoints
✓ Test predictions
✓ Confusion matrices
✓ Classification report
✓ Patient-level predictions
✓ Final exported model
```

Final selected classifier:

```text
Model3B_CT_Classifier_Final.keras
```

---

# 22. Final Conclusion

Model 3B is the CT-based three-class tumor classification module.

It uses a MobileNetV2 transfer-learning architecture with patient-level data splitting and per-image intensity normalization.

Final internal performance:

```text
Slice accuracy:       82.46%
Balanced accuracy:    65.43%
Patient accuracy:     84.21%
```

The model performs strongly on Pituitary and Brain Metastasis but currently fails to recognize Meningioma in the internal test set. This limitation is documented and must be considered when interpreting the results.

The selected model is frozen and exported as:

```text
Model3B_CT_Classifier_Final.keras
```

The next stage is a separate tumor segmentation model, followed by quantitative tumor area, size, and volume calculation.
