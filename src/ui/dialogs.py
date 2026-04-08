"""다이얼로그 모음"""
from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import tkinter as tk
import customtkinter as ctk
from utils.theme import ThemeManager


def _center(win, w: int, h: int):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - w) // 2
    y = (sh - h) // 2
    win.geometry(f"{w}x{h}+{x}+{y}")


class FindReplaceDialog(ctk.CTkToplevel):
    """찾기/바꾸기 팝업"""

    def __init__(self, master, text_widget: tk.Text, config, **kwargs):
        super().__init__(master, **kwargs)
        self._text = text_widget
        self._config = config
        theme = ThemeManager.get_theme(config.get("theme", "dark"))
        self._theme = theme

        self.title("찾기 / 바꾸기")
        self.resizable(False, False)
        self.configure(fg_color=theme["bg"])
        _center(self, 440, 230)
        self.grab_set()
        self._build()

    def _build(self):
        t = self._theme
        pad = {"padx": 10, "pady": 4}
        lbl_kw = {"fg_color": "transparent", "text_color": t["fg"],
                  "font": ctk.CTkFont(size=13), "anchor": "w"}
        ent_kw = {"fg_color": t["input_bg"], "text_color": t["input_fg"],
                  "border_color": t["border"], "height": 30, "width": 280}

        ctk.CTkLabel(self, text="찾기:", width=60, **lbl_kw).grid(row=0, column=0, **pad, sticky="w")
        self._find_var = tk.StringVar()
        self._find_entry = ctk.CTkEntry(self, textvariable=self._find_var, **ent_kw)
        self._find_entry.grid(row=0, column=1, **pad)
        self._find_entry.bind("<Return>", lambda e: self._find_next())

        ctk.CTkLabel(self, text="바꾸기:", width=60, **lbl_kw).grid(row=1, column=0, **pad, sticky="w")
        self._replace_var = tk.StringVar()
        ctk.CTkEntry(self, textvariable=self._replace_var, **ent_kw).grid(row=1, column=1, **pad)

        self._regex_var = tk.BooleanVar(value=False)
        ctk.CTkCheckBox(self, text="정규식", variable=self._regex_var,
                        text_color=t["fg"], fg_color=t["accent"],
                        hover_color=t["accent_hover"]).grid(row=2, column=1, padx=10, pady=2, sticky="w")

        btn_kw = {"fg_color": t["button_bg"], "hover_color": t["button_hover"],
                  "text_color": t["fg"], "width": 90, "height": 28, "corner_radius": 6}
        frm = ctk.CTkFrame(self, fg_color="transparent")
        frm.grid(row=3, column=0, columnspan=2, pady=8)

        ctk.CTkButton(frm, text="이전", command=self._find_prev, **btn_kw).grid(row=0, column=0, padx=4)
        ctk.CTkButton(frm, text="다음", command=self._find_next, **btn_kw).grid(row=0, column=1, padx=4)
        ctk.CTkButton(frm, text="바꾸기", command=self._replace_one, **btn_kw).grid(row=0, column=2, padx=4)
        ctk.CTkButton(frm, text="모두 바꾸기", command=self._replace_all,
                      fg_color=t["accent"], hover_color=t["accent_hover"],
                      text_color="#FFFFFF", width=90, height=28, corner_radius=6
                      ).grid(row=0, column=3, padx=4)

        self._status = ctk.CTkLabel(self, text="", fg_color="transparent",
                                    text_color=t["fg_dim"], font=ctk.CTkFont(size=11))
        self._status.grid(row=4, column=0, columnspan=2, pady=(0, 6))

        self._find_entry.focus_set()

    def _pattern(self):
        q = self._find_var.get()
        if not q:
            return None
        if self._regex_var.get():
            try:
                return re.compile(q)
            except re.error as e:
                self._status.configure(text=f"정규식 오류: {e}")
                return None
        return re.compile(re.escape(q), re.IGNORECASE)

    def _find_next(self):
        pat = self._pattern()
        if not pat:
            return
        start = self._text.index(tk.INSERT)
        content = self._text.get("1.0", tk.END)
        lines = content.split("\n")
        cur_line, cur_col = map(int, start.split("."))
        # Search from after cursor
        flat_offset = sum(len(l) + 1 for l in lines[:cur_line - 1]) + cur_col
        m = pat.search(content, flat_offset)
        if not m:
            m = pat.search(content, 0)
        if m:
            self._highlight(m.start(), m.end(), content)
        else:
            self._status.configure(text="찾을 수 없음")

    def _find_prev(self):
        pat = self._pattern()
        if not pat:
            return
        start = self._text.index(tk.INSERT)
        content = self._text.get("1.0", tk.END)
        lines = content.split("\n")
        cur_line, cur_col = map(int, start.split("."))
        flat_offset = sum(len(l) + 1 for l in lines[:cur_line - 1]) + cur_col
        matches = list(pat.finditer(content))
        if not matches:
            self._status.configure(text="찾을 수 없음")
            return
        prev = None
        for m in matches:
            if m.start() < flat_offset - 1:
                prev = m
        if prev is None:
            prev = matches[-1]
        self._highlight(prev.start(), prev.end(), content)

    def _highlight(self, start: int, end: int, content: str):
        self._text.tag_remove("sel", "1.0", tk.END)
        s_idx = self._offset_to_index(start, content)
        e_idx = self._offset_to_index(end, content)
        self._text.tag_add("sel", s_idx, e_idx)
        self._text.mark_set(tk.INSERT, s_idx)
        self._text.see(s_idx)
        self._status.configure(text="")

    def _offset_to_index(self, offset: int, content: str) -> str:
        before = content[:offset]
        line = before.count("\n") + 1
        col = offset - before.rfind("\n") - 1
        return f"{line}.{col}"

    def _replace_one(self):
        pat = self._pattern()
        if not pat:
            return
        try:
            sel_start = self._text.index(tk.SEL_FIRST)
            sel_end = self._text.index(tk.SEL_LAST)
            selected = self._text.get(sel_start, sel_end)
            if pat.fullmatch(selected):
                self._text.delete(sel_start, sel_end)
                self._text.insert(sel_start, self._replace_var.get())
        except tk.TclError:
            pass
        self._find_next()

    def _replace_all(self):
        pat = self._pattern()
        if not pat:
            return
        content = self._text.get("1.0", tk.END)
        new_content, count = pat.subn(self._replace_var.get(), content)
        if count:
            self._text.delete("1.0", tk.END)
            self._text.insert("1.0", new_content)
            self._status.configure(text=f"{count}개 바꿈")
        else:
            self._status.configure(text="찾을 수 없음")


