# Moondream2 GPU Feasibility Report — 2026-09-27

**PILOT / EXPLORATORY / NOT FORMAL THESIS RESULT**

## Verdict

**FAIL — initial pilot acceptance is incomplete.** Real CUDA load, encode and caption succeeded.
The Chinese query repeats its question instead of answering; cleanup retains 8.125 MiB allocated;
the supervisor encountered a Windows status-file PermissionError. No retry was performed.
This is not evidence that Moondream2 cannot fit 8GB. RD-001, RQ1–4 and A–D are unchanged.

## Hardware

RTX 3070 Ti 8GB (8192 MiB), Windows WDDM, driver 591.86, driver-supported CUDA 13.1;
PyTorch runtime CUDA 12.6, Python 3.11.9. Actual initial pilot began 2026-09-27T21:27:27.657861+08:00.
Before worker: device used/free 182/7836 MiB. Initial CUDA availability true, one device;
allocator baseline 0 allocated / 0 reserved. Device-used + free need not equal total due to
driver-reserved memory. Preserve NVIDIA and CUDA free measurements separately.

## Artifact

Model: `vikhyatk/moondream2@9a7d4024050840e001defacec2b00727e89149e6` (2025-06-21).
Weights SHA256: `70a7d94c0c8349eb58ed2d9e636ef2d0916960f321ecabeac6354b8ba3d7403f`.
Tokenizer: `moondream/starmie-v1@35192e10a54e36eabe0a7cc57a2c1aab371cafc5`;
tokenizer.json SHA256: `0512fdcac4a5f9e7746cbefce4a468dc93bf0f93f11e701b84f8b31bff199e9c`.
Controlled patch SHA256: `25fb689f094c1984c4e2b61e47736b3425b3402938daa6baf220064dfd8d54d3`.
All individual hashes, source URLs, allowlists and actual-size receipts remain in ignored artifacts.
Recorded HTTP payload: 3,858,337,779 bytes (<5 GB); transport overhead is not packet-metered.
Artifacts plus evidence backup at report generation: 3,867,446,790 bytes (<12 GB).
Backup: `artifacts/phase2-20260927-evidence-backup/`; raw runs, controlled source,
review evidence and source snapshots/hashes; excludes duplicate weights. Same-disk backup
is not disaster recovery. Working-tree source and tool caches are additional small overhead.
No dataset/second model/GGUF. Model README declares Apache-2.0; tokenizer local usage and unresolved
redistribution rights are distinguished in [static review](PHASE2_STATIC_REVIEW.md).

## Environment

No dependencies installed or upgraded. Exact existing versions:

```json
{
  "torch": "2.7.1+cu126",
  "transformers": "4.57.6",
  "numpy": "2.4.6",
  "Pillow": "12.3.0",
  "tokenizers": "0.22.2",
  "safetensors": "0.8.0",
  "accelerate": "NOT INSTALLED",
  "einops": "NOT INSTALLED",
  "pyvips": "NOT INSTALLED",
  "pyvips-binary": "NOT INSTALLED",
  "torchao": "NOT INSTALLED"
}
```

## Safety

Preflight PASS: provisional estimate 6000 MiB + reserve 1536 MiB <= observed free 7836 MiB.
Estimate remains UNMEASURED PILOT ESTIMATE for general workloads; one tiny fixture cannot establish
a worst-case allowance. Planning ceiling 6400 MiB; additional PyTorch allocator cap 5400 MiB.
One model load, one synthetic development image (384x256), five calls including encode.
No offload/auto mapping, quantization, compilation or cloud translation. Batch 1; two internal vision
crops (global/local) are not two user images. All recorded parameters, buffers, encoded KV state,
vision/prefill/decode input tensors are cuda:0. Shared-memory spill remains
**UNKNOWN / OBSERVABILITY LIMITATION**; neither allocator checks nor sampling prove zero spill.
Full limits and actual source hashes are in provenance.json. No intentional OOM test.
CPU tests cover refusal, token/call/image/time limits, synthetic failure and process termination.
The real supervisor error prevents declaring deadline supervision fully validated on Windows.

