"""CPU-only evidence report. Semantic adoption requires a separate human review record."""

import json
from pathlib import Path


def main() -> None:
    project = Path(__file__).resolve().parents[1]
    run = project / "artifacts/internvl3-20260928/runs/INTERNVL3_AGENT_CAPABILITY_PILOT_20260928"
    evidence = project / "artifacts/internvl3-capability-20260928/evidence"
    events = [
        json.loads(line) for line in (run / "events.jsonl").read_text(encoding="utf8").splitlines()
    ]
    done = [e for e in events if e["phase"] == "call_done"]
    expected = ["control", "scene", "objects", "detail", "verification"]
    assert [e["operation"] for e in done] == expected
    starts = {e["operation"]: e for e in events if e["phase"] == "call_start"}
    supervisor = json.loads((run / "supervisor_result.json").read_text(encoding="utf8"))
    provenance = json.loads((run / "provenance.json").read_text(encoding="utf8"))
    before = json.loads((run / "device_before.json").read_text(encoding="utf8"))
    after = supervisor["device_after"]
    cleanup = next(e for e in events if e["phase"] == "cleanup_done")
    assert (
        cleanup["measurement"]["allocated_bytes"] == cleanup["measurement"]["reserved_bytes"] == 0
    )
    technical = (
        supervisor["exit_code"] == supervisor["worker_reported_exit"] == 0
        and supervisor["job_empty"]
        and supervisor["worker_exited"]
        and supervisor["supervisor_failure"] is None
        and after["used_mib"] <= before["used_mib"] + 64
        and after["free_mib"] >= before["free_mib"] - 64
        and not any(
            e["phase"] in {"failure", "network_violation", "cleanup_failure"} for e in events
        )
    )
    assert technical
    review_path = evidence / "human_review.json"
    review = json.loads(review_path.read_text(encoding="utf8")) if review_path.exists() else None
    accepted = bool(
        review
        and review.get("reviewer_kind") == "human_user"
        and review.get("run_id") == run.name
        and review.get("all_capabilities_and_chinese_usable") is True
    )
    lines = [
        """# InternVL3 Agent Capability Result — 2026-09-28

**PILOT / EXPLORATORY / NOT FORMAL THESIS RESULT**

One NEW offline session completed: control + scene + objects + detail + verification.
Engineering execution safety PASS; no semantic scoring controlled scheduling.
No new model/download/dependency/precision/preprocessing/prompt changes or retries.
The previous INTERNVL3_INITIAL_GPU_PILOT remains immutable, including its NOT RUN probes
and lexical scheduling false-negative. This report never changes that historical verdict.

## Provenance and frozen settings

Model/tokenizer/config/template: OpenGVLab/InternVL3-2B-Instruct,
`f6c7b60375759170fd49f5e9e298e2178485c5ba`. Same verified weights/controlled source patch.
Original384x256 synthetic development fixture -> one448x448 tile; batch1/BF16/cuda:0/eager.
No CPU/disk offload, automatic mapping or planned shared-memory fallback.
Greedy temperature0/do_sample=False/num_beams1/max_new_tokens128/use_cache=True;
EOS151645/pad151643/model-default BOS151643, unchanged system/chat template.
Same6000MiB planning estimate,6400MiB ceiling,1536MiB reserve and5400MiB allocator cap.
Load180s/call60s/image300s/cleanup10s/session1800s; exactly one image/five calls.
Python3.11.9/torch2.7.1+cu126/Transformers4.57.6 unchanged; dependencies unchanged.

[Prospective amendment and human rubric](INTERNVL3_AGENT_CAPABILITY_PILOT_AMENDMENT_2026-09-28.md).
Raw evidence: artifacts/internvl3-20260928/runs/INTERNVL3_AGENT_CAPABILITY_PILOT_20260928/.
Full rendered templates, token IDs, execution receipts, placement, status/stop reasons,
errors/warnings and timestamps in events.jsonl; independent parent trace in pipe_events.jsonl.
Source hashes/commit/dirty state in provenance.json; pre-run source snapshot and authorization
under artifacts/internvl3-capability-20260928/evidence/. No GPT/cloud semantic judge.
""",
        f"\nRun ID: `{run.name}`. Started `{provenance['started']}`.\nCommit `{provenance['commit']}`.\n",
        "\nRun-start dirty state:\n\n```text\n" + provenance["dirty_state"] + "\n```\n",
        "\n## Exact prompts and raw responses\n",
    ]
    for e in done:
        lines += [
            f"\n### {e['operation']}\n",
            "Prompt:\n\n```text\n" + starts[e["operation"]]["prompt"] + "\n```\n",
            "Raw response (unmodified):\n\n```text\n" + e["raw_response"] + "\n```\n",
            f"Worker status `{e['worker_status']}`, stop `{e['stop_reason']}`; engineering receipt accepted. Semantic rating: HUMAN REVIEW, never an execution gate.\n",
        ]
    lines += [
        "\n## Latency and tokens\n\nGPU synchronization before/after operations; query totals include telemetry overhead. Every call recomputes visual features and uses fresh KV. Warm compute is not cached replay.\n\n",
        "| Query | input tokens | output tokens | visual s | generation s | query s |\n|---|---:|---:|---:|---:|---:|\n",
    ]
    for e in done:
        lines.append(
            f"| {e['operation']} | {e['input_tokens']} | {e['output_tokens']} | {e['visual_s']:.3f} | {e['generation_s']:.3f} | {e['latency_s']:.3f} |\n"
        )
    for phase in ("model_loaded", "image_ready", "cleanup_done"):
        e = next(e for e in events if e["phase"] == phase)
        lines.append(f"\n{phase}: {e.get('cold_load_s', e.get('latency_s')):.3f}s.\n")
    lines.append(
        f"\nTotal generated tokens{sum(e['output_tokens'] for e in done)};5calls;1image;1load;session{supervisor['session_seconds']:.3f}s. Load includes asset verification/framework setup, not transfer alone.\n"
    )
    measured = [e for e in events if "measurement" in e]
    lines.append(
        "\n## VRAM checkpoints\n\nMiB; peaks cumulative from CUDA baseline across load and all queries. Device telemetry is whole-device, not exact per-process attribution.\n\n| Stage | allocated | reserved | peak allocated | peak reserved | CUDA free | NVIDIA used/free |\n|---|---:|---:|---:|---:|---:|---:|\n"
    )
    for e in measured:
        m = e["measurement"]
        values = [
            m[k] / 1048576
            for k in (
                "allocated_bytes",
                "reserved_bytes",
                "peak_allocated_bytes",
                "peak_reserved_bytes",
                "cuda_free_bytes",
            )
        ]
        lines.append(
            f"| {e['phase']} {e.get('operation', '')} | "
            + " | ".join(f"{v:.3f}" for v in values)
            + f" | {m['nvidia']['used_mib']}/{m['nvidia']['free_mib']} |\n"
        )
    lines.append(
        f"\nBefore process: used/free{before['used_mib']}/{before['free_mib']}MiB. After exit: {after['used_mib']}/{after['free_mib']}MiB.\n"
    )
    lines.append("""
## Lifecycle / offline / cleanup

PASS: all inspected model parameters/buffers, vision inputs/projected features, text inputs
and returned28-layer K/V on cuda:0. Preflight and telemetry bounds passed. No OOM/error.
PASS in tested path: offline flags and Python audit before heavy imports, zero network
violations; no corrective download. This is not an OS-firewall/native-network proof.
PASS: allocated=reserved=0 after reference/workspace/cache cleanup, worker exit0,
Windows Job empty, no supervisor error, observed device baseline recovered.
Windows shared-memory spill remains **UNKNOWN / OBSERVABILITY LIMITATION**.

Warnings retained verbatim in stderr: same null-version Mistral-regex heuristic,
temperature inactive in greedy mode, BOS default151643. No warning-triggered patch.
See previous static warning explanation; original tokenizer/source unchanged.

## Tests / interpretation / limits

Before GPU:83 CPU tests PASS(3.633s), Ruff PASS, strict Mypy22 modules PASS.
Safety tests intentionally accept varied/uncertain/incorrect wording while rejecting empty,
malformed, exceptional, unhealthy, late or over-budget responses. Windows CPU integration
checks a persistent one-load/five-call process and forced timeout/process-tree cleanup.
These fixtures are mocked engineering inputs, never visual-recognition evidence.

Human review is separate and post-run. Verification text is only a model response to a
claim; even if judged usable it is not independent truth or evidence of reduced hallucination.
No formal dataset, A–D experiment, real-image sanity run or RQ2–RQ4 success claim.
The fixture and one-tile distortion limit generalization; final preprocessing must be frozen
identically for A/B/C/D before formal experiments. No new model shopping.

Regenerate CPU-only: `.venv/Scripts/python.exe scripts/internvl_capability_report.py`.
Do not rerun the consumed supervisor gate. AI assistance: safety code/tests/report generation;
human capability decision must be recorded separately, without substituting AI ratings.
""")
    (project / "docs/INTERNVL3_AGENT_CAPABILITY_RESULT.md").write_text(
        "".join(lines), encoding="utf8"
    )
    verdict = (
        "ADOPT INTERNVL3-2B-INSTRUCT AS PRIMARY VLM CANDIDATE"
        if accepted
        else "PENDING HUMAN REVIEW — no adoption verdict assigned"
    )
    decision = f"""# InternVL3 Adoption Decision — 2026-09-28

PILOT / EXPLORATORY / NOT FORMAL THESIS RESULT

**{verdict}**

Evidence: [capability result](INTERNVL3_AGENT_CAPABILITY_RESULT.md), immutable initial
[feasibility report](INTERNVL3_2B_GPU_FEASIBILITY_REPORT.md), and frozen capability amendment.
Engineering safety, offline, five completed queries, placement and cleanup PASS.
Semantic/capability review is human-only and cannot be inferred from process exit0.

"""
    if review:
        decision += (
            "Human record (user statement, no AI semantic grading):\n\n```json\n"
            + json.dumps(review, ensure_ascii=False, indent=2)
            + "\n```\n"
        )
    else:
        decision += "Human review has been requested with all five raw outputs. No response is recorded yet.\nDo not substitute CONDITIONAL/REJECT for missing review or claim ADOPT without it.\nAdapter integration remains conditional and has not begun.\n"
    decision += "\nThis is engineering/development adoption only; not RQ2–RQ4 success. Same-model verification is not ground truth. No third model, formal experiment, push or release. PUBLIC RELEASE RIGHTS remains UNKNOWN.\n"
    (project / "docs/INTERNVL3_ADOPTION_DECISION.md").write_text(decision, encoding="utf8")


if __name__ == "__main__":
    main()
