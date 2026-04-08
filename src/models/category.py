"""카테고리 데이터 모델"""
from __future__ import annotations
import uuid
from dataclasses import dataclass, field
from typing import Optional


SYSTEM_ALL = "all"
SYSTEM_PINNED = "pinned"
SYSTEM_TRASH = "trash"


@dataclass
class Category:
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    color: str = "#5B8CFF"
    parent_id: Optional[str] = None
    is_system: bool = False

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "parent_id": self.parent_id,
            "is_system": self.is_system,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Category":
        return cls(
            id=data.get("id", str(uuid.uuid4())),
            name=data.get("name", ""),
            color=data.get("color", "#5B8CFF"),
            parent_id=data.get("parent_id"),
            is_system=data.get("is_system", False),
        )

    @classmethod
    def make_system_categories(cls):
        return [
            cls(id=SYSTEM_ALL,    name="전체",   color="#5B8CFF", is_system=True),
            cls(id=SYSTEM_PINNED, name="고정됨", color="#FFD700", is_system=True),
            cls(id=SYSTEM_TRASH,  name="휴지통", color="#FF6B6B", is_system=True),
        ]
