# Brain MRI Tumor Classification --- DenseNet169 V2

## Overview

This project contains a deep-learning model for **12-class brain MRI
image classification**.

The final V2 model uses **DenseNet169** with transfer learning and
fine-tuning. It was trained on a cleaned dataset containing **4,159
unique MRI images** and evaluated on a completely held-out test set of
**635 images**.

> **Important:** This is an experimental/research/academic model. It is
> not a clinically validated diagnostic system and must not be used as a
> substitute for a qualified medical professional.

------------------------------------------------------------------------

## Final Model

-   **Architecture:** DenseNet169
-   **Version:** V2
-   **Framework:** PyTorch
-   **Input:** RGB MRI image, resized to 224 × 224
-   **Output:** 12 classes
-   **Pretraining:** ImageNet
-   **V2 loss:** Focal Loss, gamma = 2.0
-   **Optimizer:** AdamW
-   **Fine-tuning learning rate:** 5e-6
-   **Weight decay:** 1e-4
-   **Fine-tuned layers:** DenseBlock3, DenseBlock4, Norm5, classifier

Recommended model file:

``` text
brain_mri_densenet169_12class_V2_FINAL.pth
```

## 1. Classes

    ID Class
  ---- -------------------
     0 Astrocitoma
     1 Carcinoma
     2 Ependimoma
     3 Germinoma
     4 Glioblastoma
     5 Meduloblastoma
     6 Meningioma
     7 Neurocitoma
     8 Normal
     9 Oligodendroglioma
    10 Papiloma
    11 Schwannoma

The class mapping is stored inside the final checkpoint.

## 2. Dataset

The final cleaned dataset was:

``` text
/content/MRI_12_CLASS_CLEAN
```

The original selected dataset contained 4,195 images. Duplicate checking
found 36 duplicate images, leaving:

``` text
Original images : 4195
Duplicates      : 36
Unique images   : 4159
```

Final duplicate verification:

``` text
Unique hashes          : 4159
Cross-split duplicates : 0
```

Therefore, no identical image occurs across train, validation, and test.

### Split

  Split             Images
  ------------ -----------
  Train              2,906
  Validation           618
  Test                 635
  **Total**      **4,159**

### Training distribution

  Class                    Images
  ------------------- -----------
  Astrocitoma                 399
  Carcinoma                   175
  Ependimoma                  105
  Germinoma                    70
  Glioblastoma                142
  Meduloblastoma               91
  Meningioma                  595
  Neurocitoma                 319
  Normal                      365
  Oligodendroglioma           155
  Papiloma                    165
  Schwannoma                  325
  **Total**             **2,906**

A `WeightedRandomSampler` was used to reduce the effect of class
imbalance without deleting images from larger classes.

## 3. Removed Classes

The original 44-class organization contained additional categories. The
final 12-class model excludes:

``` text
Ganglioglioma
Granuloma
Tuberculoma
```

The final model therefore focuses on the selected 12-class problem.

## 4. MRI Sequence Consolidation

The original folders included sequence-specific names such as:

``` text
T1
T1C+
T2
```

For the final classifier, sequence-specific folders were consolidated
into their corresponding class. For example:

``` text
Astrocitoma T1
Astrocitoma T1C+
Astrocitoma T2
```

became:

``` text
Astrocitoma
```

## 5. Preprocessing

Input images are converted to RGB and resized to:

``` text
224 × 224
```

Normalization:

``` text
Mean = [0.485, 0.456, 0.406]
Std  = [0.229, 0.224, 0.225]
```

Evaluation preprocessing:

``` python
eval_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])
```

## 6. V1 Baseline

The original DenseNet169 baseline achieved on the untouched 635-image
test set:

``` text
Test Accuracy          : 78.74%
Test Balanced Accuracy : 82.23%
Test Macro F1          : 78.63%
```

V1 was retained as the baseline for evaluating V2.

## 7. V2 Improvements

V2 was initialized from V1 and changed in a controlled way.

### Focal Loss

``` text
Focal Loss
gamma = 2.0
```

