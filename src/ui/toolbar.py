"""툴바"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import customtkinter as ctk
from utils.theme import ThemeManager


class Toolbar(ctk.CTkFrame):
    def __init__(self, master, config, callbacks: dict, **kwargs):
        self._config = config
        theme = ThemeManager.get_theme(config.get("theme", "dark"))
        kwargs.setdefault("fg_color", theme["bg_secondary"])
        kwargs.setdefault("height", 42)
        kwargs.setdefault("corner_radius", 0)
        super().__init__(master, **kwargs)

        self._theme = theme
        self._callbacks = callbacks
        self._font_size_var = config.get("font_size", 14)
        self._build()

    def _btn(self, text, cmd, width=36, tooltip=None, toggle=False):
        t = self._theme
        b = ctk.CTkButton(
            self, text=text, command=cmd, width=width, height=28,
            fg_color=t["button_bg"], hover_color=t["button_hover"],
            text_color=t["fg"], corner_radius=6,
            font=ctk.CTkFont(size=13),
        )
        return b

    def _build(self):
        self.grid_columnconfigure(20, weight=1)
        pad = {"padx": 2, "pady": 6}

        cb = self._callbacks

        col = 0
        ctk.CTkLabel(self, text="서식:", fg_color="transparent",
                     text_color=self._theme["fg_dim"],
                     font=ctk.CTkFont(size=12)).grid(row=0, column=col, padx=(8,2), pady=6)
        col += 1

        self._btn_bold = self._btn("B", cb.get("bold", lambda: None), width=32)
        self._btn_bold.configure(font=ctk.CTkFont(size=13, weight="bold"))
        self._btn_bold.grid(row=0, column=col, **pad); col += 1

        self._btn_italic = self._btn("I", cb.get("italic", lambda: None), width=32)
        self._btn_italic.configure(font=ctk.CTkFont(size=13))
        self._btn_italic.grid(row=0, column=col, **pad); col += 1

        self._btn_underline = self._btn("U", cb.get("underline", lambda: None), width=32)
        self._btn_underline.configure(font=ctk.CTkFont(size=13))
        self._btn_underline.grid(row=0, column=col, **pad); col += 1

        # separator
        ctk.CTkFrame(self, width=1, height=24, fg_color=self._theme["border"]
                     ).grid(row=0, column=col, padx=6, pady=6); col += 1

        ctk.CTkLabel(self, text="크기:", fg_color="transparent",
                     text_color=self._theme["fg_dim"],
                     font=ctk.CTkFont(size=12)).grid(row=0, column=col, padx=(2,2), pady=6)
        col += 1

        self._btn_font_dec = self._btn("−", cb.get("font_dec", lambda: None), width=28)
        self._btn_font_dec.grid(row=0, column=col, **pad); col += 1

        self._font_size_label = ctk.CTkLabel(
            self, text=str(self._font_size_var), width=32, fg_color="transparent",
            text_color=self._theme["fg"], font=ctk.CTkFont(size=13, weight="bold"))
        self._font_size_label.grid(row=0, column=col, padx=2, pady=6); col += 1

        self._btn_font_inc = self._btn("+", cb.get("font_inc", lambda: None), width=28)
        self._btn_font_inc.grid(row=0, column=col, **pad); col += 1

        # separator
        ctk.CTkFrame(self, width=1, height=24, fg_color=self._theme["border"]
                     ).grid(row=0, column=col, padx=6, pady=6); col += 1

        self._btn_lineno = self._btn("줄번호", cb.get("toggle_line_numbers", lambda: None), width=52)
        self._btn_lineno.grid(row=0, column=col, **pad); col += 1

        self._btn_theme = self._btn("🌙" if self._config.get("theme") == "dark" else "☀️",
                                    cb.get("toggle_theme", lambda: None), width=36)
        self._btn_theme.grid(row=0, column=col, **pad); col += 1

        self._btn_preview = self._btn("미리보기", cb.get("toggle_preview", lambda: None), width=60)
        self._btn_preview.grid(row=0, column=col, **pad); col += 1

        # spacer
        col += 1

        self._btn_find = self._btn("🔍 찾기", cb.get("find", lambda: None), width=68)
        self._btn_find.grid(row=0, column=col, padx=(2, 8), pady=6); col += 1

    def update_font_size_label(self, size: int):
        self._font_size_label.configure(text=str(size))

    def update_theme_button(self, theme_name: str):
        icon = "🌙" if theme_name == "dark" else "☀️"
        self._btn_theme.configure(text=icon)

    def apply_theme(self, theme: dict):
        self._theme = theme
        self.configure(fg_color=theme["bg_secondary"])
        for btn in (self._btn_bold, self._btn_italic, self._btn_underline,
                    self._btn_font_dec, self._btn_font_inc, self._btn_lineno,
                    self._btn_theme, self._btn_preview, self._btn_find):
            btn.configure(fg_color=theme["button_bg"], hover_color=theme["button_hover"],
                          text_color=theme["fg"])
        self._font_size_label.configure(text_color=theme["fg"])
