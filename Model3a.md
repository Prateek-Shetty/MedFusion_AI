# Model 3A --- 8-Class Brain Tumor MRI Classification

## 1. Project Overview

Model 3A is an 8-class brain tumor image classification system based on
the EfficientNetB0 convolutional neural network architecture.

The model is designed to classify brain MRI images into the following
eight classes:

    Class ID Class Name
  ---------- ------------------
           0 No_Tumor
           1 Glioma
           2 Meningioma
           3 Pituitary
           4 Brain_Metastasis
           5 Schwannoma
           6 Meduloblastoma
           7 Ependymoma

The final trained model is:

`Model3A_EfficientNetB0_BrainTumor_8Class_Final.keras`

The model accepts a 224 × 224 RGB image and produces an 8-class softmax
probability vector.

This model was developed as a research/project prototype for multi-class
brain tumor MRI classification. It is not a clinical diagnostic system
and must not be used as a substitute for a qualified medical
professional.

------------------------------------------------------------------------

## 2. Objective

The objective of Model 3A is to build a single deep-learning model
capable of distinguishing between:

-   Normal/no-tumor brain images
-   Common primary brain tumor categories
-   Brain metastasis
-   Schwannoma
-   Medulloblastoma
-   Ependymoma

A major objective of the dataset construction was to avoid data leakage
while combining multiple MRI sources with substantially different class
sizes.

The final workflow therefore used:

1.  Source dataset identification
2.  Brain metastasis MRI and segmentation verification
3.  Segmentation-based tumor-positive slice selection
4.  Image extraction and tumor-region cropping
5.  Duplicate and quality control
6.  Patient-level splitting for brain metastasis
7.  Stratified splitting for the other classes
8.  Exact-image hash leakage checks
9.  Controlled training balancing
10. TensorFlow input pipeline creation
11. EfficientNetB0 model construction
12. Controlled training
13. Frozen-backbone training
14. Fine-tuning
15. Validation evaluation
16. Internal held-out test evaluation
17. Small independent external MRI evaluation
18. Final model freezing and packaging

------------------------------------------------------------------------

## 3. Final Model Architecture

### Backbone

The model uses:

**EfficientNetB0**

EfficientNetB0 was selected as the convolutional backbone because it
provides a strong image classification architecture while remaining
relatively compact compared with many larger CNN architectures.

The initial model used an ImageNet-pretrained EfficientNetB0 backbone.

The initial training strategy was:

-   EfficientNetB0 backbone
-   ImageNet pretrained weights
-   Backbone frozen initially
-   Trainable classification head
-   8-class softmax output

The model was subsequently fine-tuned in the later training stage. The
final checkpoint used for Model 3A is the Step 23 best fine-tuned
checkpoint.

The exact Step 23 layer-unfreezing configuration and fine-tuning
hyperparameters are not included in the surviving execution logs, so
they are intentionally not invented in this README.

### Input

``` text
Input shape: 224 × 224 × 3
Color format: RGB
Data type: float32 during TensorFlow input processing
```

### Output

``` text
Output shape: 8
Activation: Softmax
```

The eight output positions correspond exactly to:

``` text
0 → No_Tumor
1 → Glioma
2 → Meningioma
3 → Pituitary
4 → Brain_Metastasis
5 → Schwannoma
6 → Meduloblastoma
7 → Ependymoma
```

The output probabilities sum to approximately 1.0.

### Final Model File

``` text
Model3A_EfficientNetB0_BrainTumor_8Class_Final.keras
```

------------------------------------------------------------------------

## 4. Dataset Sources

Model 3A combines several MRI sources to construct the eight target
classes.

### 4-Class Brain Tumor Dataset

The first four classes were obtained from the 4-class brain tumor MRI
dataset:

``` text
No_Tumor
Glioma
Meningioma
Pituitary
```

The original source contained approximately:

``` text
No_Tumor   : 1800
Glioma     : 1800
Meningioma : 1800
Pituitary  : 1800
```

