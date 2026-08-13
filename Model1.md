# BrainScan Modality Model

## MRI vs CT Brain Image Classification

---

## 1. Overview

The **BrainScan Modality Model** is a deep learning image classification model developed to automatically identify whether a given brain scan is an:

- MRI (Magnetic Resonance Imaging)
- CT (Computed Tomography)

This is the first model in the BrainScan AI project.

The responsibility of this model is only to identify the imaging modality.

It does NOT diagnose brain tumors or other diseases.

### Input

A brain medical image such as:

- JPG
- JPEG
- PNG
- BMP
- WebP

### Output

    Class 0 → MRI
    Class 1 → CT

Example:

    Prediction : MRI
    Confidence : 99.8%

---

# 2. Problem Statement

Medical brain images can be obtained using different imaging modalities, mainly MRI and CT. These modalities have different image characteristics and are generally processed using different medical image-analysis techniques.

Manually identifying the modality can introduce unnecessary processing steps in an automated healthcare system.

Therefore, the objective of this model is:

> To develop an automated deep learning model that can distinguish between brain MRI and CT images and return the predicted modality with a confidence score.

---

# 3. Objectives

The main objectives of this model are:

1. Automatically identify whether an input brain image is MRI or CT.
2. Handle images with different resolutions and formats.
3. Standardize all images before model inference.
4. Use transfer learning for efficient training.
5. Train and validate the model using a dedicated dataset.
6. Evaluate the model on an unseen test dataset.
7. Save the trained model for future deployment.
8. Provide a reusable prediction function for individual images.

---

# 4. Technologies Used

| Component | Technology |
|---|---|
| Programming Language | Python |
| Deep Learning Framework | PyTorch |
| Computer Vision | Torchvision |
| Model Architecture | EfficientNet-B0 |
| Pretrained Weights | ImageNet |
| Image Processing | PIL |
| Data Processing | Pandas |
| Numerical Processing | NumPy |
| Dataset Splitting | Scikit-learn |
| Evaluation | Scikit-learn |
| Training Platform | Google Colab |
| GPU | NVIDIA Tesla T4 |
| Model Format | PyTorch `.pth` |

---

# 5. Dataset

The dataset was obtained from Kaggle and contains brain CT and MRI images.

The dataset is organized according to imaging modality and health condition.

### Dataset Structure

    Dataset/
    │
    ├── Brain Tumor CT scan Images/
    │   │
    │   ├── Healthy/
    │   │
    │   └── Tumor/
    │
    └── Brain Tumor MRI images/
        │
        ├── Healthy/
        │
        └── Tumor/

---

# 6. Dataset Statistics

The complete dataset contains:

    Total Images = 9,618

### CT Dataset

    CT Healthy = 2,300
    CT Tumor   = 2,318

    Total CT = 4,618

### MRI Dataset

    MRI Healthy = 2,000
    MRI Tumor   = 3,000

    Total MRI = 5,000

### Overall Dataset

| Modality | Healthy | Tumor | Total |
|---|---:|---:|---:|
| CT | 2,300 | 2,318 | 4,618 |
| MRI | 2,000 | 3,000 | 5,000 |
| **Total** | **4,300** | **5,318** | **9,618** |

---

# 7. Important Dataset Labeling

For this model, the `Healthy` and `Tumor` folders are NOT used as the target classes.

The model is trained only to identify the imaging modality.

The labels are:

    MRI → 0
    CT  → 1

The dataset is therefore conceptually converted as:

    MRI Healthy ─────┐
                     │
    MRI Tumor ───────┼──→ MRI (0)
                     │
                     │
    CT Healthy ──────┐
                     │
    CT Tumor ────────┼──→ CT (1)

This is important because:

> Model 1 is a modality classifier, not a tumor classifier.

The presence or absence of a tumor is not the prediction target.

---

# 8. Dataset Distribution After Labeling

After combining the Healthy and Tumor folders according to modality:

    MRI = 5,000 images
    CT  = 4,618 images

### Label Distribution

    Label 0 → MRI → 5,000 images
    Label 1 → CT  → 4,618 images

---

# 9. Dataset Split

The dataset was divided into:

    Training   → 70%
    Validation → 15%
    Testing    → 15%

### Final Split

    Total      = 9,618
    Training   = 6,732
    Validation = 1,443
    Testing    = 1,443

The dataset was split while maintaining the MRI/CT distribution.

---