This gives more emphasis to difficult examples.

### Deeper fine-tuning

V2 fine-tuned:

``` text
DenseBlock3
DenseBlock4
Norm5
Classifier
```

### Conservative augmentation

Training augmentation included:

``` text
Random Horizontal Flip
Random Rotation: ±7 degrees
Small translation
Small scale variation
Mild brightness adjustment
Mild contrast adjustment
```

### Balanced sampling

The `WeightedRandomSampler` was retained.

### Fine-tuning optimizer

``` text
AdamW
Learning rate = 5e-6
Weight decay = 1e-4
```

## 8. V2 Validation Performance

Best validation result:

``` text
Validation Accuracy          : 88.03%
Validation Balanced Accuracy : 86.35%
Validation Macro F1          : 87.43%
```

Best validation Macro F1:

``` text
0.8742920282710379
```

## 9. Final V2 Test Performance

The final V2 checkpoint was evaluated on the untouched 635-image test
set.

``` text
Test Loss              : 0.2026
Test Accuracy          : 88.35%
Test Balanced Accuracy : 89.01%
Test Macro F1          : 88.88%
```

### V1 vs V2

  Metric                    V1           V2                Improvement
  ------------------- -------- ------------ --------------------------
  Test Accuracy         78.74%   **88.35%**    +9.61 percentage points
  Balanced Accuracy     82.23%   **89.01%**    +6.78 percentage points
  Macro F1              78.63%   **88.88%**   +10.25 percentage points

## 10. V2 Per-Class Test Performance

  Class                 Precision   Recall       F1   Support
  ------------------- ----------- -------- -------- ---------
  Astrocitoma              0.8690   0.8488   0.8588        86
  Carcinoma                0.9722   0.8974   0.9333        39
  Ependimoma               0.7692   0.8696   0.8163        23
  Germinoma                0.8462   0.7333   0.7857        15
  Glioblastoma             0.8333   0.9375   0.8824        32
  Meduloblastoma           0.9524   0.9524   0.9524        21
  Meningioma               0.8333   0.8203   0.8268       128
  Neurocitoma              0.9516   0.8429   0.8939        70
  Normal                   0.8750   0.9747   0.9222        79
  Oligodendroglioma        1.0000   0.9706   0.9851        34
  Papiloma                 0.8974   0.9459   0.9211        37
  Schwannoma               0.8873   0.8873   0.8873        71

Overall:

``` text
Accuracy        : 0.8835
Macro Precision : 0.8906
Macro Recall    : 0.8901
Macro F1        : 0.8888
Weighted F1     : 0.8833
```

## 11. Model Architecture

Conceptually:

``` text
Input MRI
   |
   v
224 x 224 x 3
   |
   v
DenseNet169
   |
   +-- DenseBlock 1
   +-- DenseBlock 2
   +-- DenseBlock 3  <-- V2 fine-tuned
   +-- DenseBlock 4  <-- V2 fine-tuned
   +-- Norm5         <-- V2 fine-tuned
   |
   v
Classifier
   |
   v
12 logits
   |
   v
Softmax
   |
   v
Predicted class
```

## 12. Loading the Final Model

Example:

``` python
import torch
from torchvision import models
import torch.nn as nn

checkpoint = torch.load(
    "brain_mri_densenet169_12class_V2_FINAL.pth",
    map_location="cpu",
    weights_only=False
)

model = models.densenet169(weights=None)

in_features = model.classifier.in_features

model.classifier = nn.Sequential(
    nn.Dropout(0.4),
    nn.Linear(in_features, 12)
)

model.load_state_dict(
    checkpoint["model_state_dict"]
)

model.eval()

class_names = checkpoint["class_names"]
```

For PyTorch 2.6+, `weights_only=False` may be required for this
checkpoint because it contains metadata in addition to tensors. Only use
this for a checkpoint you trust.

## 13. External Inference