class TagDialog(ctk.CTkToplevel):
    """태그 관리 다이얼로그"""

    PRESET_COLORS = ["#FF6B6B", "#FFD93D", "#6BCB77", "#4D96FF",
                     "#C77DFF", "#FF9F43", "#48DBFB", "#FF6B9D"]

    def __init__(self, master, note, store, config, callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self._note = note
        self._store = store
        self._config = config
        self._callback = callback
        theme = ThemeManager.get_theme(config.get("theme", "dark"))
        self._theme = theme

        self.title("태그 관리")
        self.resizable(False, False)
        self.configure(fg_color=theme["bg"])
        _center(self, 380, 320)
        self.grab_set()
        self._tags = list(note.tags)
        self._build()

    def _build(self):
        t = self._theme
        ctk.CTkLabel(self, text="태그 관리", fg_color="transparent",
                     text_color=t["fg"], font=ctk.CTkFont(size=15, weight="bold")
                     ).pack(pady=(12, 4))

        self._tag_frame = ctk.CTkScrollableFrame(self, fg_color=t["bg_secondary"],
                                                  height=120, corner_radius=8)
        self._tag_frame.pack(fill="x", padx=12, pady=4)
        self._render_tags()

        add_frm = ctk.CTkFrame(self, fg_color="transparent")
        add_frm.pack(fill="x", padx=12, pady=4)
        self._new_tag_var = tk.StringVar()
        ctk.CTkEntry(add_frm, textvariable=self._new_tag_var,
                     placeholder_text="새 태그 입력...",
                     fg_color=t["input_bg"], text_color=t["input_fg"],
                     border_color=t["border"], height=30).pack(side="left", fill="x", expand=True, padx=(0,6))
        ctk.CTkButton(add_frm, text="추가", width=60, height=30,
                      fg_color=t["accent"], hover_color=t["accent_hover"],
                      text_color="#FFFFFF", command=self._add_tag, corner_radius=6
                      ).pack(side="left")

        ctk.CTkButton(self, text="저장", height=34, corner_radius=8,
                      fg_color=t["accent"], hover_color=t["accent_hover"],
                      text_color="#FFFFFF", command=self._save
                      ).pack(pady=(8, 12), padx=12, fill="x")

    def _render_tags(self):
        for w in self._tag_frame.winfo_children():
            w.destroy()
        t = self._theme
        for tag in self._tags:
            frm = ctk.CTkFrame(self._tag_frame, fg_color=t["tag_bg"], corner_radius=12)
            frm.pack(side="left", padx=3, pady=3)
            ctk.CTkLabel(frm, text=tag, fg_color="transparent",
                         text_color=t["tag_fg"], font=ctk.CTkFont(size=12)
                         ).pack(side="left", padx=(8, 2), pady=2)
            _tag = tag
            ctk.CTkButton(frm, text="×", width=20, height=20, corner_radius=10,
                          fg_color="transparent", hover_color=t["button_hover"],
                          text_color=t["fg_dim"], font=ctk.CTkFont(size=11),
                          command=lambda tg=_tag: self._remove_tag(tg)
                          ).pack(side="left", padx=(0, 4))

    def _add_tag(self):
        tag = self._new_tag_var.get().strip()
        if tag and tag not in self._tags:
            self._tags.append(tag)
            self._render_tags()
            self._new_tag_var.set("")

    def _remove_tag(self, tag: str):
        if tag in self._tags:
            self._tags.remove(tag)
            self._render_tags()

    def _save(self):
        self._note.tags = self._tags
        self._note.touch()
        self._store.save_note(self._note)
        if self._callback:
            self._callback()
        self.destroy()


class SettingsDialog(ctk.CTkToplevel):
    """설정 다이얼로그"""

    FONTS = ["Malgun Gothic", "맑은 고딕", "나눔고딕", "Noto Sans KR",
             "Arial", "Courier New", "Consolas", "Segoe UI"]

    def __init__(self, master, config, callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self._config = config
        self._callback = callback
        theme = ThemeManager.get_theme(config.get("theme", "dark"))
        self._theme = theme

        self.title("설정")
        self.resizable(False, False)
        self.configure(fg_color=theme["bg"])
        _center(self, 440, 400)
        self.grab_set()
        self._build()

    def _build(self):
        t = self._theme
        lbl_kw = {"fg_color": "transparent", "text_color": t["fg"],
                  "font": ctk.CTkFont(size=13), "anchor": "w", "width": 140}
        ent_kw = {"fg_color": t["input_bg"], "text_color": t["input_fg"],
                  "border_color": t["border"], "height": 30, "width": 200}

        ctk.CTkLabel(self, text="⚙️  설정", fg_color="transparent",
                     text_color=t["fg"], font=ctk.CTkFont(size=16, weight="bold")
                     ).grid(row=0, column=0, columnspan=2, pady=(14, 8), padx=14, sticky="w")

        # Theme
        ctk.CTkLabel(self, text="테마:", **lbl_kw).grid(row=1, column=0, padx=14, pady=6, sticky="w")
        self._theme_var = ctk.StringVar(value=self._config.get("theme", "dark"))
        ctk.CTkOptionMenu(self, values=["dark", "light"], variable=self._theme_var,
                          fg_color=t["input_bg"], button_color=t["button_bg"],
                          button_hover_color=t["button_hover"], text_color=t["fg"],
                          width=200, height=30
                          ).grid(row=1, column=1, padx=14, pady=6)

        # Font family
        ctk.CTkLabel(self, text="글꼴:", **lbl_kw).grid(row=2, column=0, padx=14, pady=6, sticky="w")
        self._font_var = ctk.StringVar(value=self._config.get("font_family", "Malgun Gothic"))
        ctk.CTkOptionMenu(self, values=self.FONTS, variable=self._font_var,
                          fg_color=t["input_bg"], button_color=t["button_bg"],
                          button_hover_color=t["button_hover"], text_color=t["fg"],
                          width=200, height=30
                          ).grid(row=2, column=1, padx=14, pady=6)

        # Font size
        ctk.CTkLabel(self, text="글자 크기:", **lbl_kw).grid(row=3, column=0, padx=14, pady=6, sticky="w")
        self._size_var = tk.IntVar(value=self._config.get("font_size", 14))
        size_frm = ctk.CTkFrame(self, fg_color="transparent")
        size_frm.grid(row=3, column=1, padx=14, pady=6, sticky="w")
        ctk.CTkButton(size_frm, text="−", width=28, height=28, corner_radius=6,
                      fg_color=t["button_bg"], hover_color=t["button_hover"],
                      text_color=t["fg"],
                      command=lambda: self._size_var.set(max(8, self._size_var.get()-1))
                      ).pack(side="left")
        self._size_lbl = ctk.CTkLabel(size_frm, textvariable=self._size_var,
                                       width=40, fg_color="transparent",
                                       text_color=t["fg"], font=ctk.CTkFont(size=13))
        self._size_lbl.pack(side="left", padx=4)
        ctk.CTkButton(size_frm, text="+", width=28, height=28, corner_radius=6,
                      fg_color=t["button_bg"], hover_color=t["button_hover"],
                      text_color=t["fg"],
                      command=lambda: self._size_var.set(min(36, self._size_var.get()+1))
                      ).pack(side="left")

        # Line numbers
        ctk.CTkLabel(self, text="줄 번호 표시:", **lbl_kw).grid(row=4, column=0, padx=14, pady=6, sticky="w")
        self._lineno_var = tk.BooleanVar(value=self._config.get("show_line_numbers", True))
        ctk.CTkSwitch(self, variable=self._lineno_var, text="",
                      fg_color=t["button_bg"], progress_color=t["accent"]
                      ).grid(row=4, column=1, padx=14, pady=6, sticky="w")

        # Wrap lines
        ctk.CTkLabel(self, text="줄 바꿈:", **lbl_kw).grid(row=5, column=0, padx=14, pady=6, sticky="w")
        self._wrap_var = tk.BooleanVar(value=self._config.get("wrap_lines", True))
        ctk.CTkSwitch(self, variable=self._wrap_var, text="",
                      fg_color=t["button_bg"], progress_color=t["accent"]
                      ).grid(row=5, column=1, padx=14, pady=6, sticky="w")

        # Sidebar width
        ctk.CTkLabel(self, text="사이드바 너비:", **lbl_kw).grid(row=6, column=0, padx=14, pady=6, sticky="w")
        self._sidebar_var = tk.IntVar(value=self._config.get("sidebar_width", 260))
        ctk.CTkEntry(self, textvariable=self._sidebar_var, **ent_kw
                     ).grid(row=6, column=1, padx=14, pady=6)

        # Buttons
        btn_frm = ctk.CTkFrame(self, fg_color="transparent")
        btn_frm.grid(row=7, column=0, columnspan=2, pady=12, padx=14, sticky="ew")
        ctk.CTkButton(btn_frm, text="취소", width=100, height=32, corner_radius=8,
                      fg_color=t["button_bg"], hover_color=t["button_hover"],
                      text_color=t["fg"], command=self.destroy
                      ).pack(side="left", padx=4)
        ctk.CTkButton(btn_frm, text="저장", width=100, height=32, corner_radius=8,
                      fg_color=t["accent"], hover_color=t["accent_hover"],
                      text_color="#FFFFFF", command=self._save
                      ).pack(side="left", padx=4)

    def _save(self):
        self._config.set("theme", self._theme_var.get())
        self._config.set("font_family", self._font_var.get())
        self._config.set("font_size", self._size_var.get())
        self._config.set("show_line_numbers", self._lineno_var.get())
        self._config.set("wrap_lines", self._wrap_var.get())
        self._config.set("sidebar_width", self._sidebar_var.get())
        if self._callback:
            self._callback()
        self.destroy()


class CategoryDialog(ctk.CTkToplevel):
    """카테고리 생성/편집 다이얼로그"""

    PRESET_COLORS = ["#5B8CFF", "#FF6B6B", "#FFD93D", "#6BCB77",
                     "#C77DFF", "#FF9F43", "#48DBFB", "#FF6B9D",
                     "#A0C4FF", "#CAFFBF"]

    def __init__(self, master, config, store, category=None, callback=None, **kwargs):
        super().__init__(master, **kwargs)
        self._config = config
        self._store = store
        self._category = category
        self._callback = callback
        theme = ThemeManager.get_theme(config.get("theme", "dark"))
        self._theme = theme

        self.title("카테고리 편집" if category else "새 카테고리")
        self.resizable(False, False)
        self.configure(fg_color=theme["bg"])
        _center(self, 360, 260)
        self.grab_set()
        self._selected_color = category.color if category else self.PRESET_COLORS[0]
        self._build()

    def _build(self):
        t = self._theme
        ctk.CTkLabel(self, text="카테고리 편집" if self._category else "새 카테고리",
                     fg_color="transparent", text_color=t["fg"],
                     font=ctk.CTkFont(size=15, weight="bold")
                     ).pack(pady=(14, 6), padx=14, anchor="w")

        ctk.CTkLabel(self, text="이름:", fg_color="transparent",
                     text_color=t["fg"], font=ctk.CTkFont(size=13)
                     ).pack(padx=14, anchor="w")
        self._name_var = tk.StringVar(value=self._category.name if self._category else "")
        ctk.CTkEntry(self, textvariable=self._name_var,
                     placeholder_text="카테고리 이름",
                     fg_color=t["input_bg"], text_color=t["input_fg"],
                     border_color=t["border"], height=32
                     ).pack(fill="x", padx=14, pady=(2, 8))

        ctk.CTkLabel(self, text="색상:", fg_color="transparent",
                     text_color=t["fg"], font=ctk.CTkFont(size=13)
                     ).pack(padx=14, anchor="w")

        color_frm = ctk.CTkFrame(self, fg_color="transparent")
        color_frm.pack(fill="x", padx=14, pady=4)
        self._color_btns = {}
        for i, color in enumerate(self.PRESET_COLORS):
            _c = color
            btn = ctk.CTkButton(color_frm, text="", width=26, height=26,
                                corner_radius=13, fg_color=color,
                                hover_color=color, border_width=0,
                                command=lambda c=_c: self._pick_color(c))
            btn.grid(row=0, column=i, padx=2)
            self._color_btns[color] = btn
        self._update_color_selection()

        btn_frm = ctk.CTkFrame(self, fg_color="transparent")
        btn_frm.pack(fill="x", padx=14, pady=12)
        ctk.CTkButton(btn_frm, text="취소", width=100, height=32, corner_radius=8,
                      fg_color=t["button_bg"], hover_color=t["button_hover"],
                      text_color=t["fg"], command=self.destroy
                      ).pack(side="left", padx=4)
        ctk.CTkButton(btn_frm, text="저장", width=100, height=32, corner_radius=8,
                      fg_color=t["accent"], hover_color=t["accent_hover"],
                      text_color="#FFFFFF", command=self._save
                      ).pack(side="left", padx=4)

    def _pick_color(self, color: str):
        self._selected_color = color
        self._update_color_selection()

    def _update_color_selection(self):
        for color, btn in self._color_btns.items():
            border = 3 if color == self._selected_color else 0
            btn.configure(border_width=border, border_color="#FFFFFF")

    def _save(self):
        name = self._name_var.get().strip()
        if not name:
            return
        from models.category import Category
        if self._category:
            self._category.name = name
            self._category.color = self._selected_color
            self._store.save_category(self._category)
        else:
            cat = Category(name=name, color=self._selected_color)
            self._store.save_category(cat)
        if self._callback:
            self._callback()
        self.destroy()