# 10. Train / Validation / Test Distribution

| Dataset | MRI | CT | Total |
|---|---:|---:|---:|
| Training | 3,500 | 3,232 | 6,732 |
| Validation | 750 | 693 | 1,443 |
| Testing | 750 | 693 | 1,443 |
| **Total** | **5,000** | **4,618** | **9,618** |

A stratified split was used to maintain a similar class distribution across the datasets.

---

# 11. Original Image Characteristics

The original dataset contains images with different formats, resolutions, and channel configurations.

### CT Healthy

    Format : PNG
    Size   : 512 × 512
    Mode   : Grayscale

### CT Tumor

    Format : JPEG
    Size   : 640 × 640
    Mode   : RGB

### MRI Healthy

    Format : JPEG
    Size   : 750 × 750
    Mode   : RGB

### MRI Tumor

    Format : JPEG
    Size   : 512 × 512
    Mode   : RGB

Because of these differences, preprocessing is required before training.

---

# 12. Image Preprocessing

The preprocessing pipeline is:

    Original Image
          │
          ▼
    Convert to RGB
          │
          ▼
    Resize to 224 × 224
          │
          ▼
    Data Augmentation
          │
          ▼
    Convert to Tensor
          │
          ▼
    ImageNet Normalization
          │
          ▼
    EfficientNet-B0

---

# 13. RGB Conversion

The original dataset contains both grayscale and RGB images.

EfficientNet-B0 expects a three-channel image.

Therefore, every image is converted to RGB.

    image = image.convert("RGB")

For a grayscale pixel:

    [120]

the RGB representation becomes:

    [120, 120, 120]

This does not create real color information. It only converts the image into the three-channel format required by the model.

---

# 14. Image Resizing

All images are resized to:

    224 × 224 pixels

This creates a standardized input size for EfficientNet-B0.

The tensor representation of one image is:

    [3, 224, 224]

where:

    3   = RGB channels
    224 = height
    224 = width

For a batch size of 32:

    [32, 3, 224, 224]

---

# 15. Data Augmentation

Data augmentation is applied to the training dataset.

The transformations include:

    RandomHorizontalFlip(p=0.5)
    RandomRotation(10)

### Purpose

Data augmentation helps reduce overfitting and allows the model to handle small variations in image orientation and positioning.

Validation and test images are not randomly augmented.

---

# 16. Image Normalization

ImageNet normalization is used because the model starts from ImageNet pretrained weights.

    mean = [
        0.485,
        0.456,
        0.406
    ]

    std = [
        0.229,
        0.224,
        0.225
    ]

---

# 17. DataLoader

The images are loaded using PyTorch `DataLoader`.

Training batch size:

    Batch Size = 32

Example:

    Image batch shape:
    torch.Size([32, 3, 224, 224])

    Labels shape:
    torch.Size([32])

This means:

    32 images
    3 RGB channels
    224 × 224 resolution

---

# 18. Model Architecture

The model used is:

## EfficientNet-B0

EfficientNet-B0 is a convolutional neural network architecture designed to provide a good balance between:

- Accuracy
- Model size
- Computational cost
- Training speed
- Inference speed

---

# 19. Why EfficientNet-B0?

EfficientNet-B0 was selected because it provides strong image classification performance while remaining computationally efficient.

### Advantages

1. Transfer Learning
   - Supports ImageNet pretrained weights.

2. Efficient Architecture
   - Requires fewer computational resources than many larger CNNs.

3. Strong Feature Extraction
   - Learns useful visual representations from medical images.

4. Faster Training
   - Can be efficiently trained using a Tesla T4 GPU.

5. Deployment Friendly
   - Relatively compact and suitable for web deployment.

---

# 20. Transfer Learning

Instead of training EfficientNet-B0 completely from scratch, ImageNet pretrained weights are used.

The pretrained network has already learned general visual features such as:

    Edges
    Textures
    Shapes
    Patterns
    Spatial features

These learned features are adapted to the MRI vs CT classification problem.

### Transfer Learning Pipeline

    ImageNet Dataset
           │
           ▼
    Pretrained EfficientNet-B0
           │
           ▼
    General Visual Features
           │
           ▼
    Fine-Tuning on Brain Dataset
           │
           ▼
    MRI vs CT Classification

---

# 21. Original EfficientNet-B0 Classifier

The original EfficientNet-B0 model is designed for ImageNet classification.