## Model

Load **PASS**, synchronized cold load 7.953 s, including asset validation and framework import.
Image encode **PASS**, 0.453 s. Dense BF16 weights; float32 rotary buffers and boolean masks by design.

## Caption

**PASS for API execution on this fixture only**. English response describes the red square and blue
circle. No formal semantic scoring or general reliability claim; extra descriptive claims remain raw.

## Query

**FAIL for answering the selected development question**, although both API calls returned normally.
Fixed prompt: `請只用繁體中文回答：圖片中有哪些形狀？它們各是什麼顏色？`
Both responses repeat the question. No English control was included, so this does not isolate
language capability from prompt/template behavior. Upstream duplicated suffix was preserved.

## Traditional Chinese

**FAIL on this prompt**: Chinese characters alone do not establish a useful Traditional Chinese answer.
Caption uses the native normal template and returns English. No translation/second model was added.
Recorded strings below are raw model output, not mock or author corrections.

## Offline

**PASS within the tested offline-mode scope**: pinned local assets, local tokenizer, offline flags,
Python socket audit; no network-violation event. No OS firewall/packet-level isolation was claimed.

## VRAM and Latency

All memory columns are MiB; duration is synchronized wall seconds. Peak counters reset per operation;
cleanup peak columns retain the preceding query peak and are not cleanup-specific peaks.

| Stage | seconds | allocated | reserved | peak allocated | peak reserved | CUDA free | device used/free |
|---|---:|---:|---:|---:|---:|---:|---:|
| cuda_baseline | — | 0.000 | 0.000 | 0.000 | 0.000 | 7091.000 | 341 / 7677 |
| model_loaded | 7.953 | 4075.651 | 4194.000 | 4075.651 | 4194.000 | 2871.000 | 4561 / 3457 |
| encode | 0.453 | 4222.069 | 4286.000 | 4227.778 | 4286.000 | 2763.000 | 4669 / 3349 |
| caption_first | 1.625 | 4222.069 | 4286.000 | 4223.343 | 4286.000 | 2763.000 | 4669 / 3349 |
| caption_warm | 1.641 | 4222.069 | 4286.000 | 4223.343 | 4286.000 | 2763.000 | 4669 / 3349 |
| query_first | 1.125 | 4222.069 | 4290.000 | 4226.570 | 4290.000 | 2759.000 | 4673 / 3345 |
| query_warm | 1.141 | 4222.069 | 4290.000 | 4226.570 | 4290.000 | 2759.000 | 4673 / 3345 |
| cleanup_done | 0.109 | 8.125 | 20.000 | 4226.570 | 4290.000 | 7029.000 | 403 / 7615 |

Parent sampled peak device use: 4673 MiB;
minimum sampled dedicated free: 3345 MiB.
These are discrete device-wide samples, not an exact per-process driver peak. WDDM process VRAM is N/A.
First/warm calls share a persistent model and encoded image; encode is excluded from caption/query
times. Two identical greedy calls are not repetitions for statistics. No confidence intervals.

## Cleanup

**FAIL for in-worker allocator-empty acceptance**, despite cleanup completing in 0.109 s:
8.125 MiB allocated / 20 MiB reserved remain. Exact retaining object is not established.
Process exit recovery **PASS observed**: worker and venv launcher no longer exist, device returns
to 182 MiB used / 7836 MiB free. Windows venv launcher PID 16424 differs from actual
Python worker PID 22252; production supervision must control the entire process tree.
Parent reported `SUPERVISOR_ERROR:PermissionError:[Errno 13] Permission denied: 'E:\\AI Agent影像辨識專案\\artifacts\\phase2-20260927\\runs\\initial-pilot\\status.json'`. Worker exit code was 1.

## Blockers and smallest proposed correction

1. Status-file replace/read sharing race: use a pipe or append-only event reader; preserve deadlines
   during transient reads and test Windows sharing failures on CPU.
