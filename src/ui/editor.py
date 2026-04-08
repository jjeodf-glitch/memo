"""노트 에디터"""
from __future__ import annotations
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import re
import tkinter as tk
import customtkinter as ctk
from typing import Optional, Callable

from utils.theme import ThemeManager


class LineNumbers(tk.Canvas):
    """줄 번호 캔버스"""

    def __init__(self, master, text_widget: tk.Text, theme: dict, **kwargs):
        kwargs.setdefault("width", 44)
        kwargs.setdefault("bd", 0)
        kwargs.setdefault("highlightthickness", 0)
        kwargs.setdefault("bg", theme["sidebar_bg"])
        super().__init__(master, **kwargs)
        self._text = text_widget
        self._theme = theme

    def redraw(self, font):
        self.delete("all")
        i = self._text.index("@0,0")
        while True:
            dline = self._text.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = i.split(".")[0]
            self.create_text(
                2, y, anchor="nw", text=linenum,
                fill=self._theme["fg_dim"], font=font
            )
            i = self._text.index(f"{i}+1line")
            if i == self._text.index(tk.END):
                break

    def apply_theme(self, theme: dict):
        self._theme = theme
        self.configure(bg=theme["sidebar_bg"])


class FindBar(ctk.CTkFrame):
    """에디터 내 인라인 찾기/바꾸기 바"""

    def __init__(self, master, text_widget: tk.Text, theme: dict, **kwargs):
        kwargs.setdefault("fg_color", theme["find_bar_bg"])
        kwargs.setdefault("corner_radius", 0)
        kwargs.setdefault("height", 36)
        super().__init__(master, **kwargs)
        self._text = text_widget
        self._theme = theme
        self._build()

    def _build(self):
        t = self._theme
        ent_kw = {"fg_color": t["input_bg"], "text_color": t["input_fg"],
                  "border_color": t["border"], "height": 26, "corner_radius": 6}
        btn_kw = {"fg_color": t["button_bg"], "hover_color": t["button_hover"],
                  "text_color": t["fg"], "height": 26, "corner_radius": 6,
                  "font": ctk.CTkFont(size=12)}

        self._find_var = tk.StringVar()
        self._find_var.trace_add("write", lambda *a: self._highlight_all())
        ctk.CTkLabel(self, text="찾기:", fg_color="transparent",
                     text_color=t["fg"], font=ctk.CTkFont(size=12)
                     ).pack(side="left", padx=(8, 2))
        ctk.CTkEntry(self, textvariable=self._find_var, width=160, **ent_kw
                     ).pack(side="left", padx=2, pady=4)

        self._replace_var = tk.StringVar()
        ctk.CTkLabel(self, text="바꾸기:", fg_color="transparent",
                     text_color=t["fg"], font=ctk.CTkFont(size=12)
                     ).pack(side="left", padx=(6, 2))
        ctk.CTkEntry(self, textvariable=self._replace_var, width=140, **ent_kw
                     ).pack(side="left", padx=2, pady=4)

        ctk.CTkButton(self, text="이전", width=46, command=self._prev, **btn_kw
                      ).pack(side="left", padx=2)
        ctk.CTkButton(self, text="다음", width=46, command=self._next, **btn_kw
                      ).pack(side="left", padx=2)
        ctk.CTkButton(self, text="바꾸기", width=56, command=self._replace_one, **btn_kw
                      ).pack(side="left", padx=2)
        ctk.CTkButton(self, text="모두", width=44,
                      fg_color=t["accent"], hover_color=t["accent_hover"],
                      text_color="#FFFFFF", height=26, corner_radius=6,
                      font=ctk.CTkFont(size=12), command=self._replace_all
                      ).pack(side="left", padx=2)

        self._result_lbl = ctk.CTkLabel(self, text="", fg_color="transparent",
                                         text_color=t["fg_dim"], font=ctk.CTkFont(size=11))
        self._result_lbl.pack(side="left", padx=6)

        ctk.CTkButton(self, text="✕", width=26, height=26, corner_radius=13,
                      fg_color="transparent", hover_color=t["button_hover"],
                      text_color=t["fg_dim"], font=ctk.CTkFont(size=12),
                      command=self.hide
                      ).pack(side="right", padx=6)

    def show(self):
        self.pack(fill="x", before=self.master.winfo_children()[0]
                  if self.master.winfo_children() else None)
        self.lift()

    def hide(self):
        self.pack_forget()
        self._text.tag_remove("find_match", "1.0", tk.END)
        self._text.focus_set()

    def _pattern(self) -> Optional[re.Pattern]:
        q = self._find_var.get()
        if not q:
            return None
        return re.compile(re.escape(q), re.IGNORECASE)

    def _highlight_all(self):
        self._text.tag_remove("find_match", "1.0", tk.END)
        pat = self._pattern()
        if not pat:
            self._result_lbl.configure(text="")
            return
        content = self._text.get("1.0", tk.END)
        matches = list(pat.finditer(content))
        for m in matches:
            s = self._offset_to_index(m.start(), content)
            e = self._offset_to_index(m.end(), content)
            self._text.tag_add("find_match", s, e)
        self._result_lbl.configure(text=f"{len(matches)}개" if matches else "없음")

    def _next(self):
        pat = self._pattern()
        if not pat:
            return
        start = self._text.index(tk.INSERT)
        content = self._text.get("1.0", tk.END)
        cur_offset = self._index_to_offset(start, content)
        m = pat.search(content, cur_offset + 1)
        if not m:
            m = pat.search(content, 0)
        if m:
            s = self._offset_to_index(m.start(), content)
            e = self._offset_to_index(m.end(), content)
            self._text.tag_remove("sel", "1.0", tk.END)
            self._text.tag_add("sel", s, e)
            self._text.mark_set(tk.INSERT, s)
            self._text.see(s)

    def _prev(self):
        pat = self._pattern()
        if not pat:
            return
        start = self._text.index(tk.INSERT)
        content = self._text.get("1.0", tk.END)
        cur_offset = self._index_to_offset(start, content)
        matches = list(pat.finditer(content, 0, max(0, cur_offset - 1)))
        if not matches:
            matches = list(pat.finditer(content))
        if matches:
            m = matches[-1]
            s = self._offset_to_index(m.start(), content)
            e = self._offset_to_index(m.end(), content)
            self._text.tag_remove("sel", "1.0", tk.END)
            self._text.tag_add("sel", s, e)
            self._text.mark_set(tk.INSERT, s)
            self._text.see(s)

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
        self._next()

    def _replace_all(self):
        pat = self._pattern()
        if not pat:
            return
        content = self._text.get("1.0", tk.END)
        new_content, count = pat.subn(self._replace_var.get(), content)
        if count:
            self._text.delete("1.0", tk.END)
            self._text.insert("1.0", new_content)
            self._result_lbl.configure(text=f"{count}개 바꿈")
        else:
            self._result_lbl.configure(text="없음")

    @staticmethod
    def _offset_to_index(offset: int, content: str) -> str:
        before = content[:offset]
        line = before.count("\n") + 1
        col = offset - (before.rfind("\n") + 1)
        return f"{line}.{col}"

    @staticmethod
    def _index_to_offset(index: str, content: str) -> int:
        line, col = map(int, index.split("."))
        lines = content.split("\n")
        return sum(len(l) + 1 for l in lines[:line - 1]) + col

    def apply_theme(self, theme: dict):
        self._theme = theme
        self.configure(fg_color=theme["find_bar_bg"])


