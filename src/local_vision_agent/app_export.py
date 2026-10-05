"""CPU-only deterministic derivatives. Never edits canonical records or runs inference."""

import csv
import hashlib
import io
import json
import math
import statistics
from pathlib import Path
from typing import Any

from .app_export_schema import CALL_COLUMNS, RATINGS, SESSION_COLUMNS, SUMMARY_COLUMNS
from .app_storage import AppStorage

Row = dict[str, Any]
REAL = "REAL_LOCAL_DEVELOPMENT_NOT_FORMAL_THESIS_RESULT"


def mapping(value: Any) -> Row:
    return value if isinstance(value, dict) else {}


def records(value: Any) -> list[Row]:
    return [x for x in value if isinstance(x, dict)] if isinstance(value, list) else []


def numeric(value: Any) -> float | int | None:
    return value if type(value) in (int, float) and math.isfinite(value) and value >= 0 else None


def known_sum(values: list[Any]) -> float | int | None:
    numbers = [numeric(x) for x in values]
    return sum(x for x in numbers if x is not None) if all(x is not None for x in numbers) else None


def values(rows: list[Row], key: str) -> list[float | int]:
    return [n for row in rows if (n := numeric(row.get(key))) is not None]


def stats(rows: list[Row], key: str) -> Row:
    nums = values(rows, key)
    return {
        "mean": statistics.mean(nums) if nums else None,
        "median": statistics.median(nums) if nums else None,
        "min": min(nums) if nums else None,
        "max": max(nums) if nums else None,
    }


def sheet_cell(value: Any) -> str | int | float | bool:
    if value is None:
        return ""
    if isinstance(value, str):
        # Also block whitespace/control-prefixed formula payloads. Only the derivative changes.
        if value.lstrip(" \t\r\n\ufeff").startswith(("=", "+", "-", "@")):
            return "'" + value
        return value
    if isinstance(value, (int, float, bool)):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def csv_text(columns: tuple[str, ...], rows: list[Row]) -> str:
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\r\n")
    writer.writerow(columns)
    for row in rows:
        writer.writerow([sheet_cell(row.get(key)) for key in columns])
    return stream.getvalue()


def evidence_label(data: Row) -> str:
    kind = mapping(data.get("metadata")).get(
        "evidence_kind", mapping(data.get("report")).get("evidence_kind")
    )
    return "REAL" if kind == REAL else "MOCK" if kind == "MOCK_NOT_RESEARCH_EVIDENCE" else "UNKNOWN"


def call_rows(data: Row) -> list[Row]:
    report, meta = mapping(data.get("report")), mapping(data.get("metadata"))
    runtime = mapping(report.get("runtime_metadata")) or mapping(data.get("attempt_runtime"))
    observations = records(report.get("observations"))
    by_id = {x.get("call_id"): x for x in observations}
    claims = records(report.get("claims"))
    is_real = meta.get("evidence_kind", report.get("evidence_kind")) == REAL
    # Real rows require a backend receipt or recorded call_start, not a planned observation.
    receipts = records(runtime.get("frame_trace"))
    if not is_real:
        receipts = [
            {
                "call_id": x.get("call_id"),
                "request": x.get("request"),
                "raw_response": mapping(x.get("answer")).get("text"),
                "output_tokens": mapping(x.get("answer")).get("output_tokens"),
                "stop_reason": mapping(x.get("answer")).get("generation_stop_reason"),
            }
            for x in observations
            if isinstance(x.get("answer"), dict)
        ]
    rows = []
    for index, receipt in enumerate(receipts, 1):
        obs = mapping(by_id.get(receipt.get("call_id")))
        request = mapping(receipt.get("request")) or mapping(obs.get("request"))
        answer = mapping(obs.get("answer"))
        candidate = next(
            (
                i
                for i, c in enumerate(claims, 1)
                if c.get("verification_id") == receipt.get("call_id")
            ),
            None,
        )
        stop = receipt.get("stop_reason", answer.get("generation_stop_reason"))
        rows.append(
            {
                "record_schema_version": "model-calls-v1/" + evidence_label(data),
                "session_id": meta.get("session_id"),
                "input_id": meta.get("input_id"),
                "frame_id": meta.get("input_id") if meta.get("source") == "WEBCAM" else None,
                "call_index": index,
                "agent_state": obs.get("state"),
                "prompt_id": request.get("prompt_id"),
                "input_tokens": receipt.get("input_tokens"),
                "output_tokens": receipt.get("output_tokens"),
                "latency_sec": receipt.get("latency_s"),
                "generation_stop_reason": stop,
                "truncated": stop == "token_limit"
                if stop in ("eos", "token_limit")
                else answer.get("truncated"),
                "candidate_id": f"claim-{candidate}" if candidate else None,
                "verification_candidate_text": request.get("claim"),
                "verification_model_verdict": answer.get("verdict")
                if request.get("tool") == "verify"
                else None,
                "raw_response": receipt.get("raw_response"),
            }
        )
    return rows


