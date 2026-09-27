# Final Moondream2 Traditional Chinese diagnostic result — 2026-09-27

**PILOT / EXPLORATORY / NOT FORMAL THESIS RESULT**

Run ID: `language-final-20260927`; actual start: 2026-09-27T21:59:19.789593+08:00.
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
| cuda_baseline | — | 0.000 | 0.000 | 0.000 | 0.000 | 341 / 7677 |
| model_loaded | 7.578 | 4075.651 | 4194.000 | 4075.651 | 4194.000 | 4561 / 3457 |
| encode | 0.312 | 4222.069 | 4286.000 | 4227.778 | 4286.000 | 4669 / 3349 |
| english_control | 0.406 | 4222.069 | 4286.000 | 4223.890 | 4286.000 | 4669 / 3349 |
| english_instruction_traditional_chinese | 0.641 | 4222.069 | 4286.000 | 4224.437 | 4286.000 | 4669 / 3349 |
| cleanup_done | 0.125 | 0.000 | 0.000 | 4224.437 | 4286.000 | 383 / 7635 |

Maximum observed allocator peak allocated: 4227.778 MiB;
peak reserved: 4286.000 MiB.
Parent sampled device peak: 4669 MiB; min free:
3349 MiB. Sampling cannot exclude unobserved transients.
Windows shared spill remains UNKNOWN / OBSERVABILITY LIMITATION.
cuBLAS workspace cleanup reduced allocated 8,519,680 bytes to zero; cleanup0.125s.
After worker exit: used182/free7836 MiB, same observed baseline.
Supervisor session 10.000s; actual PID 7476;
launcher PID 2412; worker_exited=True; job_empty=True.

## Reproducibility and preservation

Baseline commit `14c675bcaf18f0abb9a099a8def7caf9ad7016b8`; dirty state and exact source hashes recorded
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

### english_control

Exact prompt:

```text
What shapes are in the image, and what color is each shape?
```

Raw output:

```json
{
  "answer": "There are two shapes in the image: a red square and a blue circle."
}
```

Input/output tokens: 15/12; latency 0.406 s; malformed=False.

### english_instruction_traditional_chinese

Exact prompt:

```text
Answer the following question in Traditional Chinese only. Do not repeat the question. What shapes are in the image, and what color is each shape?
```

Raw output:

```json
{
  "answer": "The shapes in the image are a red square and a blue circle. The red square is square-shaped and the blue circle is circular."
}
```

Input/output tokens: 25/22; latency 0.641 s; malformed=False.