class NoteEditor(ctk.CTkFrame):
    """노트 에디터 (제목 + 태그 + 텍스트)"""

    MD_PATTERNS = [
        (re.compile(r"^(# .+)$", re.MULTILINE),      "md_h1"),
        (re.compile(r"^(## .+)$", re.MULTILINE),     "md_h2"),
        (re.compile(r"^(### .+)$", re.MULTILINE),    "md_h3"),
        (re.compile(r"\*\*(.+?)\*\*"),               "md_bold"),
        (re.compile(r"\*(.+?)\*"),                    "md_italic"),
        (re.compile(r"`(.+?)`"),                      "md_code"),
        (re.compile(r"^(\s*[-*+] .+)$", re.MULTILINE), "md_list"),
        (re.compile(r"^(\s*\d+\. .+)$", re.MULTILINE), "md_list"),
    ]

    def __init__(self, master, config, store, on_change: Optional[Callable] = None, **kwargs):
        self._config = config
        self._store = store
        self._on_change = on_change
        theme = ThemeManager.get_theme(config.get("theme", "dark"))
        self._theme = theme

        kwargs.setdefault("fg_color", theme["editor_bg"])
        kwargs.setdefault("corner_radius", 0)
        super().__init__(master, **kwargs)

        self._note = None
        self._auto_save_id = None
        self._show_line_numbers = config.get("show_line_numbers", True)
        self._font_size = config.get("font_size", 14)
        self._font_family = config.get("font_family", "Malgun Gothic")
        self._undo_stack = []
        self._redo_stack = []
        self._last_content = ""
        self._status_callback = None

        self._build()

    # ── Build ─────────────────────────────────────────────────────────────────

    def _build(self):
        t = self._theme
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Title
        title_frame = ctk.CTkFrame(self, fg_color=t["editor_bg"], corner_radius=0)
        title_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        title_frame.grid_columnconfigure(0, weight=1)

        self._title_var = tk.StringVar()
        self._title_entry = ctk.CTkEntry(
            title_frame, textvariable=self._title_var,
            placeholder_text="제목 없음",
            fg_color=t["editor_bg"], text_color=t["title_fg"],
            border_width=0, border_color=t["editor_bg"],
            font=ctk.CTkFont(family=self._font_family, size=self._font_size + 6, weight="bold"),
            height=44,
        )
        self._title_entry.grid(row=0, column=0, sticky="ew", padx=16, pady=(10, 0))
        self._title_var.trace_add("write", self._on_title_change)

        # Tag row
        self._tag_frame = ctk.CTkFrame(title_frame, fg_color="transparent")
        self._tag_frame.grid(row=1, column=0, sticky="ew", padx=12, pady=(2, 6))

        # Separator
        sep = ctk.CTkFrame(self, height=1, fg_color=t["border"], corner_radius=0)
        sep.grid(row=1, column=0, sticky="ew")

        # Editor area
        editor_container = ctk.CTkFrame(self, fg_color=t["editor_bg"], corner_radius=0)
        editor_container.grid(row=2, column=0, sticky="nsew")
        editor_container.grid_rowconfigure(1, weight=1)
        editor_container.grid_columnconfigure(1, weight=1)

        # Find bar
        self._find_bar = None  # created lazily

        # Line numbers canvas
        self._line_canvas = tk.Canvas(
            editor_container,
            width=44, bd=0, highlightthickness=0,
            bg=t["sidebar_bg"],
        )
        if self._show_line_numbers:
            self._line_canvas.grid(row=1, column=0, sticky="ns")

        # Text widget
        self._editor_font = tk.font.Font(
            family=self._font_family, size=self._font_size
        )
        self._text = tk.Text(
            editor_container,
            wrap=tk.WORD if self._config.get("wrap_lines", True) else tk.NONE,
            font=self._editor_font,
            bg=t["editor_bg"], fg=t["fg"],
            insertbackground=t["fg"],
            selectbackground=t["selection"],
            selectforeground=t["fg"],
            bd=0, padx=12, pady=8,
            undo=True, maxundo=-1,
            spacing1=2, spacing3=2,
        )
        self._text.grid(row=1, column=1, sticky="nsew")

        # Scrollbar
        sb = ctk.CTkScrollbar(editor_container, command=self._text.yview,
                              fg_color=t["scrollbar_bg"],
                              button_color=t["scrollbar_fg"],
                              button_hover_color=t["fg_dim"])
        sb.grid(row=1, column=2, sticky="ns")
        self._text.configure(yscrollcommand=sb.set)

        # Find bar placeholder frame
        self._find_placeholder = ctk.CTkFrame(editor_container, fg_color="transparent", height=0)
        self._find_placeholder.grid(row=0, column=0, columnspan=3, sticky="ew")

        # Setup tags & bindings
        self._setup_md_tags()
        self._setup_bindings()

    def _setup_md_tags(self):
        t = self._theme
        f = self._font_family
        sz = self._font_size
        self._text.tag_configure("md_h1", foreground=t["header1_fg"],
                                  font=tk.font.Font(family=f, size=sz + 6, weight="bold"))
        self._text.tag_configure("md_h2", foreground=t["header2_fg"],
                                  font=tk.font.Font(family=f, size=sz + 4, weight="bold"))
        self._text.tag_configure("md_h3", foreground=t["header2_fg"],
                                  font=tk.font.Font(family=f, size=sz + 2, weight="bold"))
        self._text.tag_configure("md_bold", foreground=t["bold_fg"],
                                  font=tk.font.Font(family=f, size=sz, weight="bold"))
        self._text.tag_configure("md_italic", foreground=t["italic_fg"],
                                  font=tk.font.Font(family=f, size=sz, slant="italic"))
        self._text.tag_configure("md_code", foreground=t["accent"],
                                  background=t["tag_bg"],
                                  font=tk.font.Font(family="Consolas", size=sz - 1))
        self._text.tag_configure("md_list", foreground=t["list_fg"])
        self._text.tag_configure("find_match", background=t["warning"],
                                  foreground=t["bg"])

    def _setup_bindings(self):
        self._text.bind("<KeyRelease>", self._on_key_release)
        self._text.bind("<ButtonRelease-1>", self._on_cursor_move)
        self._text.bind("<Control-z>", lambda e: self._undo())
        self._text.bind("<Control-y>", lambda e: self._redo())
        self._text.bind("<Control-plus>", lambda e: self.font_size_inc())
        self._text.bind("<Control-equal>", lambda e: self.font_size_inc())
        self._text.bind("<Control-minus>", lambda e: self.font_size_dec())
        self._text.bind("<Control-b>", lambda e: self.insert_bold())
        self._text.bind("<Control-i>", lambda e: self.insert_italic())
        self._text.bind("<Control-l>", lambda e: self.toggle_line_numbers())
        self._text.bind("<Control-f>", lambda e: self.show_find_bar())
        self._text.bind("<Control-h>", lambda e: self.show_find_bar())
        self._text.bind("<MouseWheel>", self._on_mousewheel)
        self._text.bind("<Control-MouseWheel>", self._on_ctrl_wheel)
        self._line_canvas.bind("<ButtonPress-1>",
                                lambda e: self._text.focus_set())

    # ── Events ────────────────────────────────────────────────────────────────

    def _on_key_release(self, event=None):
        self._apply_markdown()
        self._update_line_numbers()
        self._update_status()
        self._schedule_autosave()

    def _on_cursor_move(self, event=None):
        self._update_status()
        self._update_line_numbers()

    def _on_title_change(self, *args):
        self._schedule_autosave()

    def _on_mousewheel(self, event):
        pass  # normal scrolling handled by tk

    def _on_ctrl_wheel(self, event):
        if event.delta > 0:
            self.font_size_inc()
        else:
            self.font_size_dec()
        return "break"

    # ── Line Numbers ──────────────────────────────────────────────────────────

    def _update_line_numbers(self):
        if not self._show_line_numbers:
            return
        self._line_canvas.delete("all")
        i = self._text.index("@0,0")
        font = tk.font.Font(family=self._font_family, size=self._font_size - 2)
        while True:
            dline = self._text.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = int(i.split(".")[0])
            self._line_canvas.create_text(
                38, y, anchor="ne", text=str(linenum),
                fill=self._theme["fg_dim"], font=font,
            )
            next_i = self._text.index(f"{i}+1line")
            if next_i == i:
                break
            i = next_i

    # ── Status ────────────────────────────────────────────────────────────────

    def _update_status(self):
        if self._status_callback is None:
            return
        try:
            idx = self._text.index(tk.INSERT)
            line, col = map(int, idx.split("."))
            content = self._text.get("1.0", tk.END)
            words = len(content.split())
            chars = len(content) - 1  # remove trailing newline
            self._status_callback(line=line, col=col + 1, words=words, chars=max(0, chars))
        except Exception:
            pass

    def set_status_callback(self, cb):
        self._status_callback = cb

    # ── Markdown styling ──────────────────────────────────────────────────────

    def _apply_markdown(self):
        content = self._text.get("1.0", tk.END)
        for _, tag in self.MD_PATTERNS:
            self._text.tag_remove(tag, "1.0", tk.END)
        for pat, tag in self.MD_PATTERNS:
            for m in pat.finditer(content):
                s = self._offset_to_index(m.start(), content)
                e = self._offset_to_index(m.end(), content)
                self._text.tag_add(tag, s, e)

    @staticmethod
    def _offset_to_index(offset: int, content: str) -> str:
        before = content[:offset]
        line = before.count("\n") + 1
        col = offset - (before.rfind("\n") + 1)
        return f"{line}.{col}"

    # ── Auto-save ─────────────────────────────────────────────────────────────

    def _schedule_autosave(self):
        if self._auto_save_id:
            self.after_cancel(self._auto_save_id)
        delay = self._config.get("auto_save_delay", 2000)
        self._auto_save_id = self.after(delay, self._autosave)
        if self._on_change:
            self._on_change("saving")

    def _autosave(self):
        self._auto_save_id = None
        if self._note is None:
            return
        title = self._title_var.get().strip()
        content = self._text.get("1.0", tk.END).rstrip("\n")
        if title != self._note.title or content != self._note.content:
            self._note.title = title
            self._note.content = content
            self._note.touch()
            self._store.save_note(self._note)
        if self._on_change:
            self._on_change("saved")

    # ── Public API ────────────────────────────────────────────────────────────

    def load_note(self, note):
        self._note = note
        self._title_var.set(note.title)
        self._text.delete("1.0", tk.END)
        self._text.insert("1.0", note.content)
        self._apply_markdown()
        self._update_line_numbers()
        self._update_status()
        self._render_tags()
        self._text.edit_reset()

    def get_note(self):
        return self._note

    def get_content(self) -> str:
        return self._text.get("1.0", tk.END).rstrip("\n")

    def get_title(self) -> str:
        return self._title_var.get().strip()

    def save_now(self):
        if self._auto_save_id:
            self.after_cancel(self._auto_save_id)
            self._auto_save_id = None
        self._autosave()

    # ── Tags display ──────────────────────────────────────────────────────────

    def _render_tags(self):
        for w in self._tag_frame.winfo_children():
            w.destroy()
        if self._note is None:
            return
        t = self._theme
        for tag in self._note.tags:
            frm = ctk.CTkFrame(self._tag_frame, fg_color=t["tag_bg"], corner_radius=10)
            frm.pack(side="left", padx=2)
            ctk.CTkLabel(frm, text=f"#{tag}", fg_color="transparent",
                         text_color=t["accent"], font=ctk.CTkFont(size=11)
                         ).pack(padx=(6, 6), pady=1)

    def refresh_tags(self):
        self._render_tags()

    # ── Formatting ────────────────────────────────────────────────────────────

    def insert_bold(self):
        self._wrap_selection("**", "**")

    def insert_italic(self):
        self._wrap_selection("*", "*")

    def insert_underline(self):
        # No markdown underline; use HTML-style or just wrap
        self._wrap_selection("<u>", "</u>")

    def _wrap_selection(self, before: str, after: str):
        try:
            sel_start = self._text.index(tk.SEL_FIRST)
            sel_end = self._text.index(tk.SEL_LAST)
            selected = self._text.get(sel_start, sel_end)
            self._text.delete(sel_start, sel_end)
            self._text.insert(sel_start, f"{before}{selected}{after}")
        except tk.TclError:
            pos = self._text.index(tk.INSERT)
            self._text.insert(pos, f"{before}{after}")
            cur_line, cur_col = map(int, pos.split("."))
            self._text.mark_set(tk.INSERT, f"{cur_line}.{cur_col + len(before)}")
        self._apply_markdown()

    # ── Font size ─────────────────────────────────────────────────────────────

    def font_size_inc(self):
        self._font_size = min(36, self._font_size + 1)
        self._update_font()

    def font_size_dec(self):
        self._font_size = max(8, self._font_size - 1)
        self._update_font()

    def set_font_size(self, size: int):
        self._font_size = max(8, min(36, size))
        self._update_font()

    def _update_font(self):
        self._editor_font.configure(size=self._font_size)
        self._title_entry.configure(
            font=ctk.CTkFont(family=self._font_family, size=self._font_size + 6, weight="bold"))
        self._setup_md_tags()
        self._update_line_numbers()
        self._config.set("font_size", self._font_size)
        if self._status_callback:
            self._update_status()
        if self._on_change:
            self._on_change("font_size", self._font_size)

    # ── Line numbers ─────────────────────────────────────────────────────────

    def toggle_line_numbers(self):
        self._show_line_numbers = not self._show_line_numbers
        self._config.set("show_line_numbers", self._show_line_numbers)
        if self._show_line_numbers:
            self._line_canvas.grid()
        else:
            self._line_canvas.grid_remove()
        self._update_line_numbers()

    def set_line_numbers(self, show: bool):
        if show != self._show_line_numbers:
            self.toggle_line_numbers()

    # ── Find bar ─────────────────────────────────────────────────────────────

    def show_find_bar(self):
        if self._find_bar is None:
            self._find_bar = FindBar(
                self._find_placeholder.master,
                self._text, self._theme)
        self._find_bar.grid(row=0, column=0, columnspan=3, sticky="ew")
        self._find_bar.lift()

    def hide_find_bar(self):
        if self._find_bar:
            self._find_bar.grid_remove()

    # ── Undo/Redo ─────────────────────────────────────────────────────────────

    def _undo(self):
        try:
            self._text.edit_undo()
        except tk.TclError:
            pass
        return "break"

    def _redo(self):
        try:
            self._text.edit_redo()
        except tk.TclError:
            pass
        return "break"

    # ── Theme ─────────────────────────────────────────────────────────────────

    def apply_theme(self, theme: dict):
        self._theme = theme
        self.configure(fg_color=theme["editor_bg"])
        self._text.configure(
            bg=theme["editor_bg"], fg=theme["fg"],
            insertbackground=theme["fg"],
            selectbackground=theme["selection"],
        )
        self._line_canvas.configure(bg=theme["sidebar_bg"])
        self._title_entry.configure(
            fg_color=theme["editor_bg"],
            text_color=theme["title_fg"],
        )
        self._setup_md_tags()
        self._render_tags()
        if self._find_bar:
            self._find_bar.apply_theme(theme)

    # ── File drag-drop ────────────────────────────────────────────────────────

    def enable_drop(self):
        try:
            self._text.drop_target_register("DND_Files")  # type: ignore
            self._text.dnd_bind("<<Drop>>", self._on_drop)  # type: ignore
        except Exception:
            pass

    def _on_drop(self, event):
        path = event.data.strip("{}")
        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            self._text.insert(tk.INSERT, content)
        except Exception as e:
            pass