``` python
from PIL import Image

image = Image.open(
    "your_mri_image.jpg"
).convert("RGB")

image_tensor = eval_transform(image)
image_tensor = image_tensor.unsqueeze(0)

with torch.no_grad():
    output = model(image_tensor)

probabilities = torch.softmax(output, dim=1)

predicted_index = probabilities.argmax(
    dim=1
).item()

predicted_class = class_names[predicted_index]

confidence = probabilities[
    0,
    predicted_index
].item()

print("Prediction:", predicted_class)
print("Confidence:", f"{confidence * 100:.2f}%")
```

The model can also return the top-5 predicted classes and their softmax
scores.

## 14. Confidence Warning

A softmax confidence is a **model confidence score**, not a medical
probability.

For example:

``` text
Glioblastoma — 97%
```

does not mean that a patient has glioblastoma with 97% medical
certainty.

Performance may change on images from:

-   another hospital
-   another scanner
-   another MRI protocol
-   another MRI sequence
-   another resolution
-   another preprocessing pipeline
-   a different patient population

External validation is required before making real-world clinical
claims.

## 15. Segmentation

This model performs **classification only**.

It does not produce:

``` text
tumor mask
tumor boundary
tumor area
tumor volume
```

A separate segmentation model can be used for localization.

The intended architecture can therefore be:

``` text
MRI IMAGE
    |
    v
Preprocessing
    |
    v
DenseNet169 V2
    |
    v
Tumor / Normal Classification
    |
    +----------------------+
                           |
                           v
                 Separate Segmentation
                       Model
                           |
                           v
                  Tumor Localization
```

## 16. Limitations

The reported 88.35% test accuracy comes from a held-out test set drawn
from the same overall dataset used to construct the project dataset.

It does not establish performance on an independent hospital or external
dataset.

Important limitations include:

-   limited sample counts for some classes
-   possible dataset-specific visual patterns
-   domain shift between MRI scanners and protocols
-   relatively small test support for some classes
-   no clinical validation
-   no prospective evaluation

Therefore, this model should be treated as an **academic/research
classifier**, not a clinically validated diagnostic system.

## 17. Future Improvements

Potential future experiments:

### Data quality

-   investigate mislabeled images
-   inspect ambiguous samples
-   inspect image artifacts
-   evaluate near-duplicates
-   perform external validation

### Architecture comparison

Possible future models:

``` text
EfficientNet
EfficientNet-B3
ConvNeXt
DenseNet201
```

DenseNet169 V2 should remain the baseline for fair comparison.

### External validation

A completely independent dataset is one of the most useful next steps
because it tests whether the model generalizes beyond the original
dataset distribution.

## 18. Reproducibility Rules

For future model versions:

1.  Keep the same test set when comparing versions.
2.  Never train on the test set.
3.  Never use test performance to select hyperparameters.
4.  Keep the class mapping unchanged.
5.  Keep preprocessing documented.
6.  Record training settings.
7.  Save each model version separately.
8.  Report accuracy, balanced accuracy, and Macro F1.
9.  Report per-class precision, recall, and F1.
10. Inspect the confusion matrix.

## 19. Final Model Summary

``` text
============================================================
BRAIN MRI 12-CLASS CLASSIFICATION — V2
============================================================

Architecture:
DenseNet169

Unique images:
4,159

Train:
2,906

Validation:
618

Test:
635

Classes:
12

Test Accuracy:
88.35%

Test Balanced Accuracy:
89.01%

Test Macro F1:
88.88%

============================================================
```

Recommended final checkpoint:

``` text
brain_mri_densenet169_12class_V2_FINAL.pth
```

V1 baseline should be retained separately:

``` text
brain_mri_densenet169_12class_final.pth
```

## 20. Suggested Project Structure

``` text
brain_mri_classifier/
│
├── models/
│   ├── brain_mri_densenet169_12class_final.pth
│   └── brain_mri_densenet169_12class_V2_FINAL.pth
│
├── inference/
│   └── predict.py
│
├── training/
│   └── train_v2.py
│
├── README.md
│
└── requirements.txt
```

## Requirements

Typical packages used:

``` text
torch
torchvision
numpy
pandas
scikit-learn
matplotlib
seaborn
Pillow
```
