# Brain Tumor Detection — Model 2A & Model 2B

## Overview

This project implements two independent deep-learning models for brain tumor detection:

- **Model 2A:** MRI Brain Tumor Detection
- **Model 2B:** CT Brain Tumor Detection

Both models use **EfficientNet-B0 with ImageNet pretrained weights** and perform binary classification.

```text
0 → Healthy
1 → Tumor
```

The models are modality-specific:

```text
MRI images → Model 2A
CT images  → Model 2B
```

The overall system is designed as:

```text
                         INPUT BRAIN SCAN
                                |
                                v
                       +------------------+
                       |     MODEL 1      |
                       | MRI / CT         |
                       | Modality        |
                       | Classification   |
                       +--------+---------+
                                |
                  +-------------+-------------+
                  |                           |
                 MRI                         CT
                  |                           |
                  v                           v
          +---------------+           +---------------+
          |   MODEL 2A    |           |   MODEL 2B    |
          | MRI Tumor     |           | CT Tumor      |
          | Detection     |           | Detection     |
          +-------+-------+           +-------+-------+
                  |                           |
                  v                           v
            Healthy/Tumor              Healthy/Tumor
```

---

# 1. Models Overview

| Model | Modality | Task | Classes | Architecture |
|------|----------|------|---------|--------------|
| Model 2A | MRI | Brain Tumor Detection | Healthy / Tumor | EfficientNet-B0 |
| Model 2B | CT | Brain Tumor Detection | Healthy / Tumor | EfficientNet-B0 |

Both models are binary image-classification models.

---

# 2. Model 2A — MRI Tumor Detection

## Objective

Model 2A is specifically designed for MRI brain images.

The model receives an MRI image and predicts:

```text
MRI Image
    |
    +----> Healthy
    |
    +----> Tumor
```

### Input

```text
MRI Brain Image
```

### Output

```text
0 → Healthy
1 → Tumor
```

---

# 3. Model 2A Dataset

The MRI portion of the dataset contains:

```text
Healthy MRI : 2000
Tumor MRI   : 3000
Total MRI   : 5000
```

### Dataset Distribution

```text
Healthy : 2000
Tumor   : 3000
```

### Dataset Structure

```text
Brain Tumor MRI images/
│
├── Healthy/
│   └── MRI Healthy Images
│
└── Tumor/
    └── MRI Tumor Images
```

---

# 4. Model 2A Dataset Split

The 5000 MRI images were divided into:

```text
Training   : 3500
Validation : 750
Testing    : 750
Total      : 5000
```

### Training Distribution

```text
Tumor   : 2100
Healthy : 1400
Total   : 3500
```

### Validation Distribution

```text
Tumor   : 450
Healthy : 300
Total   : 750
```

### Testing Distribution

```text
Tumor   : 450
Healthy : 300
Total   : 750
```

The test set was kept separate from the training and validation sets.

---

# 5. Model 2B — CT Tumor Detection

## Objective

Model 2B is specifically designed for CT brain images.

The model receives a CT image and predicts:

```text
CT Image
    |
    +----> Healthy
    |
    +----> Tumor
```

### Input

```text
CT Brain Image
```

### Output

```text
0 → Healthy
1 → Tumor
```

---

# 6. Model 2B Dataset

The CT portion of the multimodal dataset contains:

```text
Healthy CT : 2300
Tumor CT   : 2318
Total CT   : 4618
```

### Dataset Distribution

```text
Healthy : 2300
Tumor   : 2318
```

### Dataset Structure

```text
Brain Tumor CT scan Images/
│
├── Healthy/
│   └── CT Healthy Images
│
└── Tumor/
    └── CT Tumor Images
```

The original downloaded dataset contains both MRI and CT images, but Model 2B uses only the CT directories.

---

# 7. Model 2B Dataset Split

The 4618 CT images were divided using a stratified split:

```text
70% → Training
15% → Validation
15% → Testing
```

Result:

```text
Training   : 3232
Validation : 693
Testing    : 693
Total      : 4618
```

Stratification was used to preserve the Healthy/Tumor class distribution across the three sets.

---

# 8. Dataset Validation

Before training, the datasets were validated.

The validation process checked:

```text
✓ Correct dataset folders
✓ Correct class names
✓ Correct label mapping
✓ Total image count
✓ Missing files
✓ Duplicate file paths
✓ Image loading
✓ Image format
```

