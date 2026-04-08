"""사이드바 - 검색, 카테고리, 노트 목록"""
from __future__ import annotations
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import tkinter as tk
import customtkinter as ctk
from typing import Optional, Callable, List

from utils.theme import ThemeManager
from models.category import SYSTEM_ALL, SYSTEM_PINNED, SYSTEM_TRASH


class NoteItem(ctk.CTkFrame):
    """사이드바 노트 아이템"""

    def __init__(self, master, note, theme: dict, on_click: Callable, on_right_click: Callable, **kwargs):
        kwargs.setdefault("fg_color", theme["note_item_bg"])
        kwargs.setdefault("corner_radius", 8)
        super().__init__(master, **kwargs)
        self._note = note
        self._theme = theme
        self._on_click = on_click
        self._on_right_click = on_right_click
        self._selected = False
        self._build()
        self._bind_events()

    def _build(self):
        t = self._theme
        self.grid_columnconfigure(0, weight=1)

        top = ctk.CTkFrame(self, fg_color="transparent")
        top.grid(row=0, column=0, sticky="ew", padx=8, pady=(6, 0))
        top.grid_columnconfigure(0, weight=1)

        title_text = ("📌 " if self._note.is_pinned else "") + self._note.display_title
        self._title_lbl = ctk.CTkLabel(
            top, text=title_text, anchor="w",
            fg_color="transparent", text_color=t["fg"],
            font=ctk.CTkFont(size=13, weight="bold"),
            wraplength=0,
        )
        self._title_lbl.grid(row=0, column=0, sticky="ew")

        self._date_lbl = ctk.CTkLabel(
            top, text=self._note.updated_at_local, anchor="e",
            fg_color="transparent", text_color=t["date_fg"],
            font=ctk.CTkFont(size=10),
        )
        self._date_lbl.grid(row=0, column=1, sticky="e", padx=(4, 0))

        preview = self._note.preview or ""
        if preview:
            self._preview_lbl = ctk.CTkLabel(
                self, text=preview, anchor="w",
                fg_color="transparent", text_color=t["preview_fg"],
                font=ctk.CTkFont(size=11),
                wraplength=200,
                justify="left",
            )
            self._preview_lbl.grid(row=1, column=0, sticky="ew", padx=8, pady=(1, 0))

        # Tags
        if self._note.tags:
            tag_frm = ctk.CTkFrame(self, fg_color="transparent")
            tag_frm.grid(row=2, column=0, sticky="ew", padx=8, pady=(2, 0))
            for tag in self._note.tags[:3]:
                frm = ctk.CTkFrame(tag_frm, fg_color=t["tag_bg"], corner_radius=8)
                frm.pack(side="left", padx=(0, 3))
                ctk.CTkLabel(frm, text=f"#{tag}", fg_color="transparent",
                             text_color=t["accent"], font=ctk.CTkFont(size=10)
                             ).pack(padx=5, pady=1)

        ctk.CTkFrame(self, height=1, fg_color=t["border"]).grid(
            row=3, column=0, sticky="ew", padx=0, pady=(6, 0))

    def _bind_events(self):
        widgets = [self, self._title_lbl, self._date_lbl]
        if hasattr(self, "_preview_lbl"):
            widgets.append(self._preview_lbl)
        for w in widgets:
            w.bind("<Button-1>", lambda e: self._on_click(self._note))
            w.bind("<Button-3>", lambda e: self._on_right_click(self._note, e))
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)

    def _on_enter(self, event=None):
        if not self._selected:
            self.configure(fg_color=self._theme["note_item_hover"])

    def _on_leave(self, event=None):
        if not self._selected:
            self.configure(fg_color=self._theme["note_item_bg"])

    def set_selected(self, selected: bool):
        self._selected = selected
        if selected:
            self.configure(fg_color=self._theme["note_item_selected"])
        else:
            self.configure(fg_color=self._theme["note_item_bg"])

    def apply_theme(self, theme: dict):
        self._theme = theme
        self.configure(fg_color=theme["note_item_bg"])


