"""Shared generation helpers for the Elmer IM full-machine case."""

from __future__ import annotations

from pathlib import Path

__all__ = [
    "write_text_file",
]


def write_text_file(path: str | Path, content: str) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