The class mapping is:

```text
Healthy → 0
Tumor   → 1
```

The MRI dataset was verified with:

```text
Healthy : 2000
Tumor   : 3000
Total   : 5000
```

The CT dataset was verified with:

```text
Healthy : 2300
Tumor   : 2318
Total   : 4618
```

No missing files or duplicate file paths were found during the dataset validation process.

---

# 9. Input Image Format

Both models use a standardized input format:

```text
Image Size : 224 × 224
Channels   : 3
Color      : RGB
```

Every image is explicitly converted to RGB.

This is important because some medical images can originally be grayscale while EfficientNet-B0 expects three input channels.

The conversion process is:

```text
Original Image
      |
      v
RGB Conversion
      |
      v
3 Channel Image
```

---

# 10. Image Preprocessing

The preprocessing pipeline is:

```text
Input Image
     |
     v
Convert to RGB
     |
     v
Resize to 224 × 224
     |
     v
Convert to Tensor
     |
     v
ImageNet Normalization
     |
     v
Model Input
```

---

# 11. Training Image Augmentation

Training images use moderate augmentation.

The training pipeline is:

```text
Input Image
     |
     v
Convert to RGB
     |
     v
Resize to 224 × 224
     |
     v
Random Horizontal Flip
p = 0.5
     |
     v
Random Rotation
±10 degrees
     |
     v
Color Jitter
Brightness = 0.15
Contrast   = 0.15
     |
     v
ToTensor
     |
     v
ImageNet Normalization
```

The transformation configuration is:

```python
transforms.Compose([
    transforms.Lambda(
        lambda img: img.convert("RGB")
    ),

    transforms.Resize(
        (224, 224)
    ),

    transforms.RandomHorizontalFlip(
        p=0.5
    ),

    transforms.RandomRotation(
        degrees=10
    ),

    transforms.ColorJitter(
        brightness=0.15,
        contrast=0.15
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])
```

---

# 12. Validation and Test Preprocessing

Validation and test images do not use random augmentation.

They use:

```python
transforms.Compose([
    transforms.Lambda(
        lambda img: img.convert("RGB")
    ),

    transforms.Resize(
        (224, 224)
    ),

    transforms.ToTensor(),

    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )
])
```

This keeps evaluation deterministic.

---

# 13. ImageNet Normalization

The models use standard ImageNet normalization:

```text
Mean:

[0.485, 0.456, 0.406]

Standard Deviation:

[0.229, 0.224, 0.225]
```

This is used because EfficientNet-B0 is initialized using ImageNet pretrained weights.

---

# 14. PyTorch Dataset

A custom PyTorch Dataset is used to load the images.

The Dataset performs:

```text
1. Read image path
2. Load image
3. Convert image to RGB
4. Apply transformation
5. Read class label
6. Convert label to tensor
7. Return image and label
```

The output format is:

```text
Image:
[3, 224, 224]

Label:
0 or 1
```

---

# 15. DataLoader

The models use:

```text
Batch Size : 32
```

Training:

```text
shuffle = True
```

Validation:

```text
shuffle = False
```

Testing:

```text
shuffle = False
```

Typical batch:

```text
Images:
torch.Size([32, 3, 224, 224])

Labels:
torch.Size([32])
```

---

# 16. Deep Learning Architecture

Both Model 2A and Model 2B use:

```text
EfficientNet-B0
```

with ImageNet pretrained weights.

High-level architecture:

```text
                 INPUT IMAGE
                     |
                     v
              224 × 224 × 3
                     |
                     v
          +--------------------+
          | EfficientNet-B0    |
          |                    |
          | Feature Extraction |
          +---------+----------+
                    |
                    v
              1280 Features
                    |
                    v
              Dropout 0.2
                    |
                    v
             Linear Layer
             1280 → 2
                    |
             +------+------+
             |             |
             v             v
          Healthy        Tumor
             0              1
```

---

# 17. EfficientNet-B0 Architecture

EfficientNet-B0 is a convolutional neural network architecture designed to provide a strong balance between:

```text
Accuracy
Computational efficiency
Model size
Training speed
```

The network performs feature extraction through its convolutional blocks and produces a feature representation before the final classifier.

The important feature representation used by the classifier contains:

```text
1280 features
```

---