The original classifier contains:

    1280 Features
          │
          ▼
    Dropout
          │
          ▼
    Linear Layer
    1280 → 1000
          │
          ▼
    1000 ImageNet Classes

The 1,000 ImageNet classes are not required for this project.

Therefore, the final classification layer is replaced.

---

# 22. Modified Classification Head

The original classifier:

    1280 → 1000

is replaced with:

    1280 → 2

Implementation:

    model.classifier[1] = nn.Linear(
        in_features=model.classifier[1].in_features,
        out_features=2
    )

The final classifier becomes:

    1280 Features
          │
          ▼
    Dropout
    p = 0.2
          │
          ▼
    Linear Layer
    1280 → 2
          │
          ├─────────────┐
          ▼             ▼
        MRI            CT
         0              1

---

# 23. Complete Architecture

    Input Image
    224 × 224 × 3
           │
           ▼
    ┌────────────────────┐
    │   EfficientNet-B0  │
    │                    │
    │ Feature Extraction │
    │                    │
    │ Convolution Blocks │
    │ MBConv Blocks      │
    │ Squeeze-Excitation │
    │ Global Pooling     │
    └─────────┬──────────┘
              │
              ▼
        1280 Features
              │
              ▼
        Dropout (0.2)
              │
              ▼
        Linear Layer
         1280 → 2
              │
        ┌─────┴─────┐
        ▼           ▼
       MRI          CT
        0            1

---

# 24. EfficientNet Feature Extraction

EfficientNet progressively learns different levels of visual information.

### Low-Level Features

Initial layers learn:

    Edges
    Intensity transitions
    Simple patterns

### Mid-Level Features

Intermediate layers learn:

    Textures
    Structures
    Shapes
    Local spatial patterns

### High-Level Features

Deeper layers learn:

    Complex visual patterns
    Global spatial characteristics
    Modality-specific representations

Final representation:

    Image
      │
      ▼
    Feature Extraction
      │
      ▼
    1280-dimensional representation
      │
      ▼
    Classification Head
      │
      ▼
    MRI / CT

---

# 25. Squeeze-and-Excitation

EfficientNet uses Squeeze-and-Excitation mechanisms within its MBConv blocks.

The purpose is to allow the network to learn which feature channels are more important.

Conceptually:

    Feature Maps
         │
         ▼
    Global Information
         │
         ▼
    Channel Importance
         │
         ▼
    Feature Re-weighting
         │
         ▼
    Improved Representation

This allows the network to focus on more informative feature channels.

---

# 26. MBConv Blocks

EfficientNet-B0 uses Mobile Inverted Bottleneck Convolution (MBConv) blocks.

A simplified MBConv pipeline is:

    Input
      │
      ▼
    Expansion
      │
      ▼
    Depthwise Convolution
      │
      ▼
    Squeeze-and-Excitation
      │
      ▼
    Projection
      │
      ▼
    Output

These blocks provide efficient feature extraction while controlling computational cost.

---

# 27. Global Average Pooling

After convolutional feature extraction, spatial feature maps are reduced using global average pooling.

Conceptually:

    Feature Maps
         │
         ▼
    Global Average Pooling
         │
         ▼
    1280 Feature Values

These 1280 feature values are passed to the classification head.

---

# 28. Classification Head

The final classification head consists of:

    Dropout
       │
       ▼
    Linear Layer
    1280 → 2

Dropout probability:

    0.2

Output classes:

    Output 0 → MRI
    Output 1 → CT

---

# 29. Loss Function

The model uses:

    nn.CrossEntropyLoss()

CrossEntropyLoss is appropriate for classification where the model produces logits for multiple classes.

For each image, the model generates:

    MRI Logit
    CT Logit

The loss function compares the predicted logits with the actual class label.

---

# 30. Optimizer

The optimizer used is:

## AdamW

Configuration:

    Learning Rate = 0.0001
    Weight Decay  = 0.0001

AdamW is an adaptive optimization algorithm that uses decoupled weight decay.

---

# 31. Learning Rate

Initial learning rate:

    0.0001

A relatively small learning rate is appropriate for transfer learning because pretrained weights should not be changed too aggressively.

---

# 32. Learning Rate Scheduler

The model uses:

    ReduceLROnPlateau

Configuration:

    Factor   = 0.5
    Patience = 2

If validation loss stops improving, the learning rate is reduced.

Example:

    0.0001
       ↓
    0.00005

