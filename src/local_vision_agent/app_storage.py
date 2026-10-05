"""Private atomic result records and strictly owned temporary camera files."""

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from .app_export_schema import RATINGS


class AppStorage:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def path(self, relative: str) -> Path:
        value = (self.root / relative).resolve()
        if not value.is_relative_to(self.root) or value == self.root:
            raise ValueError("STORAGE_PATH_ESCAPE")
        return value

    def allocate(self, identifier: str) -> Path:
        if not re.fullmatch(r"[a-zA-Z0-9-]{1,128}", identifier):
            raise ValueError("INVALID_STORAGE_ID")
        path = self.path(identifier)
        path.mkdir(exist_ok=False)
        (path / ".app-owned").write_text("windows-app-v1", encoding="utf-8")
        return path

    def save(self, directory: Path, data: dict[str, Any], name: str = "result.json") -> Path:
        relative = str(directory.relative_to(self.root) / name)
        target = self.path(relative)
        temp = self.path(relative + "." + uuid4().hex + ".tmp")
        try:
            temp.write_text(
                json.dumps(data, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8"
            )
            temp.replace(target)
        finally:
            temp.unlink(missing_ok=True)
        return target

    def load(self, relative: str) -> dict[str, Any]:
        path = self.path(relative)
        if path.stat().st_size > 16 * 1024 * 1024:
            raise ValueError("HISTORY_TOO_LARGE")
        data: Any = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict) or data.get("schema") != "windows-app-result-v1":
            raise ValueError("INVALID_HISTORY")
        if not isinstance(data.get("report_text"), str) or not isinstance(
            data.get("metadata"), dict
        ):
            raise ValueError("INVALID_HISTORY")  # noqa: TRY004 -- corrupt serialized data
        return dict(data)

    def history(self) -> list[tuple[str, dict[str, Any] | None]]:
        records: list[tuple[str, dict[str, Any] | None]] = []
        for path in sorted(self.root.glob("*/result.json"), reverse=True):
            relative = str(path.relative_to(self.root))
            try:
                records.append((relative, self.load(relative)))
            except (OSError, ValueError):
                records.append((relative, None))
        return records

    def review(self, relative: str) -> dict[str, Any]:
        self.load(relative)
        target = self.path(str(Path(relative).parent / "review.json"))
        if not target.exists():
            return {
                "human_rating": "NOT_REVIEWED",
                "human_note": "",
                "human_review_timestamp": None,
            }
        data = self.read_json(str(target.relative_to(self.root)))
        if data.get("human_rating") not in RATINGS or not isinstance(data.get("human_note"), str):
            raise ValueError("INVALID_HUMAN_REVIEW")
        return data

    def update_review(self, relative: str, rating: str, note: str) -> dict[str, Any]:
        self.load(relative)
        if rating not in RATINGS or not isinstance(note, str) or len(note) > 10000:
            raise ValueError("INVALID_HUMAN_REVIEW")
        data = {
            "schema": "author-engineering-review-v1",
            "human_rating": rating,
            "human_note": note,
            "human_review_timestamp": datetime.now(UTC).isoformat(),
            "ground_truth": False,
        }
        self.save(self.path(relative).parent, data, "review.json")
        return data

    def read_json(self, relative: str) -> dict[str, Any]:
        path = self.path(relative)
        if path.stat().st_size > 16 * 1024 * 1024:
            raise ValueError("RECORD_TOO_LARGE")
        value = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(value, dict):
            raise ValueError("INVALID_RECORD")  # noqa: TRY004 -- corrupt serialized data
        return value

    def sessions(self) -> list[tuple[str, dict[str, Any] | None]]:
        result: list[tuple[str, dict[str, Any] | None]] = []
        for path in sorted(self.root.glob("*/session.json")):
            relative = str(path.relative_to(self.root))
            try:
                data = self.read_json(relative)
                if data.get("schema") != "webcam-session-v1" or not isinstance(
                    data.get("session_id"), str
                ):
                    raise ValueError("INVALID_SESSION")
                result.append((relative, data))
            except (OSError, ValueError):
                result.append((relative, None))
        return result

    def remove_frame(self, directory: Path) -> None:
        """Never recurse or accept user file paths; remove only known owned images."""
        marker = self.path(str(directory.relative_to(self.root) / ".app-owned"))
        if marker.read_text(encoding="utf-8") != "windows-app-v1":
            raise ValueError("UNOWNED_FRAME_DIRECTORY")
        for name in ("frame.png", "input/normalized.png"):
            path = self.path(str(directory.relative_to(self.root) / name))
            path.unlink(missing_ok=True)

    def purge_ephemeral(self) -> None:
        """Recover a crashed save-OFF capture; explicit marker/retention, no recursive delete."""
        for file in self.root.glob("*/retention.json"):
            if json.loads(file.read_text(encoding="utf-8")) == {"save_frame": False}:
                self.remove_frame(file.parent)
