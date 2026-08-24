from pathlib import Path
import sys


# Add backend directory to Python path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))


from app.models.mri_detector import MRITumorDetector


MODEL_PATH = (
    BACKEND_DIR
    / "models"
    / "BrainTumor_MRI_Detector_Best.pth"
)

TEST_IMAGE = (
    BACKEND_DIR
    / "test"
    / "Brain MRI.jpg"
)


def main():

    print("=" * 60)
    print("MODEL 2A - MRI TUMOR DETECTION TEST")
    print("=" * 60)

    model = MRITumorDetector(
        MODEL_PATH
    )

    print("\nModel information:")
    print(model.get_info())

    print("\nTest image:")
    print(TEST_IMAGE)

    result = model.predict(
        TEST_IMAGE
    )

    print("\nPrediction:")
    print(
        f"  Class      : {result['predicted_class']}"
    )

    print(
        f"  Confidence : {result['confidence']:.4f}"
    )

    print("\nProbabilities:")

    for class_name, probability in result[
        "probabilities"
    ].items():

        print(
            f"  {class_name}: {probability:.4f}"
        )

    print("=" * 60)


if __name__ == "__main__":
    main()