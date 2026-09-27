"""Render the frozen final language diagnostic from retained evidence, CPU only."""

import json
from pathlib import Path


def main() -> None:
    project = Path(__file__).resolve().parents[1]
    root = project / "artifacts/phase2-20260927"
    run = root / "runs/language-final-20260927"
    events = [
        json.loads(line) for line in (run / "events.jsonl").read_text(encoding="utf8").splitlines()
    ]
    provenance = json.loads((run / "provenance.json").read_text())
    supervisor = json.loads((run / "supervisor_result.json").read_text())
    samples = [json.loads(line) for line in (run / "device_samples.jsonl").read_text().splitlines()]
    table, answers = [], []
    measurements = [e["measurement"] for e in events if "measurement" in e]
    for event in events:
        name = event.get("operation", event["phase"])
        if "measurement" in event:
            m = event["measurement"]
            elapsed = event.get("latency_s", event.get("cold_load_s"))
            seconds = "—" if elapsed is None else f"{elapsed:.3f}"
            table.append(
                f"| {name} | {seconds} | {m['allocated_bytes'] / 1048576:.3f} | "
                f"{m['reserved_bytes'] / 1048576:.3f} | {m['peak_allocated_bytes'] / 1048576:.3f} | "
                f"{m['peak_reserved_bytes'] / 1048576:.3f} | {m['nvidia']['used_mib']} / {m['nvidia']['free_mib']} |"
            )
        if "raw_response" in event:
            start = next(
                e for e in events if e["phase"] == "call_start" and e.get("operation") == name
            )
            answers.append(
                f"### {name}\n\nExact prompt:\n\n```text\n{start['prompt']}\n```\n\nRaw output:\n\n```json\n"
                + json.dumps(event["raw_response"], ensure_ascii=False, indent=2)
                + f"\n```\n\nInput/output tokens: {event['input_tokens']}/{event['output_tokens']}; "
                + f"latency {event['latency_s']:.3f} s; malformed={event['malformed']}.\n"
            )
    report = f"""# Final Moondream2 Traditional Chinese diagnostic result — 2026-09-27

**PILOT / EXPLORATORY / NOT FORMAL THESIS RESULT**

Run ID: `language-final-20260927`; actual start: {events[0]["time"]}.
Pre-result protocol: [dated amendment](PHASE2_LANGUAGE_FINAL_AMENDMENT_2026-09-27.md).

## Verdict

- English control: **PASS**. Correct red square and blue circle answer.
- English instruction → Traditional Chinese: **FAIL**. The answer is semantically correct
  for this fixture but entirely English, which is a predeclared failure condition.
- **MOONDREAM2 DIRECT TRADITIONAL CHINESE OUTPUT = REPRODUCIBLE BLOCKER**.
- Cleanup: **PASS**; allocated/reserved both zero; supervisor exit0, no error, job empty.
- Recommendation: **EVALUATE FALLBACK VLM**.

This blocker refers to the tested frozen model/configuration and accumulated diagnostic
evidence, not a proof of impossibility under every conceivable prompt. Initial/Repair1
Chinese echo failures remain unchanged; the final English-instruction response is a
distinct English-only failure. No prompt tuning or further Moondream2 language test follows.
Previously established load/encode/English-query/offline/cleanup successes are preserved.

Next candidate priority, as instructed by user: `OpenGVLab/InternVL3-2B-Instruct`.
It is only a recommendation for separately authorized evaluation; no download, source/model
execution, hardware feasibility claim, integration, or research-direction change occurred.

## Assets, environment and method

Model `vikhyatk/moondream2@9a7d4024050840e001defacec2b00727e89149e6`;
tokenizer `moondream/starmie-v1@35192e10a54e36eabe0a7cc57a2c1aab371cafc5`.
Original reviewed controlled package and local tokenizer, upstream/default query behavior
(double suffix). No repair1 single-suffix patch used. Weights BF16, rotary buffers float32,
parameters/buffers/encoded caches and compute inputs inspected cuda:0.
Same `synthetic-shapes-v1` 384x256 image, hash in retained development_manifest.json.
One persistent load, one encode, exactly two queries. No caption or other prompts.
temperature=0, top_p=1, max_tokens=128, reasoning=false; raw prompts and token IDs saved.
No translation, OpenCC, cloud, second model, output editing, install or asset download.
Python3.11.9 / torch2.7.1+cu126 / CUDA12.6 / driver591.86 / RTX3070Ti8192MiB unchanged.
Original limits and preflight unchanged (estimate6000/ceiling6400/reserve1536/allocator5400 MiB).
No automatic retries, OOM or observed limit violation. Offline local assets/flags/socket
audit active; no network violation. This is not an OS firewall/packet capture proof.

## Memory, latency and cleanup

MiB; synchronized wall seconds. Peak allocator counters reset per operation; cleanup peak
retains the last query peak. Cold load includes validation/import overhead; queries exclude
encode and measurement time. Device samples are whole-GPU observations, not process peaks.

| Stage | seconds | allocated | reserved | peak allocated | peak reserved | device used/free |
|---|---:|---:|---:|---:|---:|---:|
{chr(10).join(table)}

Maximum observed allocator peak allocated: {max(m["peak_allocated_bytes"] for m in measurements) / 1048576:.3f} MiB;
peak reserved: {max(m["peak_reserved_bytes"] for m in measurements) / 1048576:.3f} MiB.
Parent sampled device peak: {max(s["used_mib"] for s in samples)} MiB; min free:
{min(s["free_mib"] for s in samples)} MiB. Sampling cannot exclude unobserved transients.
Windows shared spill remains UNKNOWN / OBSERVABILITY LIMITATION.
cuBLAS workspace cleanup reduced allocated 8,519,680 bytes to zero; cleanup0.125s.
After worker exit: used182/free7836 MiB, same observed baseline.
Supervisor session {supervisor["session_seconds"]:.3f}s; actual PID {supervisor["worker_pid"]};
launcher PID {supervisor["launcher_pid"]}; worker_exited={supervisor["worker_exited"]}; job_empty={supervisor["job_empty"]}.

## Reproducibility and preservation

Baseline commit `{provenance["commit"]}`; dirty state and exact source hashes recorded
before execution in run/provenance.json. No further commit/push/release. All original and
Repair1 evidence unchanged. 71 CPU tests passed before GPU attempt (2.814s); strict Mypy
passed three affected modules; Ruff passed. CPU synthetic tests are not model evidence.

Evidence: `artifacts/phase2-20260927/runs/language-final-20260927/`:
events.jsonl, pipe_events.jsonl, provenance.json, device_samples.jsonl,
device_before.json, windows_before/after.json, stderr.txt, supervisor_result.json.
Prompts, raw answers, generated IDs/counts, decoding settings, placement and resource
measurements are retained per event. Model/tokenizer receipts/hashes remain under
upstream/ and evidence/controlled_manifest.json. Source/evidence backup:
`artifacts/phase2-language-final-evidence-backup/` (same disk, not disaster recovery).

CPU regeneration: `.venv/Scripts/python.exe scripts/phase2_language_report.py`.
Consumed GPU command (do not rerun or delete the exclusive run gate):

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
$env:PYTHONIOENCODING = 'utf-8'
.venv/Scripts/python.exe -B -m local_vision_agent.pilot_supervisor_repair --root artifacts/phase2-20260927 --authorize-final-language
```

Semantic/language adjudication is recorded by Codex from raw strings against the user's
predeclared rules; human review remains pending. No statistical/general-quality claim.
No additional Moondream2 prompt tuning; fallback work requires separate authorization.

## Exact prompts and unedited outputs

{chr(10).join(answers)}
"""
    (project / "docs/PHASE2_LANGUAGE_FINAL_RESULT_2026-09-27.md").write_text(
        report, encoding="utf8"
    )


if __name__ == "__main__":
    main()
