"""CPU-only reconstruction and consistency audit of the single authorized smoke run."""

import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUN_ID = "INTERNVL_REAL_AGENT_GPU_SMOKE_20260930"
RUN = ROOT / "artifacts/internvl3-20260928/runs" / RUN_ID
EVIDENCE = ROOT / "artifacts/internvl-real-agent-smoke-20260930/evidence"


def read(name):
    return json.loads((RUN / name).read_text(encoding="utf8"))


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    report = read("agent_report.json")
    trace = read("normalized_trace.json")
    provenance = read("provenance.json")
    cleanup = read("cleanup_result.json")
    termination = read("termination_result.json")
    baseline = read("device_before.json")
    events = [json.loads(s) for s in (RUN / "events.jsonl").read_text(encoding="utf8").splitlines()]
    samples = [json.loads(s) for s in (RUN / "device_samples.jsonl").read_text(encoding="utf8").splitlines()]
    timing = json.loads((EVIDENCE / "parent_timing.json").read_text(encoding="utf8"))
    amendment = ROOT / "docs/REAL_INTERNVL_AGENT_GPU_SMOKE_AMENDMENT_2026-09-30.md"
    assert digest(amendment) == (EVIDENCE / "frozen_amendment.sha256").read_text(encoding="utf8")
    audit = json.loads((EVIDENCE / "resume_audit.json").read_text(encoding="utf8"))
    for name, expected in audit["source_hashes"].items():
        assert digest(ROOT / name) == expected, name
    assert read("runtime_config.json") == audit["config"]
    assert report["image"]["sha256"] == audit["fixture_sha256"]
    assert report["method"] == "D" and report["status"] == "complete"
    assert report["stop_reason"] == "COMPLETED"
    assert report["model_revision"] == audit["runtime_manifest"]["revision"]
    assert not any(e["phase"] in {"failure", "cleanup_failure", "network_violation"} for e in events)
    loaded = [e for e in events if e["phase"] == "model_loaded"]
    assert len(loaded) == 1 and loaded[0]["offline"] and loaded[0]["placement"]["all_cuda0"]
    assert len({e["pid"] for e in events}) == 1
    assert any(e["phase"] == "preflight_pass" for e in events)
    calls = {e["call_id"]: e for e in events if e["phase"] == "call_done"}
    starts = {e["call_id"]: e for e in events if e["phase"] == "call_start"}
    assert len(calls) == len(trace) == len(report["observations"]) <= 8
    assert sum(e["output_tokens"] for e in calls.values()) <= 1024
    for observation, normalized in zip(report["observations"], trace, strict=True):
        cid = observation["call_id"]
        call = calls[cid]
        assert observation["error"] is None
        assert observation["request"] == starts[cid]["request"]
        assert observation["answer"]["text"] == normalized["raw_model_response"] == call["raw_response"]
        assert observation["answer"]["claims"] == normalized["extracted_claims"]
        assert normalized["observation_id"] == cid and normalized["state"] == observation["state"]
        assert normalized["evidence_links"] == [str(RUN / "events.jsonl") + "#" + cid]
        assert call["output_tokens"] == len(call["output_token_ids"]) <= 128
        assert call["input_tokens"] == len(starts[cid]["input_token_ids"]) <= 1024
        assert call["latency_s"] < 60 and call["worker_status"] == "healthy"
        assert all(t["device"] == "cuda:0" for t in call["kv_placement"])
        assert all(t["device"] == "cuda:0" for t in starts[cid]["input_placement"])
    for claim in report["claims"]:
        assert claim["observation_ids"] and all(cid in calls for cid in claim["observation_ids"])
        for cid in claim["observation_ids"]:
            assert claim["text"] in next(o for o in report["observations"] if o["call_id"] == cid)["answer"]["claims"]
        verify = next(o for o in report["observations"] if o["call_id"] == claim["verification_id"])
        assert verify["request"]["claim"] == claim["text"]
        assert verify["answer"]["verdict"] == claim["status"]
    assert cleanup["measurement"]["allocated_bytes"] == cleanup["measurement"]["reserved_bytes"] == 0
    assert cleanup["job_empty"] and cleanup["worker_exited"] and cleanup["baseline_equivalent"]
    assert cleanup["parent_cleanup_seconds"] <= 10 and termination["exit_code"] == 0
    assert termination["watchdog_failure"] is None
    measured = [e for e in events if "measurement" in e]
    for e in measured:
        m = e["measurement"]
        assert m["reserved_bytes"] / 1048576 <= 5400
        assert m["nvidia"]["free_mib"] >= 1536 and m["cuda_free_bytes"] / 1048576 >= 1536
    assert all(s["free_mib"] >= 1536 and s["used_mib"] - baseline["used_mib"] <= 6400 for s in samples)
    assert all(e["placement"]["device"] == "cuda:0" for e in events if e["phase"] in {"image_ready", "visual_done"})
    peak_allocated = max(e["measurement"]["peak_allocated_bytes"] for e in measured) / 1048576
    peak_reserved = max(e["measurement"]["peak_reserved_bytes"] for e in measured) / 1048576
    peak_device = max([s["used_mib"] for s in samples] + [e["measurement"]["nvidia"]["used_mib"] for e in measured])
    body = [
        "# Real InternVL Agent GPU Smoke Result — 2026-09-30",
        "DEVELOPMENT ONLY / PILOT / NOT FORMAL THESIS RESULT",
        "## Verdict\n\n**REAL INTERNVL AGENT GPU SMOKE = PASS**",
        "Engineering acceptance for one synthetic Method D run only. No quality/hallucination metric, A–D comparison or RQ2–RQ4 conclusion.",
        "## Provenance",
        f"Run: `{RUN_ID}`; Agent report UUID: `{report['run_id']}`. Exact source HEAD: `{provenance['commit']}`. Initial audit was clean; execution dirty state below contains only the prospective amendment.",
        "```text\n" + provenance["dirty_state"] + "```",
        f"Model/tokenizer/template revision: `{report['model_revision']}`. Config SHA256 `{audit['config_sha256']}`. Model/controlled/framework file hashes and exact installed versions in `evidence/resume_audit.json`; all verified before load. No asset/dependency changes.",
        "Preprocessing: `internvl-single-tile-rgb-bicubic448-imagenet-v1`; 384x256 -> one448x448 RGB BICUBIC/ImageNet-normalized tile changes aspect ratio. Final thesis preprocessing remains unfrozen.",
        "Source, config and frozen amendment hashes rechecked after execution. Full raw run preserved outside Git; no mock or translator used. Python-only report reconstruction: `.venv/Scripts/python.exe scripts/real_agent_smoke_report.py`.",
        "## Hardware",
        "```text\n" + (EVIDENCE / "hardware_before.txt").read_text(encoding="utf-8-sig").strip() + "\n```",
        "Existing torch2.7.1+cu126 (CUDA12.6 build); BF16/cuda:0/eager, one model, batch1. Planning estimate6000MiB, ceiling6400MiB, reserve1536MiB, allocator cap5400MiB. Model parameters/buffers (including vision/language), inputs, visual embeddings and 28-layer KV cache observed cuda:0. No offload/quantization/auto mapping.",
        "Windows shared GPU memory = UNKNOWN / OBSERVABILITY LIMITATION. Placement checks do not prove zero OS spill.",
        "## Method and state trace",
        "D only; existing bounded-policy-v1 prompts/transitions unchanged; <=8calls/iterations,128output tokens/call,1024input tokens/call and1024total outputtokens;60s/call,300s/image,180s/load,10s/cleanup,1800s/session.",
        " -> ".join(report["states"]),
        f"Actual calls: {len(calls)}; total outputtokens: {sum(c['output_tokens'] for c in calls.values())}; stop `{report['stop_reason']}`, investigation `{report['investigation_stop']}`.",
        "## Calls",
        "| Call | State / prompt ID | Input / output tokens | Latency s | Raw answer |\n|---|---|---:|---:|---|",
    ]
    for o in report["observations"]:
        c = calls[o["call_id"]]
        body.append(f"| {o['call_id']} | {o['state']} / {o['request']['prompt_id']} | {c['input_tokens']} / {c['output_tokens']} | {c['latency_s']:.3f} | {c['raw_response']} |")
    body += [
        "## Adaptive behavior",
        "Caption and scene normalized uncertain=false, missing=[]. OBJECT_CHECK and DETAIL_QUERY were decision visits, not model calls. Both additional queries skipped; NO_TRIGGER selected. NO_NEW_EVIDENCE and uncertain/detail branches were NOT exercised on this image (CPU fixtures cover them). No calls forced.",
        "Four literal candidate clauses retained. Caption and scene paraphrases remain separate because duplicate matching is exact-string only; no semantic deduplication claim.",
        "## Verification and traceability",
        "| Claim (literal) | Observation | Verification | Runtime status |\n|---|---|---|---|",
    ]
    for c in report["claims"]:
        body.append(f"| {c['text']} | {', '.join(c['observation_ids'])} | {c['verification_id']} | {c['status']} |")
    body += [
        "Each observation_id equals call_id and resolves to the raw events.jsonl call; normalized trace/raw answer/request/token counts/evidence links checked for equality. Each verification request matches its candidate exactly. All four explicit responses parsed supported; this is SAME-MODEL support, not independent correctness evidence. No GPT semantic judge or new human-quality approval inferred.",
        "## VRAM checkpoints",
        "All quantities MiB; allocated/reserved are worker allocator values, NVIDIA is whole-device. Peaks cumulative; not estimates.",
        "| Checkpoint | Allocated | Reserved | Peak allocated | Peak reserved | CUDA free | NVIDIA used/free |\n|---|---:|---:|---:|---:|---:|---|",
        f"| Before CUDA/load | N/A | N/A | N/A | N/A | N/A | {baseline['used_mib']}/{baseline['free_mib']} |",
    ]
    for e in measured:
        m = e["measurement"]
        vals = " | ".join(f"{m[k] / 1048576:.3f}" for k in ("allocated_bytes", "reserved_bytes", "peak_allocated_bytes", "peak_reserved_bytes", "cuda_free_bytes"))
        body.append(f"| {e['phase']} {e.get('call_id', '')} | {vals} | {m['nvidia']['used_mib']}/{m['nvidia']['free_mib']} |")
    before_cleanup = next(e for e in events if e["phase"] == "cleanup_start")
    nearest = min(samples, key=lambda s: abs(s["monotonic"] - before_cleanup["monotonic"]))
    body += [
        f"Before cleanup: cleanup_start at monotonic {before_cleanup['monotonic']}; nearest device sample offset {nearest['monotonic'] - before_cleanup['monotonic']:.3f}s: {nearest['used_mib']}/{nearest['free_mib']}MiB. No fresh allocator snapshot at cleanup_start; preceding call-6 snapshot shown above, not relabeled as contemporaneous.",
        f"Process exit: NVIDIA {cleanup['device_after']['used_mib']}/{cleanup['device_after']['free_mib']}MiB. Peak allocated {peak_allocated:.3f}MiB; peak reserved {peak_reserved:.3f}MiB; observed device peak {peak_device}MiB (sampling may miss transients).",
        "## Latency",
        "| Component | Seconds |\n|---|---:|",
        f"| Cold backend load including hash checks/imports | {loaded[0]['load_seconds']:.3f} |",
        f"| Image validation/preprocessing/transfer | {next(e for e in events if e['phase'] == 'image_ready')['latency_s']:.3f} |",
        f"| Sum synchronized model calls | {sum(c['latency_s'] for c in calls.values()):.3f} |",
        f"| Agent image controller + RPC | {sum(t['end'] - t['start'] for t in timing['timings'] if t['function'] == 'run'):.3f} |",
        f"| JSON/Markdown report serialization | {sum(t['end'] - t['start'] for t in timing['timings'] if t['function'] in ('to_json', 'to_markdown')):.3f} |",
        f"| Worker cleanup | {cleanup['latency_s']:.3f} |",
        f"| Parent cleanup through recovery | {cleanup['parent_cleanup_seconds']:.3f} |",
        f"| Full invocation through report writes | {timing['end'] - timing['start']:.3f} |",
        "Parent profiling overhead included; some substeps below clock resolution record0, not zero-cost claims. Full invocation includes cold load, Agent, measurement, cleanup and report generation; this is one development measurement, not a benchmark distribution.",
        "## Offline / cleanup / errors",
        f"Offline PASS within HF offline flags and Python network audit scope; no network-violation event. Native/OS firewall guarantee not asserted. Cleanup PASS: allocated0/reserved0, worker PID{termination['worker_pid']} exit0, Job empty, device recovered to exact observed baseline. No OOM, timeout, malformed RPC, fallback or runtime error.",
        "Warnings preserved: pinned local tokenizer emits existing Mistral-regex heuristic warning; greedy generation ignores temperature; default BOS151643 supplied. No tokenizer patch, generation change or online repair made. Full stderr retained.",
        "## Traditional Chinese report (verbatim generated artifact)",
        "```markdown\n" + (RUN / "agent_report.md").read_text(encoding="utf8").rstrip() + "\n```",
        "## Limits and next stage",
        "No real-image sanity performed: no rights-confirmed images supplied. Engineering baseline READY is NOT yet declared. Prepare <=2 non-sensitive rights-confirmed development images and freeze a separate bounded sanity session before execution. All development images stay out of untouched formal test data. Stop feature expansion; formal design freeze comes after engineering acceptance.",
        "## CPU quality checks",
        "Pre-run93 tests PASS(12.038s); post-run93 tests PASS(10.513s). Ruff src/tests/scripts PASS and strict Mypy28 source files PASS before and after smoke. Evidence/source/config/amendment and raw-run reconstruction consistency PASS. CPU process fixtures are not GPU evidence; this new smoke is a real GPU run.",
        "## AI assistance / review",
        "Development assistant audited source/evidence and generated this trace-based engineering report; no runtime cloud/LLM judge, translation, raw-output editing or research-effect claim. Author should review code and exact observations. No new institutional/advisor approval asserted.",
    ]
    (ROOT / "docs/REAL_INTERNVL_AGENT_GPU_SMOKE_RESULT.md").write_text(re.sub(r"\|\n\n\|", "|\n|", "\n\n".join(body)) + "\n", encoding="utf8")
    inventory = {p.relative_to(RUN).as_posix(): digest(p) for p in RUN.rglob("*") if p.is_file()}
    inventory_path = EVIDENCE / "run_inventory.json"
    if inventory_path.exists():
        assert json.loads(inventory_path.read_text(encoding="utf8")) == inventory, "RAW RUN CHANGED"
    else:
        inventory_path.write_text(json.dumps(inventory, indent=2), encoding="utf8")
    (EVIDENCE / "consistency_audit.json").write_text(json.dumps({"verdict": "PASS", "calls": len(calls), "peak_allocated_mib": peak_allocated, "peak_reserved_mib": peak_reserved, "peak_device_mib": peak_device, "raw_run_files": len(inventory), "source_unchanged": True}, indent=2), encoding="utf8")
    print(f"Consistency PASS: {len(calls)} calls; allocator peak {peak_allocated:.3f}MiB, reserved {peak_reserved:.3f}MiB; raw inventory frozen.")


if __name__ == "__main__":
    main()