2. Process supervision: bind launcher/worker descendants to a Windows Job Object (or validated
   equivalent) and test termination of a child tree without GPU.
3. Cleanup: isolate tensor-owning scopes, inspect remaining live CUDA tensors and library workspace
   ownership. Do not merely weaken the allocator-empty assertion; 8.125 MiB cause remains UNKNOWN.
4. Query/Chinese: inspect the fixed upstream prompt-token path on CPU, then propose a separately
   versioned, bounded English-control/Chinese query pilot. Do not silently change the preserved run.

No code-after-result repair or second GPU run was performed. Preserve negative evidence.

## Traceability, reproduction and next step

Baseline commit: `14c675bcaf18f0abb9a099a8def7caf9ad7016b8`. Phase 2 changes are dirty/uncommitted; exact source hashes
and dirty state are saved in runs/initial-pilot/provenance.json. Evidence:
`artifacts/phase2-20260927/runs/initial-pilot/` (events, device samples, stdout/stderr, Windows counters,
supervisor result); initial hardware/dependencies/review in `evidence/`.
Synthetic fixture is development-only, project-generated geometry; no untouched test set exists.

Original command (already consumed its single-attempt directory; **do not rerun/delete the gate**):

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
$env:PYTHONIOENCODING = 'utf-8'
.venv/Scripts/python.exe -B -m local_vision_agent.pilot_supervisor --root artifacts/phase2-20260927 --authorize-initial-pilot
```

Report regeneration is CPU-only: `.venv/Scripts/python.exe scripts/phase2_report.py`.
59 CPU tests pass (2.018 s); Ruff passes for six new implementation/test files; strict Mypy passes
three pilot modules. An initial test run failed due to omitted UTF-8 output environment; rerun with
the documented encoding passed. CPU tests use synthetic safety failures, not actual OOM evidence.

Next authorization needed: narrowly scoped blocker repairs plus **one newly identified retry run**
after CPU checks, retaining the same pinned model, 6000/6400/1536 MiB budget, 5400 MiB allocator cap,
one load, <=3 development images/24 calls/30 minutes and all existing token/time/image limits.
No additional download is currently needed; no dependency change proposed. Any extra acquisition
requires its own remaining byte/disk accounting and permission. Prompt changes need a dated amendment.
Full real Agent A–D adapter integration remains pending; Phase 1 A–D is still mock-only.
Detect/point/formal evaluation/release remain separately gated. No push or publication.
10/31 core-code and 11/1 acceptance remain targets, not guarantees.

AI assistance: Codex produced pilot controls/tests/static review/report; raw outputs came from local
Moondream2. Human code/rights/language review is still pending. No institutional approval is inferred.

## Raw development outputs

Decoding: max_tokens=128, temperature=0, top_p=1, reasoning=false. Caption template=normal.
Token counts are instrumented upstream generated IDs; raw strings and IDs are retained in events.

### caption_first

```json
{
  "caption": "A vibrant red square and a cool blue circle are positioned on the left and right sides of the image, respectively. The square is intact, with no visible cuts or missing parts. The circle has a smooth, solid color and no discernible holes. The image presents these two shapes against a stark white background, creating a contrast that highlights their distinct colors and forms."
}
```

Input/output tokens: 5/55; contains_cjk=False; malformed=False.

### caption_warm

```json
{
  "caption": "A vibrant red square and a cool blue circle are positioned on the left and right sides of the image, respectively. The square is intact, with no visible cuts or missing parts. The circle has a smooth, solid color and no discernible holes. The image presents these two shapes against a stark white background, creating a contrast that highlights their distinct colors and forms."
}
```

Input/output tokens: 5/55; contains_cjk=False; malformed=False.

### query_first

```json
{
  "answer": "圖片中有哪些形狀？它們各是什麼顏色？"
}
```

Input/output tokens: 64/39; contains_cjk=True; malformed=False.

### query_warm

```json
{
  "answer": "圖片中有哪些形狀？它們各是什麼顏色？"
}
```

Input/output tokens: 64/39; contains_cjk=True; malformed=False.