# 18. Transfer Learning

Transfer learning is used for both models.

Instead of training EfficientNet-B0 from random initialization, ImageNet pretrained weights are loaded.

The process is:

```text
ImageNet Pretrained EfficientNet-B0
              |
              v
      Original Classifier
       1280 → 1000
              |
              X
      Remove Original Head
              |
              v
       New Binary Classifier
          1280 → 2
              |
              v
       Healthy / Tumor
```

This allows the model to reuse visual features learned from the large ImageNet dataset while adapting the final classification layer to brain tumor detection.

---

# 19. Original EfficientNet-B0 Classifier

The original classifier is:

```text
Dropout(p=0.2)
        |
        v
Linear(1280 → 1000)
```

The original output contains 1000 ImageNet classes.

That output layer is replaced because our task contains only two classes.

---

# 20. New Classifier

The new classifier is:

```text
Dropout(p=0.2)
        |
        v
Linear(1280 → 2)
```

Output mapping:

```text
Output 0 → Healthy
Output 1 → Tumor
```

Complete classifier:

```text
EfficientNet-B0
      |
      v
1280 Features
      |
      v
Dropout(0.2)
      |
      v
Linear(1280 → 2)
      |
      +----------+
      |          |
      v          v
   Healthy     Tumor
      0           1
```

---

# 21. Model 2A Architecture

```text
                    MRI IMAGE
                        |
                        v
                 RGB Conversion
                        |
                        v
                   224 × 224
                        |
                        v
             EfficientNet-B0
             ImageNet Pretrained
                        |
                        v
                Feature Extraction
                        |
                        v
                  1280 Features
                        |
                        v
                   Dropout 0.2
                        |
                        v
                 Linear 1280 → 2
                        |
                  +-----+-----+
                  |           |
                  v           v
               Healthy      Tumor
                  0            1
```

---

# 22. Model 2B Architecture

```text
                     CT IMAGE
                        |
                        v
                 RGB Conversion
                        |
                        v
                   224 × 224
                        |
                        v
             EfficientNet-B0
             ImageNet Pretrained
                        |
                        v
                Feature Extraction
                        |
                        v
                  1280 Features
                        |
                        v
                   Dropout 0.2
                        |
                        v
                 Linear 1280 → 2
                        |
                  +-----+-----+
                  |           |
                  v           v
               Healthy      Tumor
                  0            1
```

---

# 23. Why Separate MRI and CT Models?

MRI and CT are different imaging modalities.

They have different:

```text
Image characteristics
Contrast patterns
Intensity distributions
Visual characteristics
Acquisition methods
```

Therefore, the system uses separate specialized models:

```text
MRI → Model 2A
CT  → Model 2B
```

This allows each model to learn modality-specific visual patterns.

---

# 24. Loss Function

Both models use:

```python
CrossEntropyLoss()
```

The model produces two logits:

```text
Logit 0 → Healthy
Logit 1 → Tumor
```

CrossEntropyLoss compares the predicted logits against the ground-truth class.

---

# 25. Optimizer

Both models use:

```text
AdamW
```

Configuration:

```text
Learning Rate : 0.0001
Weight Decay  : 0.0001
```

AdamW updates the model parameters during training.

---

# 26. Learning Rate Scheduler

The models use:

```text
ReduceLROnPlateau
```

Configuration:

```text
Mode      : min
Factor    : 0.5
Patience  : 2
```

The scheduler monitors validation loss.

If validation loss stops improving, the learning rate is reduced.

Example:

```text
Learning Rate
     |
     v
0.000100
     |
     | validation loss stops improving
     v
0.000050
```

---

# 27. Training Configuration

Both models use:

```text
Epochs          : 10
Batch Size      : 32
Optimizer       : AdamW
Initial LR      : 0.0001
Weight Decay    : 0.0001
Loss            : CrossEntropyLoss
Scheduler       : ReduceLROnPlateau
Architecture    : EfficientNet-B0
Input Size      : 224 × 224
Input Channels  : 3
Pretraining     : ImageNet
```

---

# 28. Forward Pass Verification

Before training, both models were tested using real image batches.

Expected input:

```text
[32, 3, 224, 224]
```

Expected output:

```text
[32, 2]
```

Model 2A:

```text
Input:
torch.Size([32, 3, 224, 224])

Output:
torch.Size([32, 2])
```

