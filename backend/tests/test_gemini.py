import os
import sys


# ============================================================
# BACKEND PATH
# ============================================================

BACKEND_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

sys.path.insert(
    0,
    BACKEND_DIR
)


# ============================================================
# GEMINI
# ============================================================

from app.services.gemini_service import gemini_service


print("=" * 60)
print("GEMINI — 3 KEY TEST")
print("=" * 60)

print(
    f"Configured keys: "
    f"{len(gemini_service.api_keys)}"
)

print(
    f"Model: "
    f"{gemini_service.model}"
)

print("-" * 60)


result = gemini_service.test_connection()


print("\nRESULT")
print("-" * 60)

print(
    f"Success    : {result['success']}"
)

print(
    f"Key used   : {result['key_used']}"
)

print(
    f"Model      : {result['model']}"
)

print(
    f"Response   : {result['response']}"
)

print("=" * 60)
print("GEMINI TEST COMPLETE")
print("=" * 60)