This allows smaller weight updates when the model approaches a good solution.

---

# 33. Training Configuration

| Parameter | Value |
|---|---|
| Architecture | EfficientNet-B0 |
| Pretrained Weights | ImageNet |
| Number of Classes | 2 |
| Input Size | 224 × 224 |
| Image Channels | 3 |
| Batch Size | 32 |
| Epochs | 10 |
| Optimizer | AdamW |
| Learning Rate | 0.0001 |
| Weight Decay | 0.0001 |
| Loss Function | CrossEntropyLoss |
| Scheduler | ReduceLROnPlateau |
| GPU | NVIDIA Tesla T4 |

---

# 34. Training Process

The training process follows:

    Training Image
          │
          ▼
    Preprocessing
          │
          ▼
    EfficientNet-B0
          │
          ▼
    Prediction
          │
          ▼
    CrossEntropyLoss
          │
          ▼
    Backpropagation
          │
          ▼
    AdamW Weight Update
          │
          ▼
    Next Batch

After each epoch:

    Training
       │
       ▼
    Validation
       │
       ▼
    Validation Loss
       │
       ▼
    Learning Rate Scheduler
       │
       ▼
    Save Best Model

---

# 35. Best Model Selection

The model does not simply use the final epoch.

The best-performing checkpoint based on validation performance was saved.

Best checkpoint:

    Epoch = 5

Best validation accuracy:

    99.93%

Model filename:

    BrainScan_Modality_Model.pth

---

# 36. Training Results

### Epoch 1

    Train Accuracy      : 98.87%
    Validation Accuracy : 99.72%

### Epoch 2

    Train Accuracy      : 99.82%
    Validation Accuracy : 99.93%

### Epoch 3

    Train Accuracy      : 99.91%
    Validation Accuracy : 99.93%

### Epoch 4

    Train Accuracy      : 99.94%
    Validation Accuracy : 99.93%

### Epoch 5

    Train Accuracy      : 99.96%
    Validation Accuracy : 99.93%

This was selected as the best checkpoint.

### Epoch 6

    Train Accuracy      : 99.93%
    Validation Accuracy : 99.93%

### Epoch 7

    Train Accuracy      : 99.94%
    Validation Accuracy : 99.93%

### Epoch 8

    Train Accuracy      : 99.97%
    Validation Accuracy : 99.93%

### Epoch 9

    Train Accuracy      : 99.99%
    Validation Accuracy : 99.93%

### Epoch 10

    Train Accuracy      : 100.00%
    Validation Accuracy : 99.93%

---

# 37. Training Time

Training was performed using:

    GPU: NVIDIA Tesla T4

Total training time:

    Approximately 9.49 minutes

---

# 38. Test Dataset

The test dataset was not used during model training.

Test set:

    Total Test Images = 1,443

Distribution:

    MRI = 750
    CT  = 693

The test dataset was used for final model evaluation.

---

# 39. Final Test Results

The model achieved:

| Metric | Result |
|---|---:|
| Accuracy | **99.79%** |
| Precision | **99.71%** |
| Recall | **99.86%** |
| F1 Score | **99.78%** |

---

# 40. Confusion Matrix

The confusion matrix was:

                    Predicted
                   MRI     CT

    Actual MRI     748      2

    Actual CT        1    692

Interpretation:

    True MRI predictions = 748
    MRI predicted as CT  = 2

    True CT predictions  = 692
    CT predicted as MRI  = 1

Total test images:

    1,443

Correct predictions:

    748 + 692 = 1,440

Incorrect predictions:

    2 + 1 = 3

Therefore:

    Accuracy = 1,440 / 1,443
             = 99.79%

---

# 41. Precision

Precision measures how many samples predicted as a particular class were actually that class.

The overall precision achieved was:

    99.71%

A high precision indicates that the model produced very few false-positive modality predictions.

---

# 42. Recall

Recall measures how many actual samples belonging to a class were correctly identified.

The overall recall achieved was:

    99.86%

The high recall indicates that very few MRI/CT images were missed.

---

# 43. F1 Score

F1-score combines precision and recall.

The model achieved:

    F1 Score = 99.78%

This provides a balanced measure of classification performance.

---

# 44. Classification Report

The final classification report was:

    Classification Report:

                  precision    recall  f1-score   support

    MRI              1.00       1.00      1.00       750
    CT               1.00       1.00      1.00       693

    accuracy                              1.00      1443
    macro avg         1.00       1.00      1.00      1443
    weighted avg      1.00       1.00      1.00      1443