def analysis_row(data: Row, review: Row | None = None) -> Row:
    meta, report = mapping(data.get("metadata")), mapping(data.get("report"))
    runtime = mapping(report.get("runtime_metadata")) or mapping(data.get("attempt_runtime"))
    source = mapping(runtime.get("source_input"))
    normalized = mapping(source.get("model_input"))
    calls = call_rows(data)
    claims = records(report.get("claims"))
    human = review or {}
    is_real = meta.get("evidence_kind", report.get("evidence_kind")) == REAL
    output = known_sum([x.get("output_tokens") for x in calls])
    inputs = known_sum([x.get("input_tokens") for x in calls])
    # No calls without an explicit complete trace is unknown, not proof of zero.
    call_count = (
        len(calls)
        if (not is_real and report) or runtime.get("calls_complete") is True or calls
        else None
    )
    if call_count is None:
        inputs = output = None
    row: Row = {
        "record_schema_version": "analysis-summary-v1/" + evidence_label(data),
        "timestamp": meta.get("timestamp"),
        "source_type": meta.get("source"),
        "session_id": meta.get("session_id"),
        "input_id": meta.get("input_id"),
        "frame_id": meta.get("input_id") if meta.get("source") == "WEBCAM" else None,
        "status": meta.get("status"),
        "completion_reason": report.get("completion"),
        "stop_reason": meta.get("stop_reason", report.get("stop_reason")),
        "agent_state_sequence": " → ".join(report.get("states", [])),
        "model_calls": call_count,
        "input_tokens": inputs,
        "output_tokens": output,
        "total_tokens": inputs + output if inputs is not None and output is not None else None,
        "truncated_call_count": sum(x.get("truncated") is True for x in calls)
        if call_count is not None and all(type(x.get("truncated")) is bool for x in calls)
        else None,
        "candidate_claim_count": report.get("candidate_claim_count"),
        "verification_attempted": report.get("verification_attempted"),
        "verification_completed": report.get("verification_completed"),
        "verification_budget_unresolved": report.get("verification_unresolved_by_budget"),
        "verification_coverage": report.get("verification_coverage_ratio"),
        "analysis_latency_sec": meta.get("analysis_latency_s"),
        "total_latency_sec": meta.get("latency_s"),
        "peak_allocated_mib": meta.get("allocated_mib") if is_real else None,
        "peak_reserved_mib": meta.get("reserved_mib") if is_real else None,
        "peak_device_used_mib": meta.get("device_used_mib") if is_real else None,
        "cleanup_status": meta.get("cleanup_status", runtime.get("session_cleanup")),
        "human_rating": human.get("human_rating", "NOT_REVIEWED"),
        "human_note": human.get("human_note", ""),
        "human_review_timestamp": human.get("human_review_timestamp"),
        "final_report": data.get("report_text"),
        "error_type": meta.get("error_type"),
        "error_message": meta.get("error_message"),
    }
    for key in ("width", "height", "format", "bytes", "sha256"):
        row["source_" + key] = source.get("source_" + key)
    for key in ("width", "height", "sha256"):
        row["normalized_" + key] = normalized.get(key)
    for verdict in ("supported", "contradicted", "unresolved"):
        row["verification_" + verdict] = (
            sum(c.get("status") == verdict for c in claims) if report else None
        )
    return row