These images were cleaned before the final split.

### 44-Class Brain Tumor MRI Dataset

The 44-class MRI dataset was used to obtain the additional target tumor
classes:

``` text
Schwannoma
Meduloblastoma
Ependymoma
```

The source used the spelling:

``` text
Ependimoma
```

for Ependymoma.

Relevant source counts before cleaning were:

``` text
Schwannoma:
T1    : 148
T1C+  : 194
T2    : 123
Total : 465

Meduloblastoma:
T1    : 23
T1C+  : 67
T2    : 41
Total : 131

Ependimoma:
T1    : 45
T1C+  : 48
T2    : 57
Total : 150
```

### Brain Metastasis Dataset

Brain metastasis images were obtained from the
Pretreat-MetsToBrain-Masks dataset.

The source contained:

``` text
200 patients
MRI volumes
Segmentation masks
T1 post-gadolinium / T1C
T1 native
T2-FLAIR
T2-weighted
```

The dataset contained 1000 NIfTI files representing 200 patients.

All 200 patients had valid MRI/mask pairing.

------------------------------------------------------------------------

## 5. Brain Metastasis MRI and Segmentation Processing

Brain metastasis required a separate preprocessing pipeline because the
source provided volumetric MRI data and segmentation masks rather than
ready-to-use 2D classification images.

### Patient and Modality Verification

The pairing verification identified:

``` text
NIfTI files: 1000
Patients: 200
Valid patients: 200
Invalid patients: 0
Unrecognized files: 0
```

Required modalities were:

``` text
seg
t1c
t1n
t2f
t2w
```

### Segmentation Verification

Representative MRI volumes had dimensions such as:

``` text
240 × 240 × 155
```

The segmentation masks contained labels:

``` text
0
1
2
3
```

where zero represented background and non-zero labels represented tumor
segmentation regions.

Across the 200 patients:

``` text
Patients with non-empty segmentation: 200
Patients with empty segmentation: 0
```

Therefore all 200 patients had usable segmentation masks.

### Tumor-Positive Slice Selection

Tumor-positive axial slices were identified using segmentation labels:

``` text
Tumor labels: 1, 2, 3
Minimum tumor voxels per slice: 20
```

Results:

``` text
Patients: 200
Patients with selected slices: 195
Patients without selected slices: 5
Total selected slices: 9822
```

The five patients without selected slices were excluded from the
extracted classification image set because they did not satisfy the
selected tumor-positive slice criterion.

### Segmentation-Based Extraction

The T1C/T1 post-gadolinium volume was used for the extracted brain
metastasis classification slices.

The extraction process was memory-safe and processed one patient at a
time.

Final extraction results:

``` text
Input slices : 9822
Processed    : 9822
Failures     : 0
Patients     : 195
```

Extracted images:

``` text
9822
```

Extracted masks:

``` text
9822
```

Image and mask verification:

``` text
Missing images: 0
Missing masks : 0
```

Images and masks were resized to:

``` text
224 × 224
```

Mask values observed:

``` text
0
255
```

The extracted segmentation masks were verified to be non-empty in the
inspected sample.

------------------------------------------------------------------------

## 6. Data Cleaning

Before final splitting, the combined dataset underwent cleaning and
duplicate control.

The cleaned class counts were:

``` text
No_Tumor          : 1681
Glioma            : 1786
Meningioma        : 1784
Pituitary         : 1762
Brain_Metastasis  : 9822
Schwannoma        : 465
Meduloblastoma    : 131
Ependymoma        : 150
```

Total clean images:

``` text
17581
```

The cleaning stage reduced the original counts where duplicate or
unsuitable images were identified.

------------------------------------------------------------------------

## 7. Leakage-Safe Dataset Splitting

A major design requirement of Model 3A was preventing information
leakage between training, validation, and test sets.

### Brain Metastasis

Brain metastasis was split at the patient level.

``` text
Total patients: 195

Training patients   : 136
Validation patients : 29
Test patients       : 30
```