The exact overall accuracy calculated from the predictions was:

    99.79%

---

# 45. Single Image Testing

After training, the saved model was tested on individual images.

### MRI Test Image

    Actual     : MRI
    Prediction : MRI
    Confidence : 100.00%

### CT Test Image

    Actual     : CT
    Prediction : CT
    Confidence : 99.99%

These tests confirmed that the saved model can be loaded and used for individual image inference.

---

# 46. Inference Pipeline

The inference pipeline is:

    Input Image
         │
         ▼
    Open Image
         │
         ▼
    Convert to RGB
         │
         ▼
    Resize 224 × 224
         │
         ▼
    Normalize
         │
         ▼
    Add Batch Dimension
         │
         ▼
    EfficientNet-B0
         │
         ▼
    Two Output Logits
         │
         ▼
    Softmax
         │
         ▼
    Highest Probability
         │
         ▼
    MRI / CT

---

# 47. Prediction Function

Example inference implementation:

    def predict_modality(image_path):

        image = Image.open(image_path).convert("RGB")

        image_tensor = val_test_transform(image)

        image_tensor = image_tensor.unsqueeze(0).to(device)

        model.eval()

        with torch.no_grad():

            output = model(image_tensor)

            probabilities = F.softmax(
                output,
                dim=1
            )

            confidence, predicted = torch.max(
                probabilities,
                dim=1
            )

        class_names = {
            0: "MRI",
            1: "CT"
        }

        prediction = class_names[
            predicted.item()
        ]

        confidence = confidence.item() * 100

        return prediction, confidence

---

# 48. Model Loading

The saved model can be loaded using:

    import torch
    from torchvision.models import efficientnet_b0
    import torch.nn as nn

    model = efficientnet_b0(weights=None)

    model.classifier[1] = nn.Linear(
        model.classifier[1].in_features,
        2
    )

    checkpoint = torch.load(
        "BrainScan_Modality_Model.pth",
        map_location="cpu"
    )

    model.load_state_dict(
        checkpoint["model_state_dict"]
    )

    model.eval()

---

# 49. Model File

The final trained model is stored as:

    BrainScan_Modality_Model.pth

Recommended project structure:

    models/
    │
    └── BrainScan_Modality_Model.pth

The checkpoint can contain:

    model_state_dict
    class_mapping
    image_size
    model_name

Class mapping:

    0 → MRI
    1 → CT

---

# 50. Model Input and Output

### Input

    Image
      ↓
    RGB
      ↓
    224 × 224
      ↓
    Tensor [3, 224, 224]

### Output

    Two logits

    Output 0 → MRI
    Output 1 → CT

After applying Softmax:

    MRI Probability
    CT Probability

The class with the highest probability is selected as the prediction.

---

# 51. Example Prediction

Input:

    brain_scan.jpg

Model:

    BrainScan_Modality_Model

Output:

    Prediction : MRI
    Confidence : 99.87%

Another example:

    brain_scan.png

Output:

    Prediction : CT
    Confidence : 99.92%

---

# 52. Complete Model Pipeline

    ┌──────────────────────────────┐
    │          INPUT IMAGE         │
    │      Brain Medical Scan      │
    └──────────────┬───────────────┘
                   │
                   ▼
          Image Validation
                   │
                   ▼
            RGB Conversion
                   │
                   ▼
             Resize 224×224
                   │
                   ▼
             Normalization
                   │
                   ▼
        ┌──────────────────────┐
        │   EfficientNet-B0    │
        │                      │
        │ ImageNet Pretrained  │
        │ Feature Extraction   │
        └──────────┬───────────┘
                   │
                   ▼
             1280 Features
                   │
                   ▼
              Dropout 0.2
                   │
                   ▼
              Linear 1280→2
                   │
             ┌─────┴─────┐
             ▼           ▼
           MRI           CT
            0             1
             │           │
             └─────┬─────┘
                   ▼
             Prediction +
              Confidence

---

# 53. Advantages

### High Classification Performance

The model achieved:

    99.79% Test Accuracy

### Efficient Architecture

EfficientNet-B0 provides a strong balance between accuracy and computational requirements.

### Transfer Learning

ImageNet pretrained weights reduce the need to learn low-level visual features from scratch.

### Fast Training

