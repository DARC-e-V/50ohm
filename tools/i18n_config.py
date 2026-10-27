"""Read the shared locale configuration for Python build tools."""

import json
from pathlib import Path

CONFIG = json.loads((Path(__file__).resolve().parents[1] / "frontend" / "i18n.config.json").read_text())
LOCALES = tuple(CONFIG["locales"])
DEFAULT_LOCALE = CONFIG["defaultLocale"]
