r"""Kullanıcı ayarlarını %APPDATA%\InstantTranslator\config.json içinde saklar."""
import json
import os
from pathlib import Path

APP_NAME = "InstantTranslator"

DEFAULT_CONFIG = {
    "hotkey": "ctrl+shift+t",
    "source_lang": "auto",
    "target_lang": "tr",
    "theme": "dark",
    "language": "auto",  # arayüz dili: "auto" | "en" | "tr"  ("auto" = sistem dili)
}


def _config_dir() -> Path:
    base = os.environ.get("APPDATA") or str(Path.home())
    d = Path(base) / APP_NAME
    d.mkdir(parents=True, exist_ok=True)
    return d


CONFIG_PATH = _config_dir() / "config.json"


class ConfigManager:
    def __init__(self):
        self.data = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        try:
            if CONFIG_PATH.exists():
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                # Sadece bilinen anahtarları al
                self.data.update({k: loaded[k] for k in loaded if k in DEFAULT_CONFIG})
        except Exception as e:
            print(f"[config] load error: {e}")

    def save(self):
        try:
            with open(CONFIG_PATH, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[config] save error: {e}")

    def get(self, key):
        return self.data.get(key, DEFAULT_CONFIG.get(key))

    def set(self, key, value):
        self.data[key] = value
        self.save()
