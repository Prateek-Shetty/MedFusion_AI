import os
import torch

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models",
    "Model3_V2.pth"
)

print("=" * 60)
print("MODEL 3 CHECKPOINT")
print("=" * 60)

print("Path:", MODEL_PATH)
print("Exists:", os.path.exists(MODEL_PATH))

checkpoint = torch.load(
    MODEL_PATH,
    map_location="cpu",
    weights_only=False
)

print("\nCheckpoint type:")
print(type(checkpoint))

if isinstance(checkpoint, dict):

    print("\nCheckpoint keys:")
    for key in checkpoint.keys():
        print(" ", key)

    if "model_state_dict" in checkpoint:
        state = checkpoint["model_state_dict"]
    elif "state_dict" in checkpoint:
        state = checkpoint["state_dict"]
    else:
        state = checkpoint

    print("\nState dict:")
    print("Number of parameters:", len(state))

    print("\nFirst 20 parameters:")
    for i, (name, value) in enumerate(state.items()):
        if i >= 20:
            break

        print(
            f"{name:50s} "
            f"{tuple(value.shape)}"
        )

else:
    print("\nCheckpoint is not a dictionary.")

print("\n" + "=" * 60)