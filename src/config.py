import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
OUTPUT_DIR = PROJECT_ROOT / "output"
GENERATED_SCENES_DIR = PROJECT_ROOT / "generated_scenes"

# Ensure directories exist
OUTPUT_DIR.mkdir(exist_ok=True)
GENERATED_SCENES_DIR.mkdir(exist_ok=True)

# OpenRouter configuration
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
LLM_MODEL = os.getenv("LLM_MODEL", "xiaomi/mimo-v2-flash")

# Video quality settings
VIDEO_QUALITY = os.getenv("VIDEO_QUALITY", "production_quality")

# Quality flag mapping for Manim CLI
QUALITY_FLAGS = {
    "low_quality": "-ql",
    "medium_quality": "-qm",
    "high_quality": "-qh",
    "production_quality": "-qp",
}
