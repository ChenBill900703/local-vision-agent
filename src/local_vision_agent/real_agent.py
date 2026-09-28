"""One-image development lifecycle around the unchanged bounded A–D decision policy."""

import argparse
import json
import time
from dataclasses import asdict, replace
from pathlib import Path
from uuid import uuid4

from .agent import Agent
from .contracts import AgentError, ImageInput, Method, Report
from .image_input import inspect_image
from .internvl_adapter import InternVLAdapter
from .internvl_contract import NORMALIZER, RuntimeConfig, load_runtime_config
from .internvl_policy import REVISION
from .reporting import to_json, to_markdown


def run_development(
    item: ImageInput,
    method: Method,
    asset_root: Path,
    evidence_directory: Path,
    config: RuntimeConfig,
) -> Report:
    """Explicit execution entry; caller must have scoped GPU authorization.

    No repeated loads, batch loop, automatic mock, semantic success claim or retries.
    A fresh adapter/controller/image memory is created for each separately invoked run.
    """
    config.__post_init__()
    if evidence_directory.exists():
        raise AgentError("RUN_DIRECTORY_EXISTS")
    started = time.monotonic()
    report: Report | None = None
    adapter = InternVLAdapter(asset_root, evidence_directory, config)
    cleanup_error: str | None = None
    try:
        inspect_image(item, config.limits)  # Bad input rejected before GPU query/load.
        adapter.load()
        adapter.begin_image(item)
        report = Agent(config.limits, adapter, executor=adapter).run(item, method)
    except Exception as exc:  # noqa: BLE001 -- explicit failure report, no fallback
        code = exc.code if isinstance(exc, AgentError) else "RUNTIME_FAILURE:" + type(exc).__name__
        report = Report(
            str(uuid4()),
            item.input_id,
            method,
            "failed",
            code,
            "NOT_STARTED",
            None,
            (),
            (),
            ("START", "REPORT", "STOP"),
            config.limits,
            model_id=adapter.model_id,
            model_revision=REVISION,
            evidence_kind="REAL_LOCAL_DEVELOPMENT_NOT_FORMAL_THESIS_RESULT",
        )
    finally:
        if adapter.loaded or adapter.transport.process is not None:
            try:
                adapter.unload()
            except Exception as exc:  # noqa: BLE001 -- never mark an unverified cleanup successful
                cleanup_error = str(exc)
                adapter.transport.abort()
    assert report is not None
    measurements = [adapter.metadata.get("measurement", {})] + [
        x.get("measurement", {}) for x in adapter.trace
    ]
    peaks = [m["peak_reserved_bytes"] / 1048576 for m in measurements if "peak_reserved_bytes" in m]
    latency = sum(x["latency_s"] for x in adapter.trace) if adapter.trace else None
    metadata: dict[str, object] = {
        "preprocessing": config.preprocessing,
        "normalizer": NORMALIZER,
        "raw_trace": str(adapter.directory / "events.jsonl"),
        "observation_evidence": {
            x["call_id"]: str(adapter.directory / "events.jsonl") + "#" + x["call_id"]
            for x in adapter.trace
        },
        "model_runtime": adapter.metadata,
        "cleanup": adapter.cleanup,
        "cleanup_error": cleanup_error,
        "end_to_end_s": time.monotonic() - started,
        "same_model_verification_is_ground_truth": False,
    }
    report = replace(
        report,
        peak_vram_mib=max(peaks) if peaks else None,
        model_latency_s=latency,
        runtime_metadata=metadata,
    )
    if cleanup_error:
        report = replace(
            report,
            status="partial" if report.observations else "failed",
            stop_reason="CLEANUP_FAILED",
        )
    # Exclusive directory is established by transport.load; invalid inputs may leave no directory.
    if adapter.transport.owns_directory:
        (adapter.directory / "agent_report.json").write_text(to_json(report), encoding="utf8")
        (adapter.directory / "agent_report.md").write_text(to_markdown(report), encoding="utf8")
        (adapter.directory / "normalized_trace.json").write_text(
            json.dumps(
                [
                    {
                        **asdict(o),
                        "observation_id": o.call_id,
                        "raw_model_response": o.answer.text if o.answer else None,
                        "extracted_claims": list(o.answer.claims) if o.answer else [],
                        "evidence_links": [
                            str(adapter.directory / "events.jsonl") + "#" + o.call_id
                        ],
                    }
                    for o in report.observations
                ],
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf8",
        )
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Explicitly authorized single-image local development run; no formal evaluation."
    )
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--assets", type=Path, required=True)
    parser.add_argument("--image", type=Path, required=True)
    parser.add_argument("--input-id", required=True)
    parser.add_argument("--evidence-dir", type=Path, required=True)
    parser.add_argument("--method", choices=[m.value for m in Method], required=True)
    parser.add_argument("--authorize-development-gpu", action="store_true", required=True)
    args = parser.parse_args()
    result = run_development(
        ImageInput(args.input_id, args.image),
        Method(args.method),
        args.assets,
        args.evidence_dir,
        load_runtime_config(args.config),
    )
    print(to_json(result))
    raise SystemExit(0 if result.status == "complete" else 1)
