import os
import sys
from PIL import Image

sys.path.insert(
    0,
    os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)

from app.models.model3a_classifier import predict_model3a


IMAGE_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "test",
    "g2.jpg"
)


if not os.path.exists(IMAGE_PATH):
    print(f"Image not found: {IMAGE_PATH}")
    sys.exit(1)


image = Image.open(IMAGE_PATH)

result = predict_model3a(image)

print("\nModel 3A")
print("-" * 30)
print(f"Tumor present : {result['tumor_present']}")
print(f"Tumor type    : {result['tumor_type']}")
print(f"Confidence    : {result['confidence']:.2%}")

print("\nProbabilities:")
for name, probability in result["probabilities"].items():
    print(f"{name:12}: {probability:.2%}")