This means slices belonging to the same brain metastasis patient were
not allowed to appear in multiple splits.

### Other Classes

The other seven classes were split using deterministic stratified
splitting.

The resulting split counts were:

  Class                Train   Validation   Test
  ------------------ ------- ------------ ------
  No_Tumor              1176          252    253
  Glioma                1250          268    268
  Meningioma            1248          268    268
  Pituitary             1233          264    265
  Brain_Metastasis      6796         1554   1472
  Schwannoma             325           70     70
  Meduloblastoma          91           20     20
  Ependymoma             105           22     23

### Leakage Checks

Patient-level leakage check:

``` text
Train ∩ Validation: 0
Train ∩ Test:       0
Validation ∩ Test:  0
```

Exact-image SHA-256 hash leakage check:

``` text
Hashes appearing in multiple splits: 0
```

Therefore no exact-image split leakage was detected.

------------------------------------------------------------------------

## 8. Training Balancing

The natural training distribution was highly imbalanced.

Before balancing:

``` text
Brain_Metastasis : 6796
Glioma           : 1250
Meningioma       : 1248
Pituitary        : 1233
No_Tumor         : 1176
Schwannoma       : 325
Meduloblastoma   : 91
Ependymoma       : 105
```

A controlled target of:

``` text
1200 training samples per class
```

was selected.

### Balancing Strategy

Large classes were downsampled.

Small classes were oversampled at the manifest level.

``` text
No_Tumor          : 1176 → 1200
Glioma            : 1250 → 1200
Meningioma        : 1248 → 1200
Pituitary         : 1233 → 1200
Brain_Metastasis  : 6796 → 1200
Schwannoma        : 325  → 1200
Meduloblastoma    : 91   → 1200
Ependymoma        : 105  → 1200
```

Final training distribution:

``` text
8 classes × 1200 samples = 9600 training manifest rows
```

Important:

The balancing did not physically duplicate image files. Rare classes
were oversampled through manifest entries.

The balanced training manifest contained:

``` text
Training rows          : 9600
Unique physical images : 6063
Repeated manifest rows : 3537
```

Validation and test datasets were deliberately left untouched.

------------------------------------------------------------------------

## 9. TensorFlow Input Pipeline

The final input pipeline was designed to avoid loading the complete
image dataset into RAM.

### Training

The training pipeline used:

``` text
Balanced manifest
↓
Image loading
↓
Resize to 224 × 224
↓
Training augmentation
↓
Shuffle
↓
Batch
↓
Prefetch
↓
Model
```

### Validation

``` text
Validation manifest
↓
Image loading
↓
Resize to 224 × 224
↓
Batch
↓
Prefetch
↓
Model
```

### Test

``` text
Test manifest
↓
Image loading
↓
Resize to 224 × 224
↓
Batch
↓
Prefetch
↓
Model
```

Batch size used in the pipeline:

``` text
32
```

The pipeline was verified with:

``` text
Images: (32, 224, 224, 3)
Labels: (32,)
```

No complete dataset was loaded into RAM.

------------------------------------------------------------------------

## 10. Image Preprocessing

The classification input size is:

``` text
224 × 224
```

Images are converted to:

``` text
RGB
```

and supplied to TensorFlow as:

``` text
float32
```

The verified raw image range in the pipeline was:

``` text
min: 0
max: 255
```

The model therefore expects ordinary RGB image input resized to 224 ×
224.

The final external-test implementation also used:

``` text
PIL RGB conversion
224 × 224 resize
float32 conversion
batch dimension
```

No CT images were used in the final external MRI evaluation.

------------------------------------------------------------------------

## 11. Model Sanity Checks

Before full training, Model 3A underwent architecture and trainability
checks.

### Architecture Check

``` text
Input:
(None, 224, 224, 3)

Output:
(None, 8)
```

### Initial Model Parameters

The initial EfficientNetB0 model had approximately:

``` text
Total parameters       : 4,059,819
Trainable parameters   : ~10,248
Non-trainable          : ~4,049,591
```

The ImageNet backbone was initially frozen.

### Gradient Check

A training sanity test verified:

``` text
Trainable variables: 2
Variables with gradients: 2
```

Therefore gradient flow was working.

An optimizer update test also confirmed that trainable variables changed
after an optimization step.

------------------------------------------------------------------------

## 12. Controlled Training Test

Before committing to longer training, a 3-epoch controlled training
experiment was performed.

Results:

  --------------------------------------------------------------------------
           Epoch Train Accuracy     Validation     Train Loss     Validation
                                      Accuracy                          Loss
  -------------- -------------- -------------- -------------- --------------
               1         70.32%         90.36%         0.8813         0.3040

               2         83.70%         89.85%         0.5233         0.2866

               3         86.41%         92.38%         0.4413         0.2354
  --------------------------------------------------------------------------

Best validation accuracy:

``` text
92.38%
```

This confirmed that the pipeline and model could learn the eight-class
problem.

------------------------------------------------------------------------

## 13. Frozen-Backbone Training

A proper frozen-backbone training stage was then performed.

Configuration recorded during this stage:

``` text
Backbone      : EfficientNetB0
Backbone      : Frozen
Optimizer     : Adam
Learning rate : 0.001
Maximum epochs: 15
Early stopping patience: 4
```

The test set was not used during this stage.

Training stopped early after seven epochs.

Results:

    Epoch   Train Accuracy   Validation Accuracy
  ------- ---------------- ---------------------
        1           87.74%                92.27%
        2           88.92%                91.91%
        3           89.16%                93.34%
        4           89.91%                92.68%
        5           89.72%                92.64%
        6           90.49%                93.23%
        7           90.59%                92.83%

Best epoch:

``` text
Epoch 3
```

Best validation accuracy:

``` text
93.34%
```

------------------------------------------------------------------------

## 14. Fine-Tuning

After the frozen-backbone training and validation evaluation, the model
proceeded to the later fine-tuning stage.

The final selected checkpoint was:

``` text
model3a_step23_best_finetuned.keras
```

This checkpoint was used for the final internal test and external MRI
evaluation.

The exact fine-tuning layer configuration and fine-tuning
hyperparameters are not retained in the available execution logs and are
therefore not claimed here.

------------------------------------------------------------------------

## 15. Internal Validation Performance

The properly trained frozen model achieved:

``` text
Validation Accuracy : 93.34%
Macro Precision     : 0.8493
Macro Recall        : 0.8585
Macro F1            : 0.8476
Weighted Precision  : 0.9393
Weighted Recall     : 0.9334
Weighted F1         : 0.9329
```

The final fine-tuned model was subsequently evaluated on the untouched
internal test set.

------------------------------------------------------------------------

## 16. Final Internal Test

The final internal test was performed using the Step 23 best fine-tuned
model.

Test set:

``` text
Total images: 2639
```

Class distribution:

``` text
No_Tumor          : 253
Glioma            : 268
Meningioma        : 268
Pituitary         : 265
Brain_Metastasis  : 1472
Schwannoma        : 70
Meduloblastoma    : 20
Ependymoma        : 23
```

All test image paths were verified.

``` text
Missing images: 0
```

The test set was not used during the earlier training stages.

### Final Internal Test Metrics

``` text
Accuracy           : 94.92%
Macro Precision    : 0.8931
Macro Recall       : 0.9193
Macro F1           : 0.9040
Weighted Precision : 0.9506
Weighted Recall    : 0.9492
Weighted F1        : 0.9488
```

### Per-Class Results

  Class                Accuracy / Recall   Precision       F1
  ------------------ ------------------- ----------- --------
  No_Tumor                        91.30%      99.14%   0.9506
  Glioma                          84.70%      91.53%   0.8798
  Meningioma                      76.12%      82.26%   0.7907
  Pituitary                       99.25%      84.03%   0.9100
  Brain_Metastasis               100.00%      99.86%   0.9993
  Schwannoma                      97.14%      90.67%   0.9379
  Meduloblastoma                 100.00%      86.96%   0.9302
  Ependymoma                      86.96%      80.00%   0.8333