The complete training process took approximately:

    9.49 minutes

on an NVIDIA Tesla T4 GPU.

### Deployment Friendly

The model can be loaded from a `.pth` file and used for individual image inference.

---

# 54. Limitations

The model has several limitations.

### 1. Modality Classification Only

The model predicts:

    MRI
    or
    CT

It does not diagnose a disease.

### 2. Dataset Dependency

The model was trained on a specific Kaggle dataset.

Performance may differ on images from:

- Other datasets
- Other hospitals
- Different scanners
- Different acquisition protocols
- Different image preprocessing pipelines

### 3. External Generalization

The reported 99.79% accuracy comes from a held-out test set originating from the same dataset distribution.

Independent external validation is required before making claims about clinical generalization.

### 4. Dataset Artifacts

The model may potentially learn dataset-specific characteristics such as:

- Image formatting
- Acquisition characteristics
- Scanner-specific patterns
- Compression patterns
- Background characteristics

rather than relying exclusively on medically meaningful modality characteristics.

### 5. Clinical Use

This model has not undergone clinical validation and must not be used as a standalone diagnostic system.

---

# 55. External Testing

The model can be tested using external MRI and CT images that were not part of the original dataset.

The purpose is to evaluate whether the model generalizes beyond the original dataset.

Example:

    External MRI
         │
         ▼
    BrainScan Modality Model
         │
         ▼
    MRI / CT

Another example:

    External CT
         │
         ▼
    BrainScan Modality Model
         │
         ▼
    MRI / CT

External validation using a sufficiently large independent dataset is recommended for research-quality evaluation.

---

# 56. Model Status

    ┌──────────────────────────────────────┐
    │       BrainScan Modality Model       │
    ├──────────────────────────────────────┤
    │ Dataset                │ COMPLETED   │
    │ Dataset Preparation    │ COMPLETED   │
    │ Labeling               │ COMPLETED   │
    │ Train/Val/Test Split   │ COMPLETED   │
    │ Preprocessing          │ COMPLETED   │
    │ DataLoader             │ COMPLETED   │
    │ Architecture           │ COMPLETED   │
    │ Transfer Learning      │ COMPLETED   │
    │ Training               │ COMPLETED   │
    │ Validation             │ COMPLETED   │
    │ Testing                │ COMPLETED   │
    │ Evaluation             │ COMPLETED   │
    │ Single Image Testing   │ COMPLETED   │
    │ Model Saving           │ COMPLETED   │
    └──────────────────────────────────────┘

---

# 57. Final Model Summary

    Model Name:
    BrainScan Modality Model

    Task:
    MRI vs CT Classification

    Architecture:
    EfficientNet-B0

    Transfer Learning:
    ImageNet

    Dataset:
    9,618 images

    Training Images:
    6,732

    Validation Images:
    1,443

    Test Images:
    1,443

    Input Size:
    224 × 224 × 3

    Batch Size:
    32

    Epochs:
    10

    Optimizer:
    AdamW

    Learning Rate:
    0.0001

    Weight Decay:
    0.0001

    Loss:
    CrossEntropyLoss

    Scheduler:
    ReduceLROnPlateau

    GPU:
    NVIDIA Tesla T4

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

    Model File:
    BrainScan_Modality_Model.pth

---

# 58. Conclusion

The **BrainScan Modality Model** successfully performs automatic classification of brain medical images into MRI and CT categories.

The model uses **EfficientNet-B0 with ImageNet transfer learning**, followed by a custom two-class classification head.

The complete dataset contains:

    9,618 images

including:

    MRI = 5,000
    CT  = 4,618

The final test results are:

    Test Accuracy  : 99.79%
    Precision      : 99.71%
    Recall         : 99.86%
    F1 Score       : 99.78%

The trained model is saved as:

    BrainScan_Modality_Model.pth

The model can now be integrated into a backend application and used to automatically identify whether an uploaded brain scan is an MRI or CT image.

This model will serve as the modality-identification stage of the larger BrainScan AI system.

---

# 59. Disclaimer

This model is developed for **academic and research purposes only**.

It is not a clinically validated medical device.

It should not be used as a substitute for:

- Professional medical diagnosis
- Medical treatment
- Clinical decision-making
- Medical advice

The reported performance represents evaluation on the available dataset and does not establish clinical effectiveness or generalization to all medical imaging environments.

Independent external validation and clinical evaluation would be required before any real-world medical deployment.