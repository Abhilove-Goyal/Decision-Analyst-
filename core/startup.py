from core.settings import settings
import shutil
from pathlib import Path

current_ipo_id = None


def clean_startup():
    """
    Resets runtime state safely.
    """
    global current_ipo_id

    current_ipo_id = None

    if settings.docs_dir.exists():
        shutil.rmtree(settings.docs_dir)

    settings.docs_dir.mkdir(parents=True, exist_ok=True)

    print("[STARTUP] Clean environment ready")