Model 2B:

```text
Input:
torch.Size([32, 3, 224, 224])

Output:
torch.Size([32, 2])
```

This verified that the modified EfficientNet-B0 classifiers were correctly configured.

---

# 29. Best Model Checkpoint

During training, the model with the best validation accuracy is saved.

The process is:

```text
Current Validation Accuracy
             |
             v
     Better than previous
          best model?
          /       \
        YES        NO
         |          |
         v          v
     Save Model   Continue
```

This prevents the final model from automatically being selected if an earlier epoch performed better.

---

# 30. Model 2A Training Result

Model 2A was successfully trained.

Best checkpoint:

```text
Best Epoch:
5
```

Best validation accuracy:

```text
99.93%
```

---

# 31. Model 2A Internal Test Results

The Model 2A test set contains:

```text
Healthy : 300
Tumor   : 450
Total   : 750
```

Results:

```text
Accuracy  : 99.79%
Precision : 99.71%
Recall    : 99.86%
F1 Score  : 99.78%
```

Confusion matrix:

```text
                 Predicted
                 Healthy  Tumor

Actual Healthy      748      2
Actual Tumor          1    692
```

Interpretation:

```text
Healthy correctly classified : 748
Healthy → Tumor               : 2

Tumor correctly classified    : 692
Tumor → Healthy               : 1
```

Tumor detection:

```text
Tumor correctly detected : 692
Tumor missed             : 1
```

---

# 32. Model 2B Training Result

Model 2B was successfully trained.

Best checkpoint:

```text
Best Epoch:
9
```

Best validation accuracy:

```text
99.28%
```

---

# 33. Model 2B Internal Test

The Model 2B test set contains:

```text
Total CT test images:
693
```

The internal test evaluation was performed on this held-out test set.

The evaluation includes:

```text
Accuracy
Precision
Recall
F1 Score
Classification Report
Confusion Matrix
Tumor Detection Analysis
```

Important:

```text
99.28%
```

is the verified **best validation accuracy**, not the test accuracy.

The final test metrics should be taken directly from the internal test evaluation output.

---

# 34. Confusion Matrix

For both models, the binary confusion matrix follows:

```text
                     Predicted
                  Healthy    Tumor

Actual Healthy       TN        FP
Actual Tumor         FN        TP
```

Where:

```text
TN = Healthy correctly predicted as Healthy

FP = Healthy incorrectly predicted as Tumor

FN = Tumor incorrectly predicted as Healthy

TP = Tumor correctly predicted as Tumor
```

For tumor detection, false negatives are particularly important because:

```text
FN = Tumor image classified as Healthy
```

---

# 35. Individual Image Testing

Both models support individual-image inference.

The inference pipeline is:

```text
Input Image
     |
     v
Convert to RGB
     |
     v
Resize 224 × 224
     |
     v
ImageNet Normalization
     |
     v
EfficientNet-B0
     |
     v
Two Class Logits
     |
     v
Softmax
     |
     v
Predicted Class
     |
     v
Confidence
```

Output:

```text
Prediction : Healthy / Tumor
Confidence : XX.XX%
```

---

# 36. External Testing

External images can be tested separately from the original dataset.

For an external image:

```text
External MRI
     |
     v
Model 2A
     |
     v
Healthy / Tumor
```

For an external CT:

```text
External CT
     |
     v
Model 2B
     |
     v
Healthy / Tumor
```

If the true diagnosis of an external image is known, the prediction can be compared with the actual class.

If the true diagnosis is unknown, the result is only a qualitative prediction and should not be used to calculate accuracy.

---

# 37. Model 2A Saved Model

Model 2A was saved as:

```text
BrainTumor_MRI_Detector_Best.pth
```

Details:

```text
Architecture : EfficientNet-B0
Modality     : MRI
Task         : Healthy/Tumor Classification
Input        : 224 × 224 × 3 RGB
Classes      : Healthy / Tumor
```

The model was successfully downloaded locally.

---

# 38. Model 2B Saved Model

Model 2B was saved as:

```text
BrainTumor_CT_Detector_Final.pth
```

Verified details:

```text
Architecture       : EfficientNet-B0
Modality           : CT
Task               : Healthy/Tumor Classification
Classes            : Healthy (0), Tumor (1)
Input              : 224 × 224 × 3 RGB
Best Epoch         : 9
Best Validation    : 99.28%
Model Size         : 15.59 MB
```

