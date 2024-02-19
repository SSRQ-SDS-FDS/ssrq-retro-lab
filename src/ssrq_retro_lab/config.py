from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
CACHE_DIR = PROJECT_ROOT / "cache"
TEI_OUTPUT_DIR = CACHE_DIR / "tei"
ZG_DATA_ROOT = PROJECT_ROOT / "data" / "ZG"
