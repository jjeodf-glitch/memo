"""
메모장 (Memo) - 가볍고 편한 메모장 앱
Python + tkinter 기반, 외부 의존성 없음
"""

from __future__ import annotations

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import re
import tempfile


# ── 색상 테마 ──────────────────────────────────────────────────────────────────
DARK = {
    "bg": "#1e1e1e",
    "fg": "#d4d4d4",
    "text_bg": "#1e1e1e",
    "text_fg": "#d4d4d4",
    "select_bg": "#264f78",
    "tab_bg": "#2d2d2d",
    "tab_active": "#1e1e1e",
    "tab_fg": "#cccccc",
    "status_bg": "#007acc",
    "status_fg": "#ffffff",
    "menu_bg": "#2d2d2d",
    "menu_fg": "#cccccc",
    "insert": "#aeafad",
    "cursor": "#aeafad",
    "find_bg": "#252526",
    "find_fg": "#cccccc",
    "btn_bg": "#3c3c3c",
    "btn_fg": "#cccccc",
    "entry_bg": "#3c3c3c",
    "entry_fg": "#cccccc",
    "highlight": "#515c6a",
}

LIGHT = {
    "bg": "#f5f5f5",
    "fg": "#1e1e1e",
    "text_bg": "#ffffff",
    "text_fg": "#1e1e1e",
    "select_bg": "#add8e6",
    "tab_bg": "#e0e0e0",
    "tab_active": "#ffffff",
    "tab_fg": "#333333",
    "status_bg": "#0078d4",
    "status_fg": "#ffffff",
    "menu_bg": "#f0f0f0",
    "menu_fg": "#1e1e1e",
    "insert": "#333333",
    "cursor": "#333333",
    "find_bg": "#f0f0f0",
    "find_fg": "#1e1e1e",
    "btn_bg": "#e0e0e0",
    "btn_fg": "#1e1e1e",
    "entry_bg": "#ffffff",
    "entry_fg": "#1e1e1e",
    "highlight": "#b3d7ff",
}


# ── 탭 데이터 ──────────────────────────────────────────────────────────────────
class TabData:
    _counter = 0

    def __init__(self):
        TabData._counter += 1
        self.id = TabData._counter
        self.filepath = None
        self.modified = False
        self.autosave_path = None
        self.text_widget = None

    @property
    def title(self):
        name = os.path.basename(self.filepath) if self.filepath else f"새 메모 {self.id}"
        return ("* " if self.modified else "") + name