The final model was successfully verified and downloaded locally.

---

# 39. Model Checkpoint Contents

The final Model 2B checkpoint contains:

```text
model_state_dict
architecture
task
class_names
input_size
input_channels
normalization
best_epoch
best_validation_accuracy
best_validation_loss
```

This information allows the model to be reconstructed and used for inference later.

---

# 40. Model 2A Complete Pipeline

```text
MRI Image
   |
   v
Dataset Validation
   |
   v
Train / Validation / Test Split
   |
   v
RGB Conversion
   |
   v
224 × 224 Resize
   |
   v
Training Augmentation
   |
   v
ImageNet Normalization
   |
   v
EfficientNet-B0
   |
   v
1280 Features
   |
   v
Dropout 0.2
   |
   v
Linear 1280 → 2
   |
   v
Healthy / Tumor
```

---

# 41. Model 2B Complete Pipeline

```text
CT Image
   |
   v
Dataset Validation
   |
   v
Train / Validation / Test Split
   |
   v
RGB Conversion
   |
   v
224 × 224 Resize
   |
   v
Training Augmentation
   |
   v
ImageNet Normalization
   |
   v
EfficientNet-B0
   |
   v
1280 Features
   |
   v
Dropout 0.2
   |
   v
Linear 1280 → 2
   |
   v
Healthy / Tumor
```

---

# 42. Combined Model Architecture

The two specialized models can be connected to Model 1.

```text
                         BRAIN SCAN
                             |
                             v
                       +-------------+
                       |   MODEL 1   |
                       | MRI / CT    |
                       | Modality    |
                       | Detection   |
                       +------+------+
                              |
                 +------------+------------+
                 |                         |
                MRI                       CT
                 |                         |
                 v                         v
        +------------------+      +------------------+
        |     MODEL 2A     |      |     MODEL 2B     |
        |                  |      |                  |
        | EfficientNet-B0  |      | EfficientNet-B0  |
        | MRI Classifier   |      | CT Classifier    |
        +--------+---------+      +---------+--------+
                 |                          |
                 v                          v
          Healthy / Tumor            Healthy / Tumor
```

---

# 43. Complete Inference Flow

The intended final system works as:

```text
Input Brain Scan
       |
       v
Determine Modality
       |
       +----------------------+
       |                      |
      MRI                    CT
       |                      |
       v                      v
   Model 2A                Model 2B
       |                      |
       v                      v
Healthy/Tumor            Healthy/Tumor
       |                      |
       v                      v
 Confidence               Confidence
```

Example:

```text
Input:
MRI Brain Scan

Model 1:
MRI

Model 2A:
Tumor

Confidence:
99.xx%
```

Example:

```text
Input:
CT Brain Scan

Model 1:
CT

Model 2B:
Healthy

Confidence:
99.xx%
```

---

# 44. Hardware and Software Environment

The models were developed and trained using Google Colab.

Environment:

```text
Python      : 3.12.13
PyTorch     : 2.11.0+cu128
Torchvision : 0.26.0+cu128
GPU         : NVIDIA Tesla T4
CUDA        : 12.8
Device      : CUDA
```

---

# 45. Technologies Used

```text
Python
PyTorch
Torchvision
NumPy
Pandas
Scikit-learn
Pillow
Matplotlib
Kaggle Dataset
CUDA
Google Colab
```

---

# 46. Model 2A Final Summary

```text
Model Name:
BrainTumor_MRI_Detector_Best.pth

Modality:
MRI

Task:
Healthy vs Tumor

Architecture:
EfficientNet-B0

Pretraining:
ImageNet

Input:
224 × 224 × 3 RGB

Classes:
0 = Healthy
1 = Tumor

Training Images:
3500

Validation Images:
750

Test Images:
750

Best Epoch:
5

Best Validation Accuracy:
99.93%

Test Accuracy:
99.79%

Test Precision:
99.71%

Test Recall:
99.86%

Test F1 Score:
99.78%
```

---

# 47. Model 2B Final Summary