class CategoryItem(ctk.CTkFrame):
    """카테고리 아이템"""

    ICONS = {
        SYSTEM_ALL: "📋",
        SYSTEM_PINNED: "📌",
        SYSTEM_TRASH: "🗑️",
    }

    def __init__(self, master, category, count: int, theme: dict, on_click: Callable, **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        kwargs.setdefault("corner_radius", 6)
        super().__init__(master, **kwargs)
        self._category = category
        self._count = count
        self._theme = theme
        self._on_click = on_click
        self._selected = False
        self._build()

    def _build(self):
        t = self._theme
        self.grid_columnconfigure(1, weight=1)

        icon = self.ICONS.get(self._category.id, "📁")
        ctk.CTkLabel(self, text=icon, fg_color="transparent",
                     font=ctk.CTkFont(size=13), width=22
                     ).grid(row=0, column=0, padx=(6, 2))

        self._name_lbl = ctk.CTkLabel(
            self, text=self._category.name, anchor="w",
            fg_color="transparent", text_color=t["fg"],
            font=ctk.CTkFont(size=13),
        )
        self._name_lbl.grid(row=0, column=1, sticky="ew", pady=4)

        if self._count > 0:
            ctk.CTkLabel(
                self, text=str(self._count), fg_color=t["button_bg"],
                text_color=t["fg_dim"], font=ctk.CTkFont(size=11),
                corner_radius=8, width=24, height=18,
            ).grid(row=0, column=2, padx=6)

        for w in self.winfo_children():
            w.bind("<Button-1>", lambda e: self._on_click(self._category))
            w.bind("<Enter>", self._on_enter)
            w.bind("<Leave>", self._on_leave)
        self.bind("<Button-1>", lambda e: self._on_click(self._category))
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)

    def _on_enter(self, event=None):
        if not self._selected:
            self.configure(fg_color=self._theme["button_hover"])

    def _on_leave(self, event=None):
        if not self._selected:
            self.configure(fg_color="transparent")

    def set_selected(self, selected: bool):
        self._selected = selected
        self.configure(fg_color=self._theme["note_item_selected"] if selected else "transparent")