def engineering_summary(rows: list[Row]) -> Row:
    total = len(rows)
    result: Row = {
        "schema": "engineering-summary-v1",
        "total_analysis_attempts": total,
        "evidence_scope": "DESCRIPTIVE ENGINEERING ONLY; reviews are not ground truth",
    }
    for source in ("IMAGE", "WEBCAM"):
        result[source.lower() + "_attempts"] = sum(r.get("source_type") == source for r in rows)
    for status in ("complete", "partial", "failed"):
        result[status + "_count"] = sum(r.get("status") == status for r in rows)
    result["unknown_status_count"] = total - sum(
        result[x + "_count"] for x in ("complete", "partial", "failed")
    )
    result["completion_rate"] = result["complete_count"] / total if total else None
    for rating in RATINGS:
        result[rating.lower() + "_count"] = sum(r.get("human_rating") == rating for r in rows)
    for field in ("model_calls", "output_tokens"):
        measured = values(rows, field)
        result["mean_" + field] = statistics.mean(measured) if measured else None
        result["median_" + field] = statistics.median(measured) if measured else None
        result["total_" + field] = known_sum([r.get(field) for r in rows])
        result[field + "_known_count"] = len(measured)
    trunc = values(rows, "truncated_call_count")
    result["truncated_analysis_count"] = sum(x > 0 for x in trunc)
    result["truncation_known_count"] = len(trunc)
    result["truncation_rate"] = sum(x > 0 for x in trunc) / len(trunc) if trunc else None
    for field in ("verification_coverage", "analysis_latency_sec"):
        for name, value in stats(rows, field).items():
            if name in ("mean", "median") or field == "analysis_latency_sec":
                result[name + "_" + field] = value
        result[field + "_known_count"] = len(values(rows, field))
    real = [r for r in rows if str(r.get("record_schema_version", "")).endswith("/REAL")]
    result["number_with_real_gpu_measurement"] = sum(
        numeric(r.get("peak_allocated_mib")) is not None
        or numeric(r.get("peak_reserved_mib")) is not None
        for r in real
    )
    for field in ("peak_allocated_mib", "peak_reserved_mib"):
        for name in ("mean", "max"):
            result[name + "_" + field] = stats(real, field)[name]
        result[field + "_known_count"] = len(values(real, field))
    return result


def session_row(session: Row, analyses: list[Row]) -> Row:
    row = {key: session.get(key) for key in SESSION_COLUMNS}
    row["record_schema_version"] = "webcam-session-v1"
    matching = [
        r
        for r in analyses
        if r.get("source_type") == "WEBCAM" and r.get("session_id") == session.get("session_id")
    ]
    summary = engineering_summary(matching)
    for target, origin in {
        "completed_frames": "complete_count",
        "partial_frames": "partial_count",
        "failed_frames": "failed_count",
        "total_model_calls": "total_model_calls",
        "average_model_calls": "mean_model_calls",
        "total_output_tokens": "total_output_tokens",
        "average_output_tokens": "mean_output_tokens",
        "mean_verification_coverage": "mean_verification_coverage",
        "truncated_frame_count": "truncated_analysis_count",
    }.items():
        row[target] = summary[origin]
    for name, value in stats(matching, "analysis_latency_sec").items():
        row[name + "_analysis_latency_sec"] = value
    for field in ("peak_allocated_mib", "peak_reserved_mib", "peak_device_used_mib"):
        row[field] = (
            stats(matching, field)["max"] if session.get("camera_backend_type") != "FAKE" else None
        )
    if session.get("camera_backend_type") == "FAKE":
        for key in ("camera_release_success", "worker_cleanup_success", "model_cleanup_success"):
            row[key] = None
    # A crashed/missing result must not make an attempted frame disappear as a zero.
    if numeric(session.get("analysis_attempts")) != len(matching):
        for key in ("total_model_calls", "total_output_tokens"):
            row[key] = None
    return row


def cleanup_status(value: Row) -> str:
    if value.get("mock_cleanup"):
        return "MOCK_NOT_PHYSICAL_EVIDENCE"
    if value.get("cleanup_error") or value.get("persistence_error"):
        return "FAIL"
    if value.get("model_was_not_loaded"):
        return "MODEL_NOT_LOADED"
    m = mapping(value.get("measurement"))
    if (
        m.get("allocated_bytes") == 0
        and m.get("reserved_bytes") == 0
        and value.get("worker_exited") is True
        and value.get("job_empty") is True
        and value.get("baseline_equivalent") is True
    ):
        return "PASS"
    return "UNVERIFIED"