The most difficult class in the internal test was Meningioma, with
76.12% recall.

The strongest recall results were observed for:

``` text
Brain_Metastasis : 100.00%
Meduloblastoma   : 100.00%
Pituitary        : 99.25%
Schwannoma       : 97.14%
```

------------------------------------------------------------------------

## 17. Internal Test Confusion Patterns

The main confusion patterns in the final internal test were:

### Glioma

Some Glioma images were classified as:

``` text
Meningioma
Pituitary
```

### Meningioma

Meningioma showed the most significant confusion with:

``` text
Pituitary
Glioma
```

### Ependymoma

Some Ependymoma images were classified as:

``` text
Schwannoma
Meduloblastoma
```

### Brain Metastasis

Brain Metastasis showed extremely strong internal test performance:

``` text
1472 / 1472 correctly classified
```

This result should still be interpreted in the context of the specific
dataset and preprocessing pipeline.

------------------------------------------------------------------------

## 18. External MRI Generalization Test

A separate external test was performed using seven independent labeled
MRI images.

The following two files were deliberately excluded:

``` text
brain ct.jpg
brain mri.jpg
```

Therefore the external MRI test contained seven images:

``` text
Brain_Metastasis.jpeg
Ependymoma.png
Glioma.jpg
Medulloblastoma.jpg
Meningioma.jpg
Pituitary.png
Schwannoma.jpg
```

### External Results

  Actual             Prediction         Confidence Result
  ------------------ ---------------- ------------ -----------
  Brain_Metastasis   Meningioma             43.19% Incorrect
  Ependymoma         Schwannoma             93.27% Incorrect
  Glioma             Glioma                 43.98% Correct
  Meduloblastoma     Meduloblastoma         72.07% Correct
  Meningioma         Glioma                 56.27% Incorrect
  Pituitary          Pituitary              90.45% Correct
  Schwannoma         Schwannoma             99.92% Correct

Final external result:

``` text
Correct   : 4
Incorrect : 3
Accuracy  : 57.14%
```

Mean confidence:

``` text
71.31%
```

Median confidence:

``` text
72.07%
```

### Interpretation

The external result is substantially lower than the internal test
result.

This indicates that the model may experience domain shift when presented
with images from a different source, acquisition protocol, image style,
preprocessing pipeline, or image distribution.

However, the external test contains only seven images. Therefore:

``` text
57.14% is NOT a reliable estimate of real-world accuracy.
```

A larger independent external dataset is required for a meaningful
generalization study.

The external images were not used for retraining, so their evaluation
remained independent.

------------------------------------------------------------------------

## 19. Why Internal and External Performance Differ

The internal test and external test answer different questions.

### Internal test

The internal test asks:

> How well does the trained model perform on previously unseen images
> drawn from the prepared dataset distribution?

Result:

``` text
94.92%
```

### External test

The external test asks:

> How well does the model behave on a very small set of independently
> sourced MRI images?

Result:

``` text
57.14%
```

The difference demonstrates why external validation is important.

The external test should not be used to artificially tune the model and
then reported as an unbiased external result.

------------------------------------------------------------------------

## 20. Model Files

The original best fine-tuned checkpoint:

``` text
/content/model3a/models/checkpoints/model3a_step23_best_finetuned.keras
```

The final renamed model:

``` text
Model3A_EfficientNetB0_BrainTumor_8Class_Final.keras
```

The final model package also contains:

``` text
model3a_config.json
README.txt
```

The configuration stores:

-   Model name
-   Architecture
-   Input size
-   Number of classes
-   Class mapping
-   Internal test metrics
-   External MRI test metrics
-   Model status

------------------------------------------------------------------------

## 21. How to Load the Final Model

Python / TensorFlow:

