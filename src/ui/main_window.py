"""메인 윈도우"""
from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
import tkinter.filedialog as fd
import tkinter.messagebox as mb
import customtkinter as ctk
from typing import Optional, Dict

from utils.theme import ThemeManager
from utils.config import AppConfig
from storage.store import NoteStore
from models.note import Note
from models.category import SYSTEM_ALL


class TabBar(ctk.CTkFrame):
    """간단한 탭 바"""

    def __init__(self, master, theme: dict, on_select, on_close, **kwargs):
        kwargs.setdefault("fg_color", theme["bg_secondary"])
        kwargs.setdefault("corner_radius", 0)
        kwargs.setdefault("height", 36)
        super().__init__(master, **kwargs)
        self._theme = theme
        self._on_select = on_select
        self._on_close = on_close
        self._tabs: Dict[str, ctk.CTkFrame] = {}
        self._active: Optional[str] = None

    def add_tab(self, note_id: str, title: str):
        if note_id in self._tabs:
            self.set_active(note_id)
            return
        t = self._theme
        frm = ctk.CTkFrame(self, fg_color=t["button_bg"], corner_radius=6,
                           height=28)
        frm.pack(side="left", padx=(4, 0), pady=4)

        lbl = ctk.CTkLabel(frm, text=title[:20], fg_color="transparent",
                           text_color=t["fg"], font=ctk.CTkFont(size=12),
                           width=max(60, min(140, len(title) * 7)))
        lbl.pack(side="left", padx=(8, 2), pady=2)

        _id = note_id
        close_btn = ctk.CTkButton(frm, text="✕", width=18, height=18, corner_radius=9,
                                   fg_color="transparent", hover_color=t["button_hover"],
                                   text_color=t["fg_dim"], font=ctk.CTkFont(size=10),
                                   command=lambda: self._on_close(_id))
        close_btn.pack(side="left", padx=(0, 4), pady=2)

        frm.bind("<Button-1>", lambda e: self._on_select(_id))
        lbl.bind("<Button-1>", lambda e: self._on_select(_id))

        self._tabs[note_id] = frm
        self.set_active(note_id)

    def set_active(self, note_id: str):
        t = self._theme
        for nid, frm in self._tabs.items():
            active = nid == note_id
            frm.configure(fg_color=t["note_item_selected"] if active else t["button_bg"])
        self._active = note_id

    def remove_tab(self, note_id: str):
        if note_id in self._tabs:
            self._tabs[note_id].destroy()
            del self._tabs[note_id]
            self._active = None

    def update_title(self, note_id: str, title: str):
        if note_id in self._tabs:
            frm = self._tabs[note_id]
            for w in frm.winfo_children():
                if isinstance(w, ctk.CTkLabel):
                    w.configure(text=title[:20])
                    break

    def get_tab_ids(self):
        return list(self._tabs.keys())

    def get_active(self):
        return self._active

    def apply_theme(self, theme: dict):
        self._theme = theme
        self.configure(fg_color=theme["bg_secondary"])
        for nid, frm in self._tabs.items():
            active = nid == self._active
            frm.configure(fg_color=theme["note_item_selected"] if active else theme["button_bg"])


