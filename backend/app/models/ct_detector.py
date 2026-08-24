from pathlib import Path

import torch
import torch.nn as nn

from PIL import Image
from torchvision import transforms
from torchvision.models import efficientnet_b0


class CTTumorDetector:
    """
    Model 2B:
    CT Healthy/Tumor classifier.

    Classes:
        0 -> Healthy
        1 -> Tumor
    """

    def __init__(self, model_path: Path):

        self.model_path = Path(model_path)

        # --------------------------------------------------
        # Device
        # --------------------------------------------------

        self.device = torch.device("cpu")

        # --------------------------------------------------
        # Load checkpoint
        # --------------------------------------------------

        checkpoint = torch.load(
            self.model_path,
            map_location=self.device,
            weights_only=False,
        )

        # --------------------------------------------------
        # Read configuration from checkpoint
        # --------------------------------------------------

        self.architecture = checkpoint["architecture"]
        self.task = checkpoint["task"]

        self.class_names = checkpoint["class_names"]

        self.image_size = checkpoint["input_size"]

        self.input_channels = checkpoint[
            "input_channels"
        ]

        self.normalization = checkpoint[
            "normalization"
        ]

        # --------------------------------------------------
        # Create EfficientNet-B0
        # --------------------------------------------------

        self.model = efficientnet_b0(
            weights=None
        )

        num_features = (
            self.model.classifier[1].in_features
        )

        self.model.classifier[1] = nn.Linear(
            num_features,
            len(self.class_names),
        )

        # --------------------------------------------------
        # Load trained weights
        # --------------------------------------------------

        self.model.load_state_dict(
            checkpoint["model_state_dict"]
        )

        self.model.to(
            self.device
        )

        self.model.eval()

        # --------------------------------------------------
        # Image preprocessing
        # --------------------------------------------------

        self.transform = transforms.Compose(
            [
                transforms.Resize(
                    self.image_size
                ),

                transforms.ToTensor(),

                transforms.Normalize(
                    mean=self.normalization["mean"],
                    std=self.normalization["std"],
                ),
            ]
        )

    # ======================================================
    # MODEL INFORMATION
    # ======================================================

    def get_info(self):

        return {
            "model_name": self.architecture,
            "task": self.task,
            "image_size": self.image_size,
            "input_channels": self.input_channels,
            "class_names": self.class_names,
            "normalization": self.normalization,
            "device": str(self.device),
        }

    # ======================================================
    # PREDICTION
    # ======================================================

    def predict(self, image_path: Path):

        image_path = Path(
            image_path
        )

        # --------------------------------------------------
        # Load image
        # --------------------------------------------------

        image = Image.open(
            image_path
        ).convert("RGB")

        # --------------------------------------------------
        # Preprocess
        # --------------------------------------------------

        tensor = self.transform(
            image
        )

        tensor = tensor.unsqueeze(0)

        tensor = tensor.to(
            self.device
        )

        # --------------------------------------------------
        # Inference
        # --------------------------------------------------

        with torch.no_grad():

            output = self.model(
                tensor
            )

            probabilities = torch.softmax(
                output,
                dim=1,
            )

        # --------------------------------------------------
        # Get predicted index
        # --------------------------------------------------

        predicted_index = int(
            torch.argmax(
                probabilities,
                dim=1,
            ).item()
        )

        # --------------------------------------------------
        # Get class name
        #
        # class_names:
        # {
        #     0: "Healthy",
        #     1: "Tumor"
        # }
        # --------------------------------------------------

        predicted_class = self.class_names[
            predicted_index
        ]

        confidence = float(
            probabilities[
                0,
                predicted_index
            ].item()
        )

        # --------------------------------------------------
        # Get probabilities for all classes
        # --------------------------------------------------

        class_probabilities = {}

        for index, probability in enumerate(
            probabilities[0]
        ):

            class_name = self.class_names[
                index
            ]

            class_probabilities[
                class_name
            ] = float(
                probability.item()
            )

        # --------------------------------------------------
        # Return result
        # --------------------------------------------------

        return {
            "predicted_class": predicted_class,
            "confidence": confidence,
            "probabilities": class_probabilities,
        }