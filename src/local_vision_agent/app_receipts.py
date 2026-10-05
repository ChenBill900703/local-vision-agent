"""Read existing local worker receipts, without executing model code or issuing requests."""

import json
from pathlib import Path
from typing import Any


def read_frame_receipts(directory: Path, input_id: str) -> tuple[list[dict[str, Any]], str | None]:
    path = directory / "events.jsonl"
    if not path.exists():
        return [], "EVENT_LOG_UNAVAILABLE"
    calls: dict[str, dict[str, Any]] = {}
    error = None
    try:
        with path.open(encoding="utf-8") as stream:
            for line in stream:
                try:
                    event = json.loads(line)
                except ValueError:
                    error = "INCOMPLETE_EVENT_LINE"
                    continue
                if not isinstance(event, dict) or event.get("input_id") != input_id:
                    continue
                identifier = event.get("call_id")
                if not isinstance(identifier, str):
                    continue
                if event.get("phase") == "call_start":
                    calls[identifier] = {
                        **event,
                        "call_started": True,
                        "input_tokens": len(event["input_token_ids"])
                        if isinstance(event.get("input_token_ids"), list)
                        else None,
                    }
                elif event.get("phase") == "call_done":
                    calls.setdefault(identifier, {}).update(event)
    except OSError as exc:
        error = "EVENT_READ_FAILED: " + str(exc)
    return list(calls.values()), error