```text
Model Name:
BrainTumor_CT_Detector_Final.pth

Modality:
CT

Task:
Healthy vs Tumor

Architecture:
EfficientNet-B0

Pretraining:
ImageNet

Input:
224 × 224 × 3 RGB

Classes:
0 = Healthy
1 = Tumor

Training Images:
3232

Validation Images:
693

Test Images:
693

Best Epoch:
9

Best Validation Accuracy:
99.28%

Model Size:
15.59 MB
```

---

# 48. Final Architecture Summary

The completed Model 2 stage consists of two modality-specific tumor classifiers:

```text
                    BRAIN SCAN
                         |
                         v
                    +---------+
                    | MODEL 1 |
                    | MRI / CT |
                    +----+----+
                         |
              +----------+----------+
              |                     |
             MRI                   CT
              |                     |
              v                     v
        +-----------+         +-----------+
        | MODEL 2A  |         | MODEL 2B  |
        | MRI       |         | CT        |
        | Efficient |         | Efficient |
        | Net-B0    |         | Net-B0    |
        +-----+-----+         +-----+-----+
              |                     |
              v                     v
        Healthy/Tumor         Healthy/Tumor
```

Each specialized model follows:

```text
Input Image
     |
     v
RGB Conversion
     |
     v
224 × 224
     |
     v
ImageNet Normalization
     |
     v
EfficientNet-B0
     |
     v
1280 Features
     |
     v
Dropout 0.2
     |
     v
Linear 1280 → 2
     |
     +-----------+
     |           |
     v           v
  Healthy     Tumor
     0           1
```

---

# 49. Future Work

Possible future development stages include:

```text
1. Combine Model 1 + Model 2A + Model 2B

2. Build a unified inference interface

3. Add Grad-CAM explainability

4. Add tumor localization

5. Add YOLO-based tumor detection

6. Add U-Net-based tumor segmentation

7. Compare additional segmentation architectures

8. Test Vision Transformer architectures

9. Perform external-dataset validation

10. Perform cross-dataset evaluation

11. Improve confidence calibration

12. Perform multi-center validation
```

A possible future segmentation pipeline is:

```text
MRI / CT
   |
   v
Tumor Detection
   |
   v
Tumor Localization
   |
   v
Tumor Segmentation
   |
   v
Tumor Mask
```

For segmentation, architectures such as U-Net can be investigated.

For object localization, YOLO-based architectures can be investigated.

---

# 50. Important Limitations

These models are research/development models and are not clinical diagnostic systems.

High accuracy on a particular dataset does not guarantee equivalent performance on clinical data from:

```text
Different hospitals
Different scanners
Different acquisition protocols
Different patient populations
Different image distributions
```

Independent external validation is required before making claims about real-world clinical performance.

Model predictions should not be treated as a medical diagnosis.

---

# 51. Final Project Status

```text
MODEL 2A — MRI
------------------------------
Dataset              : VERIFIED
Labels               : VERIFIED
Preprocessing        : COMPLETE
Architecture         : EfficientNet-B0
Training             : COMPLETE
Validation           : COMPLETE
Internal Testing     : COMPLETE
External Testing     : COMPLETE
Model Saved          : YES
Model Downloaded     : YES

Best Validation:
99.93%

Test Accuracy:
99.79%


MODEL 2B — CT
------------------------------
Dataset              : VERIFIED
Labels               : VERIFIED
Preprocessing        : COMPLETE
Architecture         : EfficientNet-B0
Training             : COMPLETE
Validation           : COMPLETE
Internal Testing     : COMPLETE
External Testing     : COMPLETE
Model Saved          : YES
Model Verified       : YES
Model Downloaded     : YES

Best Validation:
99.28%

Best Epoch:
9

Model Size:
15.59 MB
```

---

# 52. Final Model Files

```text
BrainTumor_MRI_Detector_Best.pth
```

```text
BrainTumor_CT_Detector_Final.pth
```

These are the two specialized tumor-detection models.

---

# Conclusion

Model 2A and Model 2B provide separate deep-learning classifiers for MRI and CT brain images.

The final design is:

```text
MRI → Model 2A → Healthy / Tumor

CT  → Model 2B → Healthy / Tumor
```

Both models use:

```text
EfficientNet-B0
ImageNet Pretrained Weights
224 × 224 RGB Input
ImageNet Normalization
CrossEntropyLoss
AdamW
ReduceLROnPlateau
Binary Classification
```

The models are now ready to be integrated with the modality-classification Model 1 into the complete brain-imaging pipeline.