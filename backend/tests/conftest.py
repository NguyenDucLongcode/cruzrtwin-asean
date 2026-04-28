from pathlib import Path
import sys

# Ensure repo root and AI energy module are importable during tests
REPO_ROOT = Path(__file__).resolve().parents[2]
ENERGY_DIR = REPO_ROOT / "ai-models" / "energy"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

if str(ENERGY_DIR) not in sys.path:
    sys.path.insert(0, str(ENERGY_DIR))
