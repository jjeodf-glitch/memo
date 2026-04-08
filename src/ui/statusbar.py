"""상태 표시줄"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from utils.theme import ThemeManager


class StatusBar(ctk.CTkFrame):
    def __init__(self, master, config, **kwargs):
        self._config = config
        theme = ThemeManager.get_theme(config.get("theme", "dark"))
        kwargs.setdefault("fg_color", theme["status_bg"])
        kwargs.setdefault("height", 28)
        kwargs.setdefault("corner_radius", 0)
        super().__init__(master, **kwargs)

        self._theme = theme
        self._build()

    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        lbl_opts = {"fg_color": "transparent", "text_color": self._theme["fg_dim"],
                    "font": ctk.CTkFont(size=11)}

        self._lbl_pos = ctk.CTkLabel(self, text="줄 1, 열 1", **lbl_opts)
        self._lbl_pos.grid(row=0, column=0, padx=(10, 4), sticky="w")

        sep1 = ctk.CTkLabel(self, text="|", **lbl_opts)
        sep1.grid(row=0, column=1, padx=2)

        self._lbl_words = ctk.CTkLabel(self, text="단어 0개", **lbl_opts)
        self._lbl_words.grid(row=0, column=2, padx=4)

        sep2 = ctk.CTkLabel(self, text="|", **lbl_opts)
        sep2.grid(row=0, column=3, padx=2)

        self._lbl_chars = ctk.CTkLabel(self, text="글자 0개", **lbl_opts)
        self._lbl_chars.grid(row=0, column=4, padx=4)

        sep3 = ctk.CTkLabel(self, text="|", **lbl_opts)
        sep3.grid(row=0, column=5, padx=2)

        self._lbl_font = ctk.CTkLabel(self, text=f"크기 {self._config.get('font_size')}px", **lbl_opts)
        self._lbl_font.grid(row=0, column=6, padx=4)

        sep4 = ctk.CTkLabel(self, text="|", **lbl_opts)
        sep4.grid(row=0, column=7, padx=2)

        self._lbl_save = ctk.CTkLabel(self, text="저장됨", **lbl_opts)
        self._lbl_save.grid(row=0, column=8, padx=(4, 10), sticky="e")

    def update_position(self, line: int, col: int):
        self._lbl_pos.configure(text=f"줄 {line}, 열 {col}")

    def update_counts(self, words: int, chars: int):
        self._lbl_words.configure(text=f"단어 {words}개")
        self._lbl_chars.configure(text=f"글자 {chars}개")

    def update_font_size(self, size: int):
        self._lbl_font.configure(text=f"크기 {size}px")

    def update_save_status(self, status: str):
        self._lbl_save.configure(text=status)

    def apply_theme(self, theme: dict):
        self._theme = theme
        self.configure(fg_color=theme["status_bg"])
        dim = theme["fg_dim"]
        for lbl in (self._lbl_pos, self._lbl_words, self._lbl_chars,
                    self._lbl_font, self._lbl_save):
            lbl.configure(text_color=dim)