class MainWindow(ctk.CTk):
    """메인 윈도우"""

    def __init__(self):
        super().__init__()
        self._config = AppConfig()
        self._store = NoteStore()
        theme_name = self._config.get("theme", "dark")
        ctk.set_appearance_mode(theme_name)
        ctk.set_default_color_theme("blue")

        self._theme = ThemeManager.get_theme(theme_name)
        self._open_editors: Dict[str, "NoteEditor"] = {}
        self._active_note_id: Optional[str] = None

        self._setup_window()
        self._create_layout()
        self._setup_shortcuts()
        self.protocol("WM_DELETE_WINDOW", self._on_close_window)

    # ── Window setup ──────────────────────────────────────────────────────────

    def _setup_window(self):
        self.title("메모장")
        w = self._config.get("window_width", 1100)
        h = self._config.get("window_height", 720)
        self.geometry(f"{w}x{h}")
        self.minsize(700, 500)
        self.configure(fg_color=self._theme["bg"])

    # ── Layout ────────────────────────────────────────────────────────────────

    def _create_layout(self):
        from ui.sidebar import Sidebar
        from ui.toolbar import Toolbar
        from ui.statusbar import StatusBar

        t = self._theme
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Toolbar row
        self._toolbar = Toolbar(
            self, self._config,
            callbacks={
                "bold":                self._editor_bold,
                "italic":              self._editor_italic,
                "underline":           self._editor_underline,
                "font_dec":            self._editor_font_dec,
                "font_inc":            self._editor_font_inc,
                "toggle_line_numbers": self.toggle_line_numbers,
                "toggle_theme":        self.toggle_theme,
                "toggle_preview":      self._toggle_preview,
                "find":                self._editor_find,
            },
        )
        self._toolbar.grid(row=0, column=0, columnspan=2, sticky="ew")

        # Tab bar
        self._tab_bar = TabBar(self, t, self._on_tab_select, self._on_tab_close)
        self._tab_bar.grid(row=1, column=0, columnspan=2, sticky="ew")

        # Sidebar
        sidebar_width = self._config.get("sidebar_width", 260)
        self._sidebar = Sidebar(
            self, self._config, self._store,
            on_note_select=self.open_note,
            on_new_note=self._on_new_note,
            width=sidebar_width,
        )
        self._sidebar.grid(row=2, column=0, sticky="nsew")
        self._sidebar.grid_propagate(False)
        self._sidebar.configure(width=sidebar_width)

        # Resizer
        self._resizer = ctk.CTkFrame(self, width=4, fg_color=t["border"], cursor="sb_h_double_arrow")
        self._resizer.grid(row=2, column=0, sticky="nse")
        self._resizer.bind("<Button-1>", self._on_resize_start)
        self._resizer.bind("<B1-Motion>", self._on_resize_drag)

        # Main editor area
        self._editor_area = ctk.CTkFrame(self, fg_color=t["editor_bg"], corner_radius=0)
        self._editor_area.grid(row=2, column=1, sticky="nsew")
        self._editor_area.grid_rowconfigure(0, weight=1)
        self._editor_area.grid_columnconfigure(0, weight=1)

        # Placeholder when no note open
        self._placeholder = ctk.CTkLabel(
            self._editor_area,
            text="새 노트를 만들거나 노트를 선택하세요\n\nCtrl+N : 새 노트",
            fg_color="transparent", text_color=t["fg_dim"],
            font=ctk.CTkFont(size=16),
            justify="center",
        )
        self._placeholder.grid(row=0, column=0)

        # Status bar
        self._statusbar = StatusBar(self, self._config)
        self._statusbar.grid(row=3, column=0, columnspan=2, sticky="ew")

    # ── Sidebar resize ────────────────────────────────────────────────────────

    def _on_resize_start(self, event):
        self._resize_start_x = event.x_root
        self._resize_start_width = self._sidebar.winfo_width()

    def _on_resize_drag(self, event):
        delta = event.x_root - self._resize_start_x
        new_width = max(180, min(500, self._resize_start_width + delta))
        self._sidebar.configure(width=new_width)
        self._config.set("sidebar_width", new_width)

    # ── Shortcuts ─────────────────────────────────────────────────────────────

    def _setup_shortcuts(self):
        self.bind("<Control-n>", lambda e: self._on_new_note())
        self.bind("<Control-N>", lambda e: self._on_new_note())
        self.bind("<Control-s>", lambda e: self._on_save())
        self.bind("<Control-S>", lambda e: self._on_save_as())
        self.bind("<Control-w>", lambda e: self._on_close_tab())
        self.bind("<Control-W>", lambda e: self._on_close_tab())
        self.bind("<Control-f>", lambda e: self._editor_find())
        self.bind("<Control-h>", lambda e: self._editor_find())
        self.bind("<Control-z>", lambda e: self._editor_undo())
        self.bind("<Control-y>", lambda e: self._editor_redo())
        self.bind("<Control-l>", lambda e: self.toggle_line_numbers())
        self.bind("<Control-comma>", lambda e: self._open_settings())
        self.bind("<Escape>", lambda e: self._editor_hide_find())

    # ── Note operations ───────────────────────────────────────────────────────

    def _on_new_note(self):
        from ui.editor import NoteEditor
        cat_id = self._sidebar.get_current_category()
        if cat_id in ("pinned", "trash"):
            cat_id = SYSTEM_ALL
        note = Note(title="", content="", category_id=cat_id)
        self._store.save_note(note)
        self.open_note(note)
        self._sidebar.refresh()

    def open_note(self, note):
        """노트를 에디터 탭으로 열기"""
        from ui.editor import NoteEditor
        note_id = note.id if isinstance(note, Note) else note
        if isinstance(note, str):
            note = self._store.get_note(note_id)
            if not note:
                return

        self._hide_placeholder()

        if note_id in self._open_editors:
            self._tab_bar.set_active(note_id)
            self._show_editor(note_id)
            return

        editor = NoteEditor(
            self._editor_area, self._config, self._store,
            on_change=lambda *a: self._on_editor_change(note_id, *a),
            fg_color=self._theme["editor_bg"],
        )
        editor.load_note(note)
        editor.set_status_callback(self._on_status_update)
        editor.grid(row=0, column=0, sticky="nsew")

        self._open_editors[note_id] = editor
        self._tab_bar.add_tab(note_id, note.display_title)
        self._show_editor(note_id)
        self._sidebar.select_note(note_id)

    def _show_editor(self, note_id: str):
        for nid, editor in self._open_editors.items():
            if nid == note_id:
                editor.grid()
            else:
                editor.grid_remove()
        self._active_note_id = note_id
        self._tab_bar.set_active(note_id)

    def _hide_placeholder(self):
        self._placeholder.grid_remove()

    def _show_placeholder(self):
        if not self._open_editors:
            self._placeholder.grid(row=0, column=0)

    def _on_editor_change(self, note_id: str, *args):
        editor = self._open_editors.get(note_id)
        if editor:
            note = editor.get_note()
            if note:
                self._tab_bar.update_title(note_id, note.display_title)
                self._sidebar.refresh()
        if args and args[0] == "saved":
            self._statusbar.update_save_status("저장됨")
        elif args and args[0] == "saving":
            self._statusbar.update_save_status("저장 중...")
        elif args and args[0] == "font_size":
            size = args[1] if len(args) > 1 else self._config.get("font_size")
            self._statusbar.update_font_size(size)
            self._toolbar.update_font_size_label(size)

    def _on_status_update(self, line=1, col=1, words=0, chars=0):
        self._statusbar.update_position(line, col)
        self._statusbar.update_counts(words, chars)

    # ── Tab operations ────────────────────────────────────────────────────────

    def _on_tab_select(self, note_id: str):
        self._show_editor(note_id)
        note = self._store.get_note(note_id)
        if note:
            self._sidebar.select_note(note_id)

    def _on_tab_close(self, note_id: str):
        editor = self._open_editors.get(note_id)
        if editor:
            editor.save_now()
            editor.destroy()
            del self._open_editors[note_id]
        self._tab_bar.remove_tab(note_id)
        self._active_note_id = None

        remaining = self._tab_bar.get_tab_ids()
        if remaining:
            self._show_editor(remaining[-1])
        else:
            self._show_placeholder()

    def _on_close_tab(self):
        if self._active_note_id:
            self._on_tab_close(self._active_note_id)

    # ── File operations ───────────────────────────────────────────────────────

    def _on_save(self):
        editor = self._get_active_editor()
        if not editor:
            return
        note = editor.get_note()
        if not note:
            return
        path = fd.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("텍스트 파일", "*.txt"), ("마크다운", "*.md"), ("모든 파일", "*.*")],
            initialfile=f"{note.display_title}.txt",
            title="파일로 저장",
        )
        if path:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(f"# {note.title}\n\n{note.content}")
                self._statusbar.update_save_status("파일 저장됨")
            except Exception as e:
                mb.showerror("저장 오류", f"파일 저장 중 오류가 발생했습니다:\n{e}")

    def _on_save_as(self):
        self._on_save()

    # ── Editor helpers ────────────────────────────────────────────────────────

    def _get_active_editor(self):
        if self._active_note_id:
            return self._open_editors.get(self._active_note_id)
        return None

    def _editor_bold(self):
        e = self._get_active_editor()
        if e: e.insert_bold()

    def _editor_italic(self):
        e = self._get_active_editor()
        if e: e.insert_italic()

    def _editor_underline(self):
        e = self._get_active_editor()
        if e: e.insert_underline()

    def _editor_font_dec(self):
        e = self._get_active_editor()
        if e: e.font_size_dec()

    def _editor_font_inc(self):
        e = self._get_active_editor()
        if e: e.font_size_inc()

    def _editor_find(self):
        e = self._get_active_editor()
        if e: e.show_find_bar()

    def _editor_hide_find(self):
        e = self._get_active_editor()
        if e: e.hide_find_bar()

    def _editor_undo(self):
        e = self._get_active_editor()
        if e:
            e._undo()

    def _editor_redo(self):
        e = self._get_active_editor()
        if e:
            e._redo()

    def _toggle_preview(self):
        pass  # preview mode can be extended

    # ── Theme & settings ──────────────────────────────────────────────────────

    def toggle_theme(self):
        current = self._config.get("theme", "dark")
        new_theme = "light" if current == "dark" else "dark"
        self._config.set("theme", new_theme)
        ctk.set_appearance_mode(new_theme)
        self._theme = ThemeManager.get_theme(new_theme)
        self._apply_theme_to_widgets(self._theme)

    def _apply_theme_to_widgets(self, theme: dict):
        self.configure(fg_color=theme["bg"])
        self._toolbar.apply_theme(theme)
        self._toolbar.update_theme_button(theme["name"])
        self._tab_bar.apply_theme(theme)
        self._sidebar.apply_theme(theme)
        self._statusbar.apply_theme(theme)
        self._editor_area.configure(fg_color=theme["editor_bg"])
        self._placeholder.configure(text_color=theme["fg_dim"])
        for editor in self._open_editors.values():
            editor.apply_theme(theme)

    def toggle_line_numbers(self):
        for editor in self._open_editors.values():
            editor.toggle_line_numbers()

    def refresh_sidebar(self):
        self._sidebar.refresh()

    def _open_settings(self):
        from ui.dialogs import SettingsDialog
        SettingsDialog(self, self._config, callback=self._on_settings_saved)

    def _on_settings_saved(self):
        new_theme = self._config.get("theme", "dark")
        ctk.set_appearance_mode(new_theme)
        self._theme = ThemeManager.get_theme(new_theme)
        self._apply_theme_to_widgets(self._theme)
        font_size = self._config.get("font_size", 14)
        for editor in self._open_editors.values():
            editor.set_font_size(font_size)
        self._statusbar.update_font_size(font_size)
        self._toolbar.update_font_size_label(font_size)

    # ── Window close ──────────────────────────────────────────────────────────

    def _on_close_window(self):
        for editor in self._open_editors.values():
            editor.save_now()
        w = self.winfo_width()
        h = self.winfo_height()
        self._config.set("window_width", w)
        self._config.set("window_height", h)
        self.destroy()