class Sidebar(ctk.CTkFrame):
    """왼쪽 사이드바"""

    def __init__(self, master, config, store,
                 on_note_select: Optional[Callable] = None,
                 on_new_note: Optional[Callable] = None,
                 **kwargs):
        self._config = config
        self._store = store
        self._on_note_select = on_note_select
        self._on_new_note = on_new_note
        theme = ThemeManager.get_theme(config.get("theme", "dark"))
        self._theme = theme

        kwargs.setdefault("fg_color", theme["sidebar_bg"])
        kwargs.setdefault("corner_radius", 0)
        super().__init__(master, **kwargs)

        self._current_category_id = SYSTEM_ALL
        self._selected_note = None
        self._note_items: List[NoteItem] = []
        self._category_items: List[CategoryItem] = []
        self._search_query = ""
        self._sort_by = config.get("sort_by", "updated_at")
        self._sort_order = config.get("sort_order", "desc")
        self._context_menu: Optional[tk.Menu] = None

        self._build()
        self.refresh()

    def _build(self):
        t = self._theme
        self.grid_rowconfigure(4, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color=t["bg_secondary"], corner_radius=0, height=50)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(header, text="📝 메모장", fg_color="transparent",
                     text_color=t["fg"], font=ctk.CTkFont(size=16, weight="bold")
                     ).grid(row=0, column=0, padx=12, pady=10, sticky="w")

        self._btn_new = ctk.CTkButton(
            header, text="+", width=32, height=30, corner_radius=8,
            fg_color=t["accent"], hover_color=t["accent_hover"],
            text_color="#FFFFFF", font=ctk.CTkFont(size=18),
            command=self._new_note,
        )
        self._btn_new.grid(row=0, column=1, padx=8, pady=8)

        # Search box
        search_frm = ctk.CTkFrame(self, fg_color=t["sidebar_bg"], corner_radius=0)
        search_frm.grid(row=1, column=0, sticky="ew", padx=8, pady=(8, 4))
        search_frm.grid_columnconfigure(0, weight=1)

        self._search_var = tk.StringVar()
        self._search_var.trace_add("write", self._on_search_change)
        self._search_entry = ctk.CTkEntry(
            search_frm, textvariable=self._search_var,
            placeholder_text="🔍 검색...",
            fg_color=t["input_bg"], text_color=t["input_fg"],
            border_color=t["border"], height=32, corner_radius=8,
        )
        self._search_entry.grid(row=0, column=0, sticky="ew")

        # Sort controls
        sort_frm = ctk.CTkFrame(self, fg_color="transparent")
        sort_frm.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, 4))
        ctk.CTkLabel(sort_frm, text="정렬:", fg_color="transparent",
                     text_color=t["fg_dim"], font=ctk.CTkFont(size=11)
                     ).pack(side="left")
        self._sort_var = ctk.StringVar(value=self._sort_by)
        sort_menu = ctk.CTkOptionMenu(
            sort_frm, values=["updated_at", "created_at", "title"],
            variable=self._sort_var,
            fg_color=t["input_bg"], button_color=t["button_bg"],
            button_hover_color=t["button_hover"], text_color=t["fg"],
            width=110, height=24, font=ctk.CTkFont(size=11),
            command=self._on_sort_change,
        )
        sort_menu.pack(side="left", padx=4)
        self._sort_order_var = ctk.StringVar(value="↓" if self._sort_order == "desc" else "↑")
        ctk.CTkButton(
            sort_frm, textvariable=self._sort_order_var, width=26, height=24,
            fg_color=t["button_bg"], hover_color=t["button_hover"],
            text_color=t["fg"], font=ctk.CTkFont(size=11),
            command=self._toggle_sort_order,
        ).pack(side="left")

        # Category list
        self._cat_scroll = ctk.CTkScrollableFrame(
            self, fg_color=t["sidebar_bg"], corner_radius=0, height=160,
            scrollbar_button_color=t["scrollbar_fg"],
            scrollbar_button_hover_color=t["fg_dim"],
        )
        self._cat_scroll.grid(row=3, column=0, sticky="ew", padx=0, pady=0)
        self._cat_scroll.grid_columnconfigure(0, weight=1)

        # Separator
        ctk.CTkFrame(self, height=1, fg_color=t["border"], corner_radius=0
                     ).grid(row=3, column=0, sticky="ew")

        # Note list
        self._note_scroll = ctk.CTkScrollableFrame(
            self, fg_color=t["sidebar_bg"], corner_radius=0,
            scrollbar_button_color=t["scrollbar_fg"],
            scrollbar_button_hover_color=t["fg_dim"],
        )
        self._note_scroll.grid(row=4, column=0, sticky="nsew", padx=0, pady=0)
        self._note_scroll.grid_columnconfigure(0, weight=1)

    # ── Refresh ───────────────────────────────────────────────────────────────

    def refresh(self):
        self._refresh_categories()
        self._refresh_notes()

    def _refresh_categories(self):
        for w in self._cat_scroll.winfo_children():
            w.destroy()
        self._category_items.clear()

        categories = self._store.list_categories(include_system=True)
        # system first
        system_ids = [SYSTEM_ALL, SYSTEM_PINNED, SYSTEM_TRASH]
        system_cats = [c for c in categories if c.id in system_ids]
        user_cats = [c for c in categories if c.id not in system_ids]

        # sort system by predefined order
        system_cats.sort(key=lambda c: system_ids.index(c.id))

        def count_for(cat_id):
            if cat_id == SYSTEM_ALL:
                return len(self._store.list_notes())
            elif cat_id == SYSTEM_PINNED:
                return len(self._store.list_notes(category_id=SYSTEM_PINNED))
            elif cat_id == SYSTEM_TRASH:
                return len(self._store.list_notes(category_id=SYSTEM_TRASH, include_deleted=True))
            else:
                return len(self._store.list_notes(category_id=cat_id))

        for cat in system_cats + user_cats:
            item = CategoryItem(
                self._cat_scroll, cat, count_for(cat.id),
                self._theme, self._on_category_click,
            )
            item.grid(sticky="ew", padx=4, pady=1)
            item.grid_columnconfigure(0, weight=1)
            self._category_items.append(item)
            if cat.id == self._current_category_id:
                item.set_selected(True)

        if user_cats:
            sep = ctk.CTkFrame(self._cat_scroll, height=1, fg_color=self._theme["border"])
            sep.grid(sticky="ew", padx=8, pady=2)

        # Add category button
        ctk.CTkButton(
            self._cat_scroll, text="+ 카테고리 추가", height=28,
            fg_color="transparent", hover_color=self._theme["button_hover"],
            text_color=self._theme["fg_dim"], font=ctk.CTkFont(size=12),
            anchor="w", command=self._new_category,
        ).grid(sticky="ew", padx=4, pady=(2, 4))

    def _refresh_notes(self):
        for w in self._note_scroll.winfo_children():
            w.destroy()
        self._note_items.clear()

        include_deleted = self._current_category_id == SYSTEM_TRASH
        notes = self._store.list_notes(
            category_id=self._current_category_id,
            include_deleted=include_deleted,
            search_query=self._search_query or None,
            sort_by=self._sort_by,
            sort_order=self._sort_order,
        )

        if not notes:
            ctk.CTkLabel(
                self._note_scroll, text="노트가 없습니다.",
                fg_color="transparent", text_color=self._theme["fg_dim"],
                font=ctk.CTkFont(size=12),
            ).pack(pady=20)
            return

        for note in notes:
            item = NoteItem(
                self._note_scroll, note, self._theme,
                on_click=self._on_note_click,
                on_right_click=self._on_note_right_click,
            )
            item.pack(fill="x", padx=4, pady=1)
            self._note_items.append(item)
            if self._selected_note and note.id == self._selected_note.id:
                item.set_selected(True)

    # ── Callbacks ─────────────────────────────────────────────────────────────

    def _on_category_click(self, category):
        self._current_category_id = category.id
        for item in self._category_items:
            item.set_selected(item._category.id == category.id)
        self._refresh_notes()

    def _on_note_click(self, note):
        self._selected_note = note
        for item in self._note_items:
            item.set_selected(item._note.id == note.id)
        if self._on_note_select:
            self._on_note_select(note)

    def _on_note_right_click(self, note, event):
        self._show_context_menu(note, event.x_root, event.y_root)

    def _on_search_change(self, *args):
        self._search_query = self._search_var.get()
        self._refresh_notes()

    def _on_sort_change(self, value):
        self._sort_by = value
        self._config.set("sort_by", value)
        self._refresh_notes()

    def _toggle_sort_order(self):
        self._sort_order = "asc" if self._sort_order == "desc" else "desc"
        self._sort_order_var.set("↑" if self._sort_order == "asc" else "↓")
        self._config.set("sort_order", self._sort_order)
        self._refresh_notes()

    # ── Context menu ──────────────────────────────────────────────────────────

    def _show_context_menu(self, note, x: int, y: int):
        if self._context_menu:
            self._context_menu.destroy()

        t = self._theme
        menu = tk.Menu(self, tearoff=0,
                       bg=t["bg_secondary"], fg=t["fg"],
                       activebackground=t["accent"],
                       activeforeground="#FFFFFF",
                       bd=1, relief="flat")
        self._context_menu = menu

        if note.is_deleted:
            menu.add_command(label="♻️  복원", command=lambda: self._restore_note(note))
            menu.add_command(label="🗑️  영구 삭제", command=lambda: self._purge_note(note))
        else:
            pin_label = "📌  고정 해제" if note.is_pinned else "📌  고정"
            menu.add_command(label=pin_label, command=lambda: self._toggle_pin(note))
            menu.add_separator()
            categories = [c for c in self._store.list_categories() if not c.is_system]
            if categories:
                sub = tk.Menu(menu, tearoff=0,
                              bg=t["bg_secondary"], fg=t["fg"],
                              activebackground=t["accent"],
                              activeforeground="#FFFFFF")
                sub.add_command(label="전체", command=lambda: self._move_note(note, SYSTEM_ALL))
                for cat in categories:
                    _id = cat.id
                    sub.add_command(label=cat.name, command=lambda i=_id: self._move_note(note, i))
                menu.add_cascade(label="📁  카테고리로 이동", menu=sub)
            menu.add_separator()
            menu.add_command(label="🏷️  태그 관리", command=lambda: self._manage_tags(note))
            menu.add_separator()
            menu.add_command(label="🗑️  휴지통으로 이동", command=lambda: self._delete_note(note))

        menu.tk_popup(x, y)

    def _toggle_pin(self, note):
        note.is_pinned = not note.is_pinned
        note.touch()
        self._store.save_note(note)
        self.refresh()

    def _delete_note(self, note):
        self._store.delete_note(note.id)
        if self._selected_note and self._selected_note.id == note.id:
            self._selected_note = None
        self.refresh()

    def _restore_note(self, note):
        self._store.restore_note(note.id)
        self.refresh()

    def _purge_note(self, note):
        import tkinter.messagebox as mb
        if mb.askyesno("영구 삭제", f"'{note.display_title}'을(를) 영구 삭제하시겠습니까?\n이 작업은 되돌릴 수 없습니다."):
            self._store.purge_note(note.id)
            if self._selected_note and self._selected_note.id == note.id:
                self._selected_note = None
            self.refresh()

    def _move_note(self, note, category_id: str):
        note.category_id = category_id
        note.touch()
        self._store.save_note(note)
        self.refresh()

    def _manage_tags(self, note):
        from ui.dialogs import TagDialog
        TagDialog(self, note, self._store, self._config, callback=self.refresh)

    def _new_note(self):
        if self._on_new_note:
            self._on_new_note()

    def _new_category(self):
        from ui.dialogs import CategoryDialog
        CategoryDialog(self, self._config, self._store, callback=self.refresh)

    # ── Public ────────────────────────────────────────────────────────────────

    def select_note(self, note_id: str):
        note = self._store.get_note(note_id)
        if note:
            self._selected_note = note
            for item in self._note_items:
                item.set_selected(item._note.id == note_id)

    def get_current_category(self) -> str:
        return self._current_category_id

    def apply_theme(self, theme: dict):
        self._theme = theme
        self.configure(fg_color=theme["sidebar_bg"])
        self.refresh()