def export_bundle(storage: AppStorage, kind: str = "all") -> Path:
    """New exclusive derived directory; filename allowlist, no user/model output paths."""
    allowed = {"all", "analysis_summary", "model_calls", "webcam_sessions"}
    if kind not in allowed:
        raise ValueError("INVALID_EXPORT_KIND")
    from uuid import uuid4

    summaries: list[Row] = []
    calls: list[Row] = []
    errors: list[Row] = []
    sources: dict[str, str] = {}
    entries = storage.history()
    valid = [(ref, d) for ref, d in entries if d is not None]
    valid.sort(
        key=lambda x: (
            str(mapping(x[1].get("metadata")).get("timestamp", "")),
            str(mapping(x[1].get("metadata")).get("session_id", "")),
            str(mapping(x[1].get("metadata")).get("input_id", "")),
            x[0],
        )
    )
    for ref, data in valid:
        try:
            review = storage.review(ref)
        except (OSError, ValueError) as exc:
            errors.append({"reference": ref, "error": "INVALID_REVIEW", "detail": str(exc)})
            review = {"human_rating": "NOT_REVIEWED", "human_note": ""}
        try:
            row = analysis_row(data, review)
            rows = call_rows(data)
        except (ValueError, TypeError, KeyError) as exc:
            errors.append({"reference": ref, "error": "INVALID_RECORD_CONTENT", "detail": str(exc)})
            continue
        cleanup_path = storage.path(str(Path(ref).parent / "session_cleanup.json"))
        if cleanup_path.exists():
            try:
                cleanup = storage.read_json(str(cleanup_path.relative_to(storage.root)))
                row["cleanup_status"] = cleanup_status(cleanup)
                sources[str(cleanup_path.relative_to(storage.root))] = hashlib.sha256(
                    cleanup_path.read_bytes()
                ).hexdigest()
            except (OSError, ValueError):
                errors.append({"reference": ref, "error": "INVALID_CLEANUP_RECORD"})
        summaries.append(row)
        calls.extend(rows)
        sources[ref] = hashlib.sha256(storage.path(ref).read_bytes()).hexdigest()
        review_path = storage.path(str(Path(ref).parent / "review.json"))
        if review_path.exists():
            sources[str(review_path.relative_to(storage.root))] = hashlib.sha256(
                review_path.read_bytes()
            ).hexdigest()
    errors.extend(
        {"reference": ref, "error": "CORRUPT_HISTORY"} for ref, data in entries if data is None
    )
    sessions = []
    for ref, session in storage.sessions():
        if session is None:
            errors.append({"reference": ref, "error": "CORRUPT_SESSION"})
        else:
            sessions.append(session_row(session, summaries))
            sources[ref] = hashlib.sha256(storage.path(ref).read_bytes()).hexdigest()
    known_sessions = {x.get("session_id") for x in sessions}
    for identifier in sorted(
        {
            str(r["session_id"])
            for r in summaries
            if r.get("source_type") == "WEBCAM" and r.get("session_id")
        }
    ):
        if identifier not in known_sessions:
            sessions.append(session_row({"session_id": identifier}, summaries))
            errors.append({"session_id": identifier, "error": "SESSION_METADATA_UNAVAILABLE"})
    sessions.sort(
        key=lambda s: (str(s.get("session_start_timestamp", "")), str(s.get("session_id", "")))
    )
    directory = storage.allocate("export-" + uuid4().hex)
    tables = {
        "analysis_summary": (SUMMARY_COLUMNS, summaries),
        "model_calls": (CALL_COLUMNS, calls),
        "webcam_sessions": (SESSION_COLUMNS, sessions),
    }
    for name, (columns, table) in tables.items():
        if kind in ("all", name):
            path = storage.path(str(directory.relative_to(storage.root) / (name + ".csv")))
            temporary = path.with_suffix(".tmp")
            with temporary.open("w", encoding="utf-8-sig", newline="") as stream:
                stream.write(csv_text(columns, table))
            temporary.replace(path)
    summary = engineering_summary(summaries)
    summary["by_evidence_kind"] = {
        label: engineering_summary(
            [r for r in summaries if str(r["record_schema_version"]).endswith("/" + label)]
        )
        for label in ("REAL", "MOCK", "UNKNOWN")
    }
    storage.save(directory, summary, "engineering_summary.json")
    storage.save(
        directory,
        {
            "schema": "export-audit-v1",
            "source_sha256": sources,
            "errors": errors,
            "valid_analysis_records": len(summaries),
            "unreadable_records": len(errors),
            "csv_text_escape": "prefix apostrophe for leading =+-@ after whitespace; JSON unchanged",
            "denominators": "completion: valid analysis attempts; missing numeric observations excluded from means with known counts; incomplete totals=null",
            "csv_files": {
                p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                for p in sorted(directory.glob("*.csv"))
            },
        },
        "export_audit.json",
    )
    return directory