# ── 찾기/바꾸기 다이얼로그 ───────────────────────────────────────────────────────
class FindReplaceDialog(tk.Toplevel):
    def __init__(self, parent, app, replace_mode=False):
        super().__init__(parent)
        self.app = app
        self.replace_mode = replace_mode
        self.title("바꾸기" if replace_mode else "찾기")
        self.resizable(False, False)
        self.transient(parent)

        t = app.theme

        self.configure(bg=t["find_bg"])

        pad = {"padx": 6, "pady": 4}

        tk.Label(self, text="찾기:", bg=t["find_bg"], fg=t["find_fg"]).grid(
            row=0, column=0, sticky="e", **pad
        )
        self.find_var = tk.StringVar()
        self.find_entry = tk.Entry(
            self,
            textvariable=self.find_var,
            bg=t["entry_bg"],
            fg=t["entry_fg"],
            insertbackground=t["cursor"],
            width=28,
            relief="flat",
        )
        self.find_entry.grid(row=0, column=1, columnspan=2, sticky="ew", **pad)

        if replace_mode:
            tk.Label(self, text="바꾸기:", bg=t["find_bg"], fg=t["find_fg"]).grid(
                row=1, column=0, sticky="e", **pad
            )
            self.replace_var = tk.StringVar()
            self.replace_entry = tk.Entry(
                self,
                textvariable=self.replace_var,
                bg=t["entry_bg"],
                fg=t["entry_fg"],
                insertbackground=t["cursor"],
                width=28,
                relief="flat",
            )
            self.replace_entry.grid(row=1, column=1, columnspan=2, sticky="ew", **pad)

        self.case_var = tk.BooleanVar(value=False)
        tk.Checkbutton(
            self,
            text="대소문자 구분",
            variable=self.case_var,
            bg=t["find_bg"],
            fg=t["find_fg"],
            selectcolor=t["btn_bg"],
            activebackground=t["find_bg"],
            activeforeground=t["find_fg"],
        ).grid(row=2, column=0, columnspan=3, sticky="w", **pad)

        btn_row = 3
        tk.Button(
            self,
            text="이전",
            command=self.find_prev,
            bg=t["btn_bg"],
            fg=t["btn_fg"],
            relief="flat",
            width=8,
        ).grid(row=btn_row, column=0, **pad)
        tk.Button(
            self,
            text="다음",
            command=self.find_next,
            bg=t["btn_bg"],
            fg=t["btn_fg"],
            relief="flat",
            width=8,
        ).grid(row=btn_row, column=1, **pad)

        if replace_mode:
            tk.Button(
                self,
                text="바꾸기",
                command=self.replace_one,
                bg=t["btn_bg"],
                fg=t["btn_fg"],
                relief="flat",
                width=8,
            ).grid(row=btn_row + 1, column=0, **pad)
            tk.Button(
                self,
                text="모두 바꾸기",
                command=self.replace_all,
                bg=t["btn_bg"],
                fg=t["btn_fg"],
                relief="flat",
                width=10,
            ).grid(row=btn_row + 1, column=1, **pad)

        tk.Button(
            self,
            text="닫기",
            command=self.destroy,
            bg=t["btn_bg"],
            fg=t["btn_fg"],
            relief="flat",
            width=8,
        ).grid(row=btn_row + (2 if replace_mode else 0), column=2, **pad)

        self.find_entry.focus_set()
        self.bind("<Return>", lambda e: self.find_next())
        self.bind("<Escape>", lambda e: self.destroy())

    def _text(self):
        tab = self.app.current_tab()
        return tab.text_widget if tab else None

    def _query(self):
        return self.find_var.get()

    def find_next(self, backwards=False):
        txt = self._text()
        if not txt:
            return
        query = self._query()
        if not query:
            return
        txt.tag_remove("search_hl", "1.0", tk.END)
        case = self.case_var.get()
        nocase = not case
        start = txt.index(tk.INSERT)
        if backwards:
            pos = txt.search(query, start, backwards=True, nocase=nocase, stopindex="1.0")
            if not pos:
                pos = txt.search(query, tk.END, backwards=True, nocase=nocase)
        else:
            pos = txt.search(query, f"{start}+1c", nocase=nocase, stopindex=tk.END)
            if not pos:
                pos = txt.search(query, "1.0", nocase=nocase, stopindex=tk.END)
        if pos:
            end = f"{pos}+{len(query)}c"
            txt.tag_add("search_hl", pos, end)
            txt.tag_config("search_hl", background=self.app.theme["highlight"])
            txt.mark_set(tk.INSERT, pos)
            txt.see(pos)
        else:
            messagebox.showinfo("찾기", f"'{query}'을(를) 찾을 수 없습니다.", parent=self)

    def find_prev(self):
        self.find_next(backwards=True)

    def replace_one(self):
        txt = self._text()
        if not txt:
            return
        query = self._query()
        replace = self.replace_var.get() if self.replace_mode else ""
        if not query:
            return
        case = self.case_var.get()
        nocase = not case
        sel = txt.tag_ranges("search_hl")
        if sel:
            txt.delete(sel[0], sel[1])
            txt.insert(sel[0], replace)
        self.find_next()

    def replace_all(self):
        txt = self._text()
        if not txt:
            return
        query = self._query()
        replace = self.replace_var.get() if self.replace_mode else ""
        if not query:
            return
        case = self.case_var.get()
        nocase = not case
        content = txt.get("1.0", tk.END)
        if nocase:
            new_content, count = re.subn(re.escape(query), replace, content, flags=re.IGNORECASE)
        else:
            count = content.count(query)
            new_content = content.replace(query, replace)
        if count:
            txt.delete("1.0", tk.END)
            txt.insert("1.0", new_content.rstrip("\n"))
            messagebox.showinfo("바꾸기", f"{count}개 교체됨.", parent=self)
        else:
            messagebox.showinfo("바꾸기", f"'{query}'을(를) 찾을 수 없습니다.", parent=self)