``` python
import tensorflow as tf

model = tf.keras.models.load_model(
    "Model3A_EfficientNetB0_BrainTumor_8Class_Final.keras",
    compile=False
)

print(model.input_shape)
print(model.output_shape)
```

Expected output:

``` text
(None, 224, 224, 3)
(None, 8)
```

------------------------------------------------------------------------

## 22. Basic Inference Example

``` python
import numpy as np
import tensorflow as tf

from PIL import Image

CLASS_NAMES = [
    "No_Tumor",
    "Glioma",
    "Meningioma",
    "Pituitary",
    "Brain_Metastasis",
    "Schwannoma",
    "Meduloblastoma",
    "Ependymoma"
]

MODEL_PATH = (
    "Model3A_EfficientNetB0_BrainTumor_8Class_Final.keras"
)

model = tf.keras.models.load_model(
    MODEL_PATH,
    compile=False
)

image = Image.open(
    "test_image.jpg"
).convert("RGB")

image = image.resize(
    (224, 224)
)

image_array = np.asarray(
    image,
    dtype=np.float32
)

image_array = np.expand_dims(
    image_array,
    axis=0
)

probabilities = model.predict(
    image_array,
    verbose=0
)[0]

predicted_id = int(
    np.argmax(probabilities)
)

predicted_class = CLASS_NAMES[
    predicted_id
]

confidence = float(
    probabilities[predicted_id]
)

print(
    "Prediction:",
    predicted_class
)

print(
    f"Confidence: {confidence * 100:.2f}%"
)
```

Example output:

``` text
Prediction: Meningioma
Confidence: 92.41%
```

The confidence value is the model's softmax probability and should not
be interpreted as a medically calibrated probability of disease.

------------------------------------------------------------------------

## 23. Recommended Input

The model was developed for brain MRI image classification.

Recommended input characteristics:

``` text
Image type : MRI
Color      : RGB
Size       : Any reasonable source size
Model size : 224 × 224
Channels   : 3
```

The inference pipeline converts the image to RGB and resizes it to:

``` text
224 × 224 × 3
```

CT images were not part of the final Model 3A external MRI evaluation.

Therefore this model should not be described as a validated CT
classifier.

------------------------------------------------------------------------

## 24. Training Environment

The model was trained in Google Colab.

Recorded TensorFlow version during the pipeline:

``` text
TensorFlow 2.20.0
```

GPU availability was verified during training:

``` text
GPU: /physical_device:GPU:0
```

The workflow was designed to operate with limited RAM by using:

-   Manifest-based datasets
-   Lazy image loading
-   TensorFlow batching
-   Prefetching
-   Patient-at-a-time NIfTI processing
-   Avoidance of full-volume accumulation in RAM

The brain metastasis extraction stage was specifically rewritten to
prevent the complete MRI dataset from being loaded into memory.

------------------------------------------------------------------------

## 25. Reproducibility and Audit Files

Important manifests and audit files were generated throughout the
pipeline.

Examples include:

``` text
brain_metastasis_patient_pairing.csv
brain_metastasis_tumor_positive_slices.csv
brain_metastasis_processed_manifest.csv
model3a_8class_source_manifest.csv
model3a_8class_split_manifest.csv
model3a_8class_split_counts.csv
model3a_brain_metastasis_patient_split.csv
model3a_8class_balanced_train_manifest.csv
model3a_8class_validation_manifest.csv
model3a_8class_test_manifest.csv
```

Evaluation outputs included:

``` text
model3a_step25_internal_test_predictions.csv
model3a_step25_internal_test_metrics.csv
model3a_step25_internal_test_report.csv
model3a_step25_internal_test_confusion_matrix.csv
model3a_step25_internal_test_per_class.csv
model3a_step26_external_mri_results.csv
model3a_step26_external_mri_report.csv
model3a_step26_external_mri_confusion_matrix.csv
```

These files document the dataset construction, splitting, balancing, and
evaluation process.

