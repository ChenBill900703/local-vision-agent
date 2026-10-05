"""JSON-only persistent worker. No arbitrary adapter/class deserialization or fallback."""

import argparse
import json
import os
import sys
import time
import traceback
from pathlib import Path
from typing import Any

from .contracts import AgentError, ImageInput, Limits, Request
from .internvl_backend import InternVLBackend
from .internvl_contract import RuntimeConfig
from .pilot_worker import Evidence
from .source_input import SourceImageLimits


def serve(
    root: Path, directory: Path, configuration: Path, *, persistent_images: bool = False
) -> int:
    evidence = Evidence(directory, pipe=True)
    backend: InternVLBackend | None = None
    exit_code = 1
    close_id: int | None = None
    try:
        values = json.loads(configuration.read_text(encoding="utf8"))
        values["limits"] = Limits(**values["limits"])
        values["source_image_limits"] = SourceImageLimits.from_dict(values["source_image_limits"])
        config = RuntimeConfig(**values)
        backend = InternVLBackend(root, config, evidence)
        backend.persistent_images = persistent_images
        evidence.emit("response", id=0, op="load", payload=backend.load())
        expected_id = 1
        while True:
            line = sys.stdin.readline(65537)
            if not line or len(line) > 65536:
                raise AgentError("RPC_EOF_OR_OVERSIZE")
            request: dict[str, Any] = json.loads(line)
            if (
                set(request) != {"id", "op", "payload"}
                or type(request["id"]) is not int
                or request["id"] != expected_id
                or not isinstance(request["payload"], dict)
            ):
                raise AgentError("INVALID_RPC_SCHEMA_OR_SEQUENCE")
            expected_id += 1
            op, payload = request["op"], request["payload"]
            if op == "begin_image":
                if set(payload) != {"input_id", "path", "sha256"}:
                    raise AgentError("INVALID_IMAGE_SCHEMA")
                result = backend.begin_image(
                    ImageInput(payload["input_id"], Path(payload["path"])), payload["sha256"]
                )
            elif op == "invoke":
                result = backend.invoke(Request(**payload))
            elif op == "end_image" and not payload and persistent_images:
                result = backend.end_image()
            elif op == "unload" and not payload:
                close_id = request["id"]
                exit_code = 0
                break
            else:
                raise AgentError("UNKNOWN_RPC_OPERATION")
            evidence.emit("response", id=request["id"], op=op, payload=result)
    except Exception as exc:  # noqa: BLE001 -- preserve error, no retry/fallback
        evidence.emit("failure", message=str(exc), traceback=traceback.format_exc())
    # Exception frames have been released before cleanup, including CUDA tensors.
    try:
        result = backend.unload() if backend is not None else {}
        if close_id is not None:
            evidence.emit("response", id=close_id, op="unload", payload=result)
    except Exception as exc:  # noqa: BLE001 -- process exit follows even if cleanup fails
        exit_code = 1
        evidence.emit("cleanup_failure", message=str(exc), traceback=traceback.format_exc())
    evidence.emit("worker_done", exit_code=exit_code)
    return exit_code


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--configuration", type=Path, required=True)
    parser.add_argument("--persistent-images", action="store_true")
    args = parser.parse_args()
    print(
        json.dumps({"phase": "ready", "pid": os.getpid(), "monotonic": time.monotonic()}),
        flush=True,
    )
    if sys.stdin.readline().strip() != "GO":
        raise SystemExit("SUPERVISOR_HANDSHAKE_REQUIRED")
    raise SystemExit(
        serve(
            args.root.resolve(),
            args.run_dir.resolve(),
            args.configuration.resolve(),
            persistent_images=args.persistent_images,
        )
    )