# ── 메인 앱 ───────────────────────────────────────────────────────────────────
class MemoApp:
    AUTOSAVE_INTERVAL = 30  # 자동 저장 주기 (초): 변경된 탭을 임시 파일에 저장하는 간격
    FONT_FAMILY = "Consolas"
    FONT_SIZE_DEFAULT = 13
    FONT_SIZE_MIN = 7
    FONT_SIZE_MAX = 40

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("메모장")
        self.root.geometry("860x620")
        self.root.minsize(480, 320)

        self._dark_mode = True
        self._font_size = self.FONT_SIZE_DEFAULT
        self._tabs: list[TabData] = []
        self._autosave_timer = None
        self._find_dialog = None

        self.theme = DARK.copy()
        self._build_ui()
        self._apply_theme()
        self._new_tab()
        self._schedule_autosave()

        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ── UI 구성 ────────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_menu()

        # 탭 노트북
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
        self.notebook.bind("<Button-2>", self._on_tab_middle_click)

        # 상태 바
        self.status_bar = tk.Label(
            self.root,
            text="준비",
            anchor="w",
            padx=8,
            pady=2,
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    def _build_menu(self):
        t = self.theme
        self.menubar = tk.Menu(self.root, tearoff=False)

        # 파일
        file_menu = tk.Menu(self.menubar, tearoff=False)
        file_menu.add_command(label="새로 만들기    Ctrl+N", command=self._new_tab)
        file_menu.add_command(label="열기...         Ctrl+O", command=self._open_file)
        file_menu.add_separator()
        file_menu.add_command(label="저장             Ctrl+S", command=self._save)
        file_menu.add_command(label="다른 이름으로 저장  Ctrl+Shift+S", command=self._save_as)
        file_menu.add_separator()
        file_menu.add_command(label="종료", command=self._on_close)
        self.menubar.add_cascade(label="파일", menu=file_menu)

        # 편집
        edit_menu = tk.Menu(self.menubar, tearoff=False)
        edit_menu.add_command(label="실행취소     Ctrl+Z", command=self._undo)
        edit_menu.add_command(label="다시실행     Ctrl+Y", command=self._redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="찾기          Ctrl+F", command=self._find)
        edit_menu.add_command(label="바꾸기        Ctrl+H", command=self._replace)
        self.menubar.add_cascade(label="편집", menu=edit_menu)

        # 보기
        view_menu = tk.Menu(self.menubar, tearoff=False)
        view_menu.add_command(label="다크 모드 토글", command=self._toggle_dark_mode)
        view_menu.add_separator()
        view_menu.add_command(label="폰트 크게     Ctrl++", command=self._font_bigger)
        view_menu.add_command(label="폰트 작게     Ctrl+-", command=self._font_smaller)
        self.menubar.add_cascade(label="보기", menu=view_menu)

        self.root.config(menu=self.menubar)

        # 단축키
        self.root.bind_all("<Control-n>", lambda e: self._new_tab())
        self.root.bind_all("<Control-N>", lambda e: self._new_tab())
        self.root.bind_all("<Control-o>", lambda e: self._open_file())
        self.root.bind_all("<Control-O>", lambda e: self._open_file())
        self.root.bind_all("<Control-s>", lambda e: self._save())
        self.root.bind_all("<Control-S>", lambda e: self._save())
        self.root.bind_all("<Control-Shift-s>", lambda e: self._save_as())
        self.root.bind_all("<Control-Shift-S>", lambda e: self._save_as())
        self.root.bind_all("<Control-w>", lambda e: self._close_tab())
        self.root.bind_all("<Control-W>", lambda e: self._close_tab())
        self.root.bind_all("<Control-f>", lambda e: self._find())
        self.root.bind_all("<Control-F>", lambda e: self._find())
        self.root.bind_all("<Control-h>", lambda e: self._replace())
        self.root.bind_all("<Control-H>", lambda e: self._replace())
        self.root.bind_all("<Control-z>", lambda e: self._undo())
        self.root.bind_all("<Control-y>", lambda e: self._redo())
        self.root.bind_all("<Control-equal>", lambda e: self._font_bigger())
        self.root.bind_all("<Control-plus>", lambda e: self._font_bigger())
        self.root.bind_all("<Control-minus>", lambda e: self._font_smaller())

    # ── 탭 관리 ────────────────────────────────────────────────────────────────

    def _new_tab(self, filepath=None, content=""):
        tab = TabData()
        tab.filepath = filepath

        frame = tk.Frame(self.notebook)

        txt = tk.Text(
            frame,
            wrap=tk.WORD,
            undo=True,
            maxundo=-1,
            font=(self.FONT_FAMILY, self._font_size),
            relief="flat",
            borderwidth=0,
            padx=8,
            pady=8,
        )
        scrollbar = tk.Scrollbar(frame, orient=tk.VERTICAL, command=txt.yview)
        txt.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        if content:
            txt.insert("1.0", content)
            txt.edit_reset()

        tab.text_widget = txt
        self._tabs.append(tab)

        self.notebook.add(frame, text=tab.title)
        self.notebook.select(frame)

        txt.bind("<<Modified>>", lambda e, t=tab: self._on_modified(t))
        txt.bind("<MouseWheel>", self._on_mousewheel)
        txt.bind("<Button-4>", self._on_mousewheel)
        txt.bind("<Button-5>", self._on_mousewheel)
        txt.bind("<KeyRelease>", lambda e: self._update_status())
        txt.bind("<ButtonRelease>", lambda e: self._update_status())

        self._apply_theme_to_text(txt)
        self._apply_theme_to_frame(frame)
        txt.focus_set()
        self._update_status()
        return tab

    def _close_tab(self, tab_index=None):
        if len(self._tabs) == 0:
            return
        if tab_index is None:
            tab_index = self.notebook.index(self.notebook.select())
        tab = self._tabs[tab_index]
        if tab.modified:
            name = os.path.basename(tab.filepath) if tab.filepath else f"새 메모 {tab.id}"
            answer = messagebox.askyesnocancel(
                "저장 확인",
                f"'{name}'의 변경 사항을 저장하시겠습니까?",
            )
            if answer is None:
                return
            if answer:
                if not self._save_tab(tab):
                    return
        if tab.autosave_path and os.path.exists(tab.autosave_path):
            try:
                os.remove(tab.autosave_path)
            except OSError:
                pass
        self.notebook.forget(tab_index)
        self._tabs.pop(tab_index)
        if not self._tabs:
            self._new_tab()

    def _on_tab_middle_click(self, event):
        try:
            idx = self.notebook.index(f"@{event.x},{event.y}")
            self._close_tab(idx)
        except tk.TclError:
            pass

    def _on_tab_changed(self, event):
        self._update_status()

    def current_tab(self) -> TabData | None:
        try:
            idx = self.notebook.index(self.notebook.select())
            return self._tabs[idx]
        except (tk.TclError, IndexError):
            return None

    def _tab_index(self, tab: TabData):
        return self._tabs.index(tab)

    def _update_tab_title(self, tab: TabData):
        idx = self._tab_index(tab)
        self.notebook.tab(idx, text=tab.title)

    # ── 파일 작업 ──────────────────────────────────────────────────────────────

    def _open_file(self):
        paths = filedialog.askopenfilenames(
            filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")]
        )
        for path in paths:
            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            except UnicodeDecodeError:
                try:
                    with open(path, "r", encoding="cp949") as f:
                        content = f.read()
                except Exception as exc:
                    messagebox.showerror("오류", f"파일을 열 수 없습니다:\n{exc}")
                    continue
            except Exception as exc:
                messagebox.showerror("오류", f"파일을 열 수 없습니다:\n{exc}")
                continue

            # 이미 열린 탭인지 확인
            for tab in self._tabs:
                if tab.filepath == path:
                    self.notebook.select(self._tab_index(tab))
                    return

            # 현재 탭이 비어있고 수정되지 않았으면 재사용
            cur = self.current_tab()
            if cur and not cur.modified and cur.filepath is None:
                cur.filepath = path
                cur.text_widget.delete("1.0", tk.END)
                cur.text_widget.insert("1.0", content)
                cur.text_widget.edit_reset()
                cur.modified = False
                self._update_tab_title(cur)
            else:
                self._new_tab(filepath=path, content=content)

    def _save(self):
        tab = self.current_tab()
        if tab:
            self._save_tab(tab)

    def _save_as(self):
        tab = self.current_tab()
        if tab:
            self._save_tab(tab, force_dialog=True)

    def _save_tab(self, tab: TabData, force_dialog=False) -> bool:
        if force_dialog or tab.filepath is None:
            path = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("텍스트 파일", "*.txt"), ("모든 파일", "*.*")],
                initialfile=f"새 메모 {tab.id}.txt" if tab.filepath is None else None,
            )
            if not path:
                return False
            tab.filepath = path
        try:
            content = tab.text_widget.get("1.0", "end-1c")
            with open(tab.filepath, "w", encoding="utf-8") as f:
                f.write(content)
            tab.modified = False
            self._update_tab_title(tab)
            self._update_status()
            return True
        except Exception as exc:
            messagebox.showerror("오류", f"저장 실패:\n{exc}")
            return False

    # ── 자동 저장 ──────────────────────────────────────────────────────────────

    def _schedule_autosave(self):
        self._autosave_timer = self.root.after(
            self.AUTOSAVE_INTERVAL * 1000, self._autosave
        )

    def _autosave(self):
        for tab in self._tabs:
            if tab.modified:
                try:
                    content = tab.text_widget.get("1.0", "end-1c")
                    if tab.autosave_path is None:
                        fd, path = tempfile.mkstemp(suffix=".txt", prefix="memo_autosave_")
                        os.close(fd)
                        tab.autosave_path = path
                    with open(tab.autosave_path, "w", encoding="utf-8") as f:
                        f.write(content)
                except Exception:
                    pass
        self._schedule_autosave()

    # ── 편집 ──────────────────────────────────────────────────────────────────

    def _on_modified(self, tab: TabData):
        if tab.text_widget.edit_modified():
            tab.modified = True
            self._update_tab_title(tab)
            tab.text_widget.edit_modified(False)
        self._update_status()

    def _undo(self):
        txt = self._get_current_text()
        if txt:
            try:
                txt.edit_undo()
            except tk.TclError:
                pass

    def _redo(self):
        txt = self._get_current_text()
        if txt:
            try:
                txt.edit_redo()
            except tk.TclError:
                pass

    def _find(self):
        txt = self._get_current_text()
        if not txt:
            return
        if self._find_dialog and self._find_dialog.winfo_exists():
            self._find_dialog.focus()
            return
        self._find_dialog = FindReplaceDialog(self.root, self, replace_mode=False)

    def _replace(self):
        txt = self._get_current_text()
        if not txt:
            return
        if self._find_dialog and self._find_dialog.winfo_exists():
            self._find_dialog.destroy()
        self._find_dialog = FindReplaceDialog(self.root, self, replace_mode=True)

    def _get_current_text(self) -> tk.Text | None:
        tab = self.current_tab()
        return tab.text_widget if tab else None

    # ── 폰트 / 마우스 휠 ──────────────────────────────────────────────────────

    def _font_bigger(self):
        if self._font_size < self.FONT_SIZE_MAX:
            self._font_size += 1
            self._update_all_fonts()

    def _font_smaller(self):
        if self._font_size > self.FONT_SIZE_MIN:
            self._font_size -= 1
            self._update_all_fonts()

    def _on_mousewheel(self, event):
        if event.state & 0x4:  # Ctrl held
            if event.num == 4 or event.delta > 0:
                self._font_bigger()
            elif event.num == 5 or event.delta < 0:
                self._font_smaller()
            return "break"

    def _update_all_fonts(self):
        f = (self.FONT_FAMILY, self._font_size)
        for tab in self._tabs:
            tab.text_widget.configure(font=f)
        self._update_status()

    # ── 상태 바 ───────────────────────────────────────────────────────────────

    def _update_status(self):
        tab = self.current_tab()
        if not tab:
            self.status_bar.config(text="준비")
            return
        txt = tab.text_widget
        try:
            cursor = txt.index(tk.INSERT)
            line, col = cursor.split(".")
            content = txt.get("1.0", "end-1c")
            chars = len(content)
            lines = content.count("\n") + 1 if content else 0
            self.status_bar.config(
                text=f"  줄 {line}  열 {int(col)+1}  |  총 {lines}줄  {chars}자  |  폰트 {self._font_size}pt"
            )
        except tk.TclError:
            pass

    # ── 테마 ──────────────────────────────────────────────────────────────────

    def _toggle_dark_mode(self):
        self._dark_mode = not self._dark_mode
        self.theme = DARK.copy() if self._dark_mode else LIGHT.copy()
        self._apply_theme()

    def _apply_theme(self):
        t = self.theme
        self.root.configure(bg=t["bg"])
        self.status_bar.configure(bg=t["status_bg"], fg=t["status_fg"])

        # 메뉴바 스타일 (기본 OS 메뉴라 제한적)
        try:
            self.menubar.configure(bg=t["menu_bg"], fg=t["menu_fg"],
                                   activebackground=t["select_bg"],
                                   activeforeground=t["fg"])
            for i in range(self.menubar.index("end") + 1):
                m = self.menubar.entrycget(i, "menu")
                submenu = self.root.nametowidget(m)
                submenu.configure(bg=t["menu_bg"], fg=t["menu_fg"],
                                  activebackground=t["select_bg"],
                                  activeforeground=t["fg"])
        except Exception:
            pass

        # ttk 노트북 탭 스타일
        style = ttk.Style()
        style.theme_use("default")
        style.configure(
            "TNotebook",
            background=t["tab_bg"],
            borderwidth=0,
        )
        style.configure(
            "TNotebook.Tab",
            background=t["tab_bg"],
            foreground=t["tab_fg"],
            padding=[10, 4],
            borderwidth=0,
        )
        style.map(
            "TNotebook.Tab",
            background=[("selected", t["tab_active"])],
            foreground=[("selected", t["fg"])],
        )

        for tab in self._tabs:
            self._apply_theme_to_text(tab.text_widget)
            self._apply_theme_to_frame(tab.text_widget.master)

    def _apply_theme_to_text(self, txt: tk.Text):
        t = self.theme
        txt.configure(
            bg=t["text_bg"],
            fg=t["text_fg"],
            insertbackground=t["insert"],
            selectbackground=t["select_bg"],
            selectforeground=t["text_fg"],
        )

    def _apply_theme_to_frame(self, frame: tk.Frame):
        t = self.theme
        frame.configure(bg=t["bg"])
        for child in frame.winfo_children():
            cls = child.__class__.__name__
            if cls == "Scrollbar":
                try:
                    child.configure(bg=t["tab_bg"], troughcolor=t["bg"])
                except tk.TclError:
                    pass

    # ── 종료 ──────────────────────────────────────────────────────────────────

    def _on_close(self):
        for tab in list(self._tabs):
            if tab.modified:
                name = os.path.basename(tab.filepath) if tab.filepath else f"새 메모 {tab.id}"
                answer = messagebox.askyesnocancel(
                    "저장 확인",
                    f"'{name}'의 변경 사항을 저장하시겠습니까?",
                )
                if answer is None:
                    return
                if answer:
                    if not self._save_tab(tab):
                        return
        if self._autosave_timer:
            self.root.after_cancel(self._autosave_timer)
        # 임시 파일 정리
        for tab in self._tabs:
            if tab.autosave_path and os.path.exists(tab.autosave_path):
                try:
                    os.remove(tab.autosave_path)
                except OSError:
                    pass
        self.root.destroy()


# ── 진입점 ────────────────────────────────────────────────────────────────────

def main():
    root = tk.Tk()
    app = MemoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