------------------------------------------------------------------------

## 26. Data Leakage Controls

Model 3A explicitly checked for two important forms of leakage.

### Patient-level leakage

For brain metastasis:

``` text
Train patients ∩ Validation patients = 0
Train patients ∩ Test patients = 0
Validation patients ∩ Test patients = 0
```

### Exact-image leakage

SHA-256 image hashes were compared across splits.

Result:

``` text
Hashes appearing in multiple splits: 0
```

Therefore no exact duplicate image was found across training,
validation, and test splits.

------------------------------------------------------------------------

## 27. Important Dataset Limitation

The class distribution is not naturally balanced.

The rare classes include:

``` text
Meduloblastoma
Ependymoma
Schwannoma
```

The training dataset therefore used manifest-level oversampling.

Validation and test sets were not artificially balanced.

This is important because the internal test represents the prepared
dataset distribution rather than an artificially equal class
distribution.

In particular, Brain Metastasis has a much larger number of test images
than several rare classes.

For this reason, both accuracy and macro F1 should be reported.

------------------------------------------------------------------------

## 28. Important External Validation Limitation

The external test contained only seven labeled MRI images.

Therefore:

``` text
External accuracy = 57.14%
```

should not be presented as the definitive real-world accuracy of the
model.

It should be described as:

> A small independent external MRI generalization test.

A proper external validation study should contain a substantially larger
number of independently sourced patients and images, ideally with
patient-level separation and representative class distributions.

------------------------------------------------------------------------

## 29. Final Performance Summary

``` text
============================================================
MODEL 3A FINAL SUMMARY
============================================================

Architecture:
    EfficientNetB0

Input:
    224 × 224 × 3 RGB

Output:
    8-class Softmax

Classes:
    8

Training:
    Completed

Fine-tuning:
    Completed

Final checkpoint:
    Step 23 best fine-tuned model

------------------------------------------------------------

INTERNAL TEST

Images:
    2639

Accuracy:
    94.92%

Macro Precision:
    0.8931

Macro Recall:
    0.9193

Macro F1:
    0.9040

Weighted F1:
    0.9488

------------------------------------------------------------

EXTERNAL MRI TEST

Independent images:
    7

Correct:
    4

Incorrect:
    3

Accuracy:
    57.14%

------------------------------------------------------------

DATA LEAKAGE

Patient leakage:
    None detected

Exact image hash leakage:
    None detected

------------------------------------------------------------

FINAL STATUS

Model:
    FROZEN

Training:
    COMPLETE

Internal evaluation:
    COMPLETE

External evaluation:
    COMPLETE

CT external test:
    EXCLUDED

Final model:
    Model3A_EfficientNetB0_BrainTumor_8Class_Final.keras
============================================================
```

------------------------------------------------------------------------

## 30. Model 3A Conclusion

Model 3A successfully implements an eight-class brain tumor MRI
classification pipeline using EfficientNetB0.

The final model achieved:

``` text
94.92% accuracy
0.9040 macro F1
```

on the 2,639-image internal held-out test set.

The model also demonstrated the ability to classify several independent
MRI examples correctly, although the seven-image external test produced
a lower accuracy of 57.14%, highlighting domain-shift and generalization
limitations.

The final checkpoint is frozen and should be treated as the completed
Model 3A model.

Future experiments should be versioned separately rather than modifying
this final checkpoint.

------------------------------------------------------------------------

## 31. Final Model Identity

**Model Name:**

`Model3A_EfficientNetB0_BrainTumor_8Class_Final`

**Architecture:**

`EfficientNetB0`

**Task:**

`8-Class Brain Tumor MRI Classification`

**Input:**

`224 × 224 × 3 RGB`

**Output:**

`8-Class Softmax`

**Final Internal Test Accuracy:**

`94.92%`

**Final Internal Test Macro F1:**

`0.9040`

**External MRI Pilot Accuracy:**

`57.14% on 7 independent images`

**Status:**

`FINAL / FROZEN`
