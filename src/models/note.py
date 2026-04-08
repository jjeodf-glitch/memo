"""노트 데이터 모델"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Note:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    content: str = ""
    category_id: str = "all"
    tags: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=_now_iso)
    updated_at: str = field(default_factory=_now_iso)
    is_pinned: bool = False
    is_deleted: bool = False

    @property
    def preview(self) -> str:
        text = self.content.strip()
        if len(text) > 100:
            return text[:100] + "..."
        return text

    @property
    def display_title(self) -> str:
        return self.title.strip() if self.title.strip() else "제목 없음"

    @property
    def updated_at_local(self) -> str:
        try:
            dt = datetime.fromisoformat(self.updated_at)
            local_dt = dt.astimezone()
            return local_dt.strftime("%Y-%m-%d %H:%M")
        except Exception:
            return self.updated_at

    def touch(self) -> None:
        self.updated_at = _now_iso()

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "category_id": self.category_id,
            "tags": self.tags,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_pinned": self.is_pinned,
            "is_deleted": self.is_deleted,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Note":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            title=data.get("title", ""),
            content=data.get("content", ""),
            category_id=data.get("category_id", "all"),
            tags=data.get("tags", []),
            created_at=data.get("created_at", _now_iso()),
            updated_at=data.get("updated_at", _now_iso()),
            is_pinned=data.get("is_pinned", False),
            is_deleted=data.get("is_deleted", False),
        )
