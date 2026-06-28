"""Validate environment configuration on startup."""
import os
import sys

required = ["CEREBRAS_API_KEY"]
optional = {
    "GEMMA_MODEL": "gemma-4-31b",
    "SIMULATION_ENABLED": "true",
    "APP_NAME": "AEGISFLOW",
    "CEREBRAS_BASE_URL": "https://api.cerebras.ai/v1",
}

print("AEGISFLOW Environment Validation")
print("=" * 40)
all_ok = True
for key in required:
    if os.getenv(key):
        print(f"  [OK] {key}=****{os.getenv(key)[-4:]}")
    else:
        print(f"  [MISSING] {key} is not set")
        all_ok = False

for key, default in optional.items():
    val = os.getenv(key, default)
    print(f"  [OK] {key}={val}")

sys.exit(0 if all_ok else 1)
