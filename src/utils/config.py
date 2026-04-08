"""앱 설정 관리"""
from __future__ import annotations
import json
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".memo_app"
CONFIG_FILE = CONFIG_DIR / "config.json"

_DEFAULTS: dict = {
    "theme": "dark",
    "font_size": 14,
    "font_family": "Malgun Gothic",
    "show_line_numbers": True,
    "sidebar_width": 260,
    "window_width": 1100,
    "window_height": 720,
    "sort_by": "updated_at",
    "sort_order": "desc",
    "auto_save_delay": 2000,
    "wrap_lines": True,
    "sidebar_collapsed": False,
}


class AppConfig:
    def __init__(self):
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self._data: dict = dict(_DEFAULTS)
        self.load()

    def load(self) -> None:
        if not CONFIG_FILE.exists():
            return
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                saved = json.load(f)
            self._data.update(saved)
        except Exception as e:
            print(f"[Config] 설정 로드 실패: {e}")

    def save(self) -> None:
        try:
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self._data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[Config] 설정 저장 실패: {e}")

    def get(self, key: str, fallback: Any = None) -> Any:
        return self._data.get(key, _DEFAULTS.get(key, fallback))

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value
        self.save()
