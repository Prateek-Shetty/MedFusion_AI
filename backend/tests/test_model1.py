from pathlib import Path
import sys


# Add backend directory to Python path
BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))


from app.models.modality_model import ModalityModel


MODEL_PATH = BACKEND_DIR / "models" / "BrainScan_Modality_Model.pth"
TEST_IMAGE = BACKEND_DIR / "test" / "Brain MRI.jpg"


def main():

    print("=" * 60)
    print("MODEL 1 - MODALITY CLASSIFICATION TEST")
    print("=" * 60)

    model = ModalityModel(MODEL_PATH)

    print("\nModel information:")
    print(model.get_info())

    print("\nTest image:")
    print(TEST_IMAGE)

    result = model.predict(TEST_IMAGE)

    print("\nPrediction:")
    print(f"  Modality   : {result['predicted_modality']}")
    print(f"  Confidence : {result['confidence']:.4f}")

    print("\nProbabilities:")

    for modality, probability in result["probabilities"].items():
        print(f"  {modality}: {probability:.4f}")

    print("=" * 60)


if __name__ == "__main__":
    main()