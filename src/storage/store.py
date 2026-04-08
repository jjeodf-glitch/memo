"""JSON 기반 노트 저장소"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from typing import List, Optional

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.note import Note
from models.category import Category, SYSTEM_ALL, SYSTEM_PINNED, SYSTEM_TRASH


DATA_DIR = Path.home() / ".memo_app"
DATA_FILE = DATA_DIR / "data.json"


class NoteStore:
    def __init__(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        self._notes: dict[str, Note] = {}
        self._categories: dict[str, Category] = {}
        self._load()
        self._ensure_system_categories()

    # ── Internal ──────────────────────────────────────────────────────────────

    def _load(self) -> None:
        if not DATA_FILE.exists():
            self._notes = {}
            self._categories = {}
            return
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for nd in data.get("notes", []):
                n = Note.from_dict(nd)
                self._notes[n.id] = n
            for cd in data.get("categories", []):
                c = Category.from_dict(cd)
                self._categories[c.id] = c
        except Exception as e:
            print(f"[Store] 데이터 로드 실패: {e}")
            self._notes = {}
            self._categories = {}

    def _save(self) -> None:
        try:
            data = {
                "notes": [n.to_dict() for n in self._notes.values()],
                "categories": [c.to_dict() for c in self._categories.values()],
            }
            tmp = DATA_FILE.with_suffix(".tmp")
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            tmp.replace(DATA_FILE)
        except Exception as e:
            print(f"[Store] 데이터 저장 실패: {e}")

    def _ensure_system_categories(self) -> None:
        for cat in Category.make_system_categories():
            if cat.id not in self._categories:
                self._categories[cat.id] = cat

    # ── Notes ─────────────────────────────────────────────────────────────────

    def save_note(self, note: Note) -> None:
        self._notes[note.id] = note
        self._save()

    def get_note(self, note_id: str) -> Optional[Note]:
        return self._notes.get(note_id)

    def list_notes(
        self,
        category_id: Optional[str] = None,
        include_deleted: bool = False,
        search_query: Optional[str] = None,
        sort_by: str = "updated_at",
        sort_order: str = "desc",
    ) -> List[Note]:
        notes = list(self._notes.values())

        # filter deleted
        if category_id == SYSTEM_TRASH:
            notes = [n for n in notes if n.is_deleted]
        elif not include_deleted:
            notes = [n for n in notes if not n.is_deleted]

        # filter by category
        if category_id and category_id not in (SYSTEM_ALL, SYSTEM_TRASH):
            if category_id == SYSTEM_PINNED:
                notes = [n for n in notes if n.is_pinned and not n.is_deleted]
            else:
                notes = [n for n in notes if n.category_id == category_id]

        # search filter
        if search_query:
            q = search_query.lower()
            notes = [
                n for n in notes
                if q in n.title.lower() or q in n.content.lower()
            ]

        # sort
        reverse = sort_order == "desc"
        if sort_by == "title":
            notes.sort(key=lambda n: n.display_title.lower(), reverse=reverse)
        elif sort_by == "created_at":
            notes.sort(key=lambda n: n.created_at, reverse=reverse)
        else:
            notes.sort(key=lambda n: n.updated_at, reverse=reverse)

        # pinned notes always on top (except in trash/pinned views)
        if category_id not in (SYSTEM_PINNED, SYSTEM_TRASH):
            pinned = [n for n in notes if n.is_pinned]
            unpinned = [n for n in notes if not n.is_pinned]
            notes = pinned + unpinned

        return notes

    def delete_note(self, note_id: str) -> None:
        note = self._notes.get(note_id)
        if note:
            note.is_deleted = True
            note.touch()
            self._save()

    def restore_note(self, note_id: str) -> None:
        note = self._notes.get(note_id)
        if note:
            note.is_deleted = False
            note.touch()
            self._save()

    def purge_note(self, note_id: str) -> None:
        if note_id in self._notes:
            del self._notes[note_id]
            self._save()

    # ── Categories ────────────────────────────────────────────────────────────

    def save_category(self, category: Category) -> None:
        self._categories[category.id] = category
        self._save()

    def get_category(self, category_id: str) -> Optional[Category]:
        return self._categories.get(category_id)

    def list_categories(self, include_system: bool = True) -> List[Category]:
        cats = list(self._categories.values())
        if not include_system:
            cats = [c for c in cats if not c.is_system]
        return cats

    def delete_category(self, category_id: str) -> None:
        cat = self._categories.get(category_id)
        if cat and not cat.is_system:
            # move notes to "all"
            for note in self._notes.values():
                if note.category_id == category_id:
                    note.category_id = SYSTEM_ALL
            del self._categories[category_id]
            self._save()
