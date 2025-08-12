from __future__ import annotations
import json, os
from typing import Set

class SeenStore:
    def __init__(self, path: str):
        self.path = path
        self._seen = set()  # type: Set[str]
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.path):
            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    self._seen = set(json.load(f))
            except Exception:
                self._seen = set()
        else:
            self._seen = set()

    def mark_and_filter_new(self, ids: list[str]) -> list[str]:
        new_ids = [i for i in ids if i not in self._seen]
        self._seen.update(new_ids)
        return new_ids

    def save(self) -> None:
        os.makedirs(os.path.dirname(self.path), exist_ok=True)
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(sorted(self._seen), f, ensure_ascii=False, indent=2)
