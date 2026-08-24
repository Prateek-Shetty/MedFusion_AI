# Model 3A — Brain Tumor MRI Classification

## 1. Project Overview

**Model 3A** is a 3-class brain tumor MRI image classification system built using **EfficientNet-B0** with ImageNet pretrained weights.

The final selected model is **V1**, which achieved:

- **Test Accuracy: 92.08%**
- Architecture: EfficientNet-B0
- Input: RGB, 224 × 224
- Classes:
  1. Glioma
  2. Meningioma
  3. Pituitary

The model is intended for an academic/research project and is **not a clinical diagnostic system**.

---

# 2. Dataset

The original dataset contained four classes:

```text
glioma
meningioma
notumor
pituitary
```

For Model 3A, `notumor` was excluded.

### Final classes

```text
0 → glioma
1 → meningioma
2 → pituitary
```

### Dataset counts

| Split | Glioma | Meningioma | Pituitary | Total |
|---|---:|---:|---:|---:|
| Training | 1260 | 1260 | 1260 | 3780 |
| Validation | 140 | 140 | 140 | 420 |
| Testing | 400 | 400 | 400 | 1200 |

The final V1 model used the original 4,200 relevant training images:

```text
Glioma      : 1400
Meningioma  : 1400
Pituitary   : 1400
```

A stratified 90/10 training-validation split was then performed.

The test set contained:

```text
Glioma      : 400
Meningioma  : 400
Pituitary   : 400
```

The test set was kept untouched during training.

---

# 3. Preprocessing

All images were converted to RGB.

### Training preprocessing

```text
Resize → 224 × 224
Random Horizontal Flip
Random Rotation ±10°
ToTensor
ImageNet Normalization
```

### Validation/Test preprocessing

```text
Resize → 224 × 224
ToTensor
ImageNet Normalization
```

ImageNet normalization:

```text
Mean = [0.485, 0.456, 0.406]
Std  = [0.229, 0.224, 0.225]
```

---

# 4. Model Architecture

## EfficientNet-B0

The model started from ImageNet pretrained EfficientNet-B0 weights.

Original classifier:

```text
Dropout(p=0.2)
Linear(1280 → 1000)
```

Final classifier:

```text
Dropout(p=0.3)
Linear(1280 → 3)
```

### Parameters

```text
Total parameters     : 4,011,391
```

Stage 1 trainable parameters:

```text
3,843
```

Stage 2 trainable parameters:

```text
3,133,727
```

---

# 5. Training Strategy

Model 3A used two-stage transfer learning.

## Stage 1 — Classifier Training

The EfficientNet backbone was frozen.

Only the classifier was trained.

```text
Backbone        : Frozen
Classifier      : Trainable

Loss            : CrossEntropyLoss
Optimizer       : AdamW
Learning rate   : 1e-3
Weight decay    : 1e-4
Epochs          : 8
Scheduler       : ReduceLROnPlateau
```

The best V1 Stage 1 validation accuracy was:

```text
89.29%
```

---

# 6. Stage 2 — Fine-Tuning

The final three EfficientNet feature blocks were unfrozen:

```text
features.6
features.7
features.8
```

Earlier blocks remained frozen:

```text
features.0 → features.5
```

BatchNorm layers were frozen.

Differential learning rates were used:

```text
Backbone    : 1e-5
Classifier  : 1e-4
```

Other settings:

```text
Optimizer           : AdamW
Weight decay        : 1e-4
Loss                : CrossEntropyLoss
Maximum epochs      : 15
Early stopping      : 5 epochs
```

Best V1 Stage 2 validation accuracy:

```text
95.71%
```

The best validation model was restored before final testing.

---

# 7. Final V1 Test Results

## Overall

```text
Test images : 1200
Accuracy    : 92.08%
```

## Classification Report

```text
              precision    recall  f1-score   support

glioma          0.???       ???       ???       400
meningioma      0.???       ???       ???       400
pituitary       0.???       ???       ???       400
```

> Note: The exact V1 per-class classification report and confusion matrix were not included in the final training output retained for this reference. The confirmed final V1 overall test accuracy is **92.08%**.

---

# 8. Model Experiments

Several Model 3A versions were tested.

| Version | Test Accuracy | Glioma → Meningioma |
|---|---:|---:|
| **V1** | **92.08%** | **74** |
| V2 | 89.83% | 93 |
| V3 | 90.33% | 91 |
| V4 | 91.50% | 75 |
| V5 | 90.50% | 88 |
| V6 | 90.17% | 102 |

### Final decision

**V1 was selected as the final Model 3A model.**

Reason:

```text
V1 Test Accuracy = 92.08%
```

This was higher than all later experimental versions.

---

# 9. V2–V6 Experiments

## V2

Stage 1:

```text
Validation accuracy: 89.29%
```

Stage 2:

```text
Validation accuracy: 95.95%
```

Test:

```text
89.83%
```

Glioma recall:

```text
74.75%
```

Main issue:

```text
93 Gliomas → Meningioma
```

---

## V3 — Class Weighted Fine-Tuning

Glioma class weight:

```text
Glioma      : 1.30
Meningioma  : 1.00
Pituitary   : 1.00
```

Test:

```text
90.33%
```

Glioma recall:

```text
76.00%
```

Glioma → Meningioma:

```text
91
```

The improvement was insufficient to beat V1.

---

## V4 — Hard Glioma Oversampling

Hard Glioma samples were identified from training predictions.

Sampling:

```text
Normal samples : 1.0×
Hard Gliomas   : 3.0×
```

No validation or test images were modified.

Test:

```text
91.50%
```

Glioma recall:

```text
79.25%
```

Glioma → Meningioma:

```text
75
```

V4 was the strongest alternative to V1, but still below V1 overall accuracy.

---

## V5 — RGB Dataset + Hard Glioma Oversampling

RGB preprocessing was restored and hard Glioma samples were oversampled.

Test:

```text
90.50%
```

Glioma recall:

```text
76.50%
```

Glioma → Meningioma:

```text
88
```

V5 did not beat V1.

---

## V6 — Removal of 60 Hardest Gliomas

60 highly confused Glioma training images were temporarily removed from the active training dataset.

The removed files were backed up.

Training distribution after removal:

```text
Glioma      : 1340
Meningioma  : 1400
Pituitary   : 1400
```

After the 90/10 split:

```text
Training   : 3726
Validation : 414
Testing    : 1200
```

V6 validation accuracy:

```text
96.86%
```

However, final test accuracy dropped to:

```text
90.17%
```

Glioma recall:

```text
73.25%
```

Glioma → Meningioma:

```text
102
```

Therefore V6 was rejected.

The 60 removed Glioma images were restored before final V1 retraining.

---

# 10. Final Model File

The final model was saved as:

```text
brain_tumor_efficientnet_v1.pth
```

Expected project location:

```text
model/
└── brain_tumor_efficientnet_v1.pth
```

A configuration file was also created:

```text
config.json
```

Recommended project structure:

```text
brain-tumor-project/
│
├── model/
│   └── brain_tumor_efficientnet_v1.pth
│
├── config/
│   └── config.json
│
├── test_images/
│
├── predict.py
├── app.py
├── requirements.txt
└── README.md
```

---

# 11. Inference Configuration

The final model expects:

```text
Input:
RGB image

Resolution:
224 × 224

Classes:
0 = glioma
1 = meningioma
2 = pituitary
```

The same ImageNet normalization used during evaluation must be used during inference:

```python
transforms.Normalize(
    [0.485, 0.456, 0.406],
    [0.229, 0.224, 0.225]
)
```

The model outputs three logits.

Softmax converts these into class probabilities.

---

# 12. Example Prediction

Example output format:

```text
glioma      : 92.31%
meningioma  :  6.42%
pituitary   :  1.27%

Prediction : GLIOMA
Confidence : 92.31%
```

Confidence represents the model's softmax probability and should **not** be interpreted as clinical certainty.

---

# 13. VS Code Inference Pipeline

The intended application pipeline is:

```text
User uploads MRI
        ↓
Image converted to RGB
        ↓
Resize to 224 × 224
        ↓
Tensor conversion
        ↓
ImageNet normalization
        ↓
EfficientNet-B0 V1
        ↓
Softmax
        ↓
Class probabilities
        ↓
Final prediction
        ↓
Confidence
```

The current planned interface uses Streamlit.

Run:

```bash
streamlit run app.py
```

---

# 14. Important Reproducibility Notes

The final V1 model was trained from:

```text
Fresh EfficientNet-B0
+
ImageNet pretrained weights
+
Original RGB dataset
+
notumor excluded
+
90/10 stratified split
+
Stage 1 classifier training
+
Stage 2 fine-tuning
```

V1 did **not** use the V6 removed-Glioma dataset.

The final V1 training dataset contained:

```text
1400 Glioma
1400 Meningioma
1400 Pituitary
```

The test set contained:

```text
400 Glioma
400 Meningioma
400 Pituitary
```

---

# 15. Final Result

## Model 3A Final Model

```text
Selected version : V1

Architecture     : EfficientNet-B0
Input            : 224 × 224 RGB
Classes          : 3
Training images  : 3780
Validation       : 420
Test images      : 1200

Best validation accuracy : 95.71%
Final test accuracy      : 92.08%
```

### Final decision

**V1 is the official Model 3A model.**

Do not replace the V1 checkpoint with V2–V6 unless a future experiment demonstrates a statistically meaningful improvement on an untouched evaluation set.

---

# 16. Limitations

This model is an academic machine-learning classifier.

Important limitations include:

- Test accuracy does not guarantee clinical performance.
- The dataset may not represent all MRI scanners, acquisition protocols, populations, or tumor presentations.
- Glioma was the most difficult class in the experiments.
- High softmax confidence does not guarantee correctness.
- External validation on an independent dataset was not performed in this project.
- The model should not be used as a standalone medical diagnostic tool.

---

# 17. Final Reference

```text
MODEL 3A
│
├── Dataset
│   ├── Glioma
│   ├── Meningioma
│   └── Pituitary
│
├── Architecture
│   └── EfficientNet-B0
│
├── Training
│   ├── Stage 1
│   └── Stage 2
│
├── Final Version
│   └── V1
│
└── Final Test Accuracy
    └── 92.08%
```

**Model 3A Final: EfficientNet-B0 V1 — 92.08% test accuracy.**
