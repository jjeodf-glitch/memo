"""테마 관리"""
from __future__ import annotations
from typing import Dict


DARK_THEME: Dict[str, str] = {
    "name": "dark",
    "bg": "#1E1E2E",
    "bg_secondary": "#181825",
    "fg": "#CDD6F4",
    "fg_dim": "#6C7086",
    "accent": "#89B4FA",
    "accent_hover": "#B4D0FF",
    "sidebar_bg": "#181825",
    "editor_bg": "#1E1E2E",
    "border": "#313244",
    "button_bg": "#313244",
    "button_hover": "#45475A",
    "selection": "#45475A",
    "note_item_bg": "#24243E",
    "note_item_hover": "#2A2A3E",
    "note_item_selected": "#313160",
    "tag_bg": "#313244",
    "tag_fg": "#CDD6F4",
    "find_bar_bg": "#181825",
    "status_bg": "#11111B",
    "title_fg": "#CDD6F4",
    "preview_fg": "#6C7086",
    "date_fg": "#585B70",
    "pin_color": "#FFD700",
    "header1_fg": "#89B4FA",
    "header2_fg": "#74C7EC",
    "bold_fg": "#CBA6F7",
    "italic_fg": "#94E2D5",
    "list_fg": "#A6E3A1",
    "scrollbar_bg": "#313244",
    "scrollbar_fg": "#585B70",
    "input_bg": "#313244",
    "input_fg": "#CDD6F4",
    "danger": "#F38BA8",
    "success": "#A6E3A1",
    "warning": "#FAB387",
}

LIGHT_THEME: Dict[str, str] = {
    "name": "light",
    "bg": "#EFF1F5",
    "bg_secondary": "#E6E9EF",
    "fg": "#4C4F69",
    "fg_dim": "#9CA0B0",
    "accent": "#1E66F5",
    "accent_hover": "#0858E2",
    "sidebar_bg": "#E6E9EF",
    "editor_bg": "#FFFFFF",
    "border": "#CCE0F5",
    "button_bg": "#DCE0E8",
    "button_hover": "#CCD0DA",
    "selection": "#BCC0CC",
    "note_item_bg": "#E6E9EF",
    "note_item_hover": "#DCE0E8",
    "note_item_selected": "#C6CDE8",
    "tag_bg": "#DCE0E8",
    "tag_fg": "#4C4F69",
    "find_bar_bg": "#E6E9EF",
    "status_bg": "#CCD0DA",
    "title_fg": "#4C4F69",
    "preview_fg": "#8C8FA1",
    "date_fg": "#9CA0B0",
    "pin_color": "#DF8E1D",
    "header1_fg": "#1E66F5",
    "header2_fg": "#179299",
    "bold_fg": "#8839EF",
    "italic_fg": "#04A5E5",
    "list_fg": "#40A02B",
    "scrollbar_bg": "#CCD0DA",
    "scrollbar_fg": "#9CA0B0",
    "input_bg": "#DCE0E8",
    "input_fg": "#4C4F69",
    "danger": "#D20F39",
    "success": "#40A02B",
    "warning": "#FE640B",
}


class ThemeManager:
    _themes: Dict[str, Dict[str, str]] = {
        "dark": DARK_THEME,
        "light": LIGHT_THEME,
    }

    @staticmethod
    def get_theme(name: str) -> Dict[str, str]:
        return ThemeManager._themes.get(name, DARK_THEME)

    @staticmethod
    def get_color(theme_name: str, key: str, fallback: str = "#888888") -> str:
        theme = ThemeManager.get_theme(theme_name)
        return theme.get(key, fallback)
