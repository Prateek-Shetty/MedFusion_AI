import os
import sys

# Add backend root to Python path
BACKEND_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(
    0,
    BACKEND_DIR
)

from app.services.gemini_service import test_gemini


print("=" * 60)
print("GEMINI CONNECTION TEST")
print("=" * 60)

result = test_gemini()

print("\nGemini response:")
print(result)

print("\n" + "=" * 60)
print("GEMINI TEST COMPLETE")
print("=" * 60)