# Phase 2 repair1 result — 2026-09-27

**PILOT / EXPLORATORY / NOT FORMAL THESIS RESULT**

## Verdict: CONDITIONAL PASS

Minimal technical feasibility (local CUDA load, image encode, English caption/query,
offline-mode operation, inspected placement, bounded memory and cleanup) passed on one
synthetic development image. **Direct useful Traditional Chinese response remains FAIL**
for the tested prompt. Full product/Agent acceptance is NOT passed. No formal quality,
hallucination, statistical or general worst-case-memory claim follows.

Initial FAIL evidence/report remains unchanged. Repair1 is a new dated exploratory
amendment, not a replacement or omission of failed runs. See [pre-result protocol](PHASE2_REPAIR1_AMENDMENT.md)
and [initial report](MOONDREAM2_GPU_FEASIBILITY_REPORT.md).

## Resolved and unresolved blockers

| Item | Result | Evidence / limit |
|---|---|---|
| Windows status-file race | Resolved in tested path | Pipe transport; supervisor_failure=null; exit 0 |
| Actual worker/descendant termination | PASS | Windows Job ownership; CPU child-tree and timeout tests; real job empty |
| 8.125 MiB cleanup residue | Resolved in this run | cuBLAS clear changed 8519680 allocated bytes to 0; final allocated/reserved both 0 |
| English visual query | PASS on fixture | Both original and single suffix answer red square / blue circle |
| Chinese visual query | FAIL on tested prompt | Both variants repeat question; no informative shape/color answer |
| Duplicate suffix hypothesis | Not supported as sole cause of Chinese failure | Removing second suffix did not fix Chinese; keep upstream default for future integration |

The measured before/after cuBLAS clear supports identifying the previous residue as a
cached library workspace rather than surviving model weights. This is a specific finding;
do not suppress future nonzero cleanup failures. API is private/version-specific, guarded
for availability; no PyTorch upgrade was performed.

The presence of Chinese characters is not a language-quality pass. English answers show
the visual query route works for this fixture, but do not prove all English prompts work.
No third model load, prompt search, translation model or deterministic label substitution
was performed. A Traditional Chinese report schema already exists; its labels alone do
not make embedded English model output a fully Traditional Chinese semantic report.

## Frozen assets, environment and safety

Same model `vikhyatk/moondream2@9a7d4024050840e001defacec2b00727e89149e6`, tokenizer
`moondream/starmie-v1@35192e10a54e36eabe0a7cc57a2c1aab371cafc5`; no acquisition/install/upgrade.
Dense BF16 weights, float32 rotary buffers; torch2.7.1+cu126, CUDA12.6, driver591.86,
RTX3070Ti8192MiB. All original licenses/usage limits remain as in static review.
Controlled repair patch SHA256: `a4eee272862651846144807e553dd7cb661bdfca8565b1ef9bf80ae7ef63e549`.
Original controlled package and weights remain unchanged. New package only exposes the
suffix comparison switch; default is original double suffix, never a silent algorithm change.

One persistent model load; one original 384x256 development geometry fixture; seven calls
including encode. Output128/call, input1024/call, total output<=1024/image; no advanced tools.
Original ceiling6400/reserve1536/provisional estimate6000/allocator cap5400 MiB preserved.
Preflight required >=7536 MiB free and passed. No offload, second model, auto mapping,
planned shared fallback, compilation or formal evaluation.
Parameter/buffer/encoded-cache placement and compute inputs all inspected as cuda:0.
Windows shared spill attribution remains UNKNOWN / OBSERVABILITY LIMITATION.

Offline flags/local tokenizer/controlled code/socket audit used; no network violation.
This validates the configured offline path, not an OS firewall or packet capture guarantee.

## VRAM and synchronized latency

MiB; seconds are synchronized wall time. Per-call times exclude image encode and boundary
measurement. Cold load includes asset hashing and framework setup. Peak reserved resets
per operation; cleanup row retains previous operation peak. Driver samples are device-wide,
not exact per-process peak. Native caption first/warm share the same image cache.

| Stage | seconds | allocated | reserved | peak reserved | CUDA free | device used/free |
|---|---:|---:|---:|---:|---:|---:|
| cuda_baseline | — | 0.000 | 0.000 | 0.000 | 7091.000 | 341 / 7677 |
| model_loaded | 7.438 | 4075.651 | 4194.000 | 4194.000 | 2871.000 | 4561 / 3457 |
| encode | 0.313 | 4222.069 | 4286.000 | 4286.000 | 2763.000 | 4669 / 3349 |
| caption_first | 1.547 | 4222.069 | 4286.000 | 4286.000 | 2763.000 | 4669 / 3349 |
| caption_warm | 1.531 | 4222.069 | 4286.000 | 4286.000 | 2763.000 | 4669 / 3349 |
| query_original_en | 0.250 | 4222.069 | 4286.000 | 4286.000 | 2763.000 | 4669 / 3349 |
| query_original_zh | 1.078 | 4222.069 | 4290.000 | 4290.000 | 2759.000 | 4673 / 3345 |
| query_single_suffix_en | 0.359 | 4222.069 | 4290.000 | 4290.000 | 2759.000 | 4673 / 3345 |
| query_single_suffix_zh | 1.094 | 4222.069 | 4290.000 | 4290.000 | 2759.000 | 4673 / 3345 |
| cleanup_done | 0.110 | 0.000 | 0.000 | 4290.000 | 7049.000 | 383 / 7635 |

Supervisor total session: 14.875 s. Actual worker PID
14700, venv launcher PID 2024; job empty
True, worker exited True.
After process exit device used/free: 182/7836 MiB.
No OOM or budget/timeout violation observed. Sampling cannot exclude transient unobserved peaks.

## Tests, provenance and evidence

68 CPU unit/integration tests passed before this attempt (2.766 s); six changed pilot
modules passed strict Mypy; changed modules/scripts/tests passed Ruff. CPU fixtures mock
GPU metrics and tensors, explicitly separate from actual GPU results above. No deliberate OOM.

Baseline commit `14c675bcaf18f0abb9a099a8def7caf9ad7016b8`; dirty-state and exact runtime source hashes in
`artifacts/phase2-20260927/runs/repair1-pilot/provenance.json`. Events contain raw answers,
token IDs, prompts/settings, placement, memory and times. Pipe transcript, device samples,
Windows counters, stderr and supervisor result are retained beside them. Controlled
source diff/hash manifest is in evidence/controlled_repair1_manifest.json. Backup is
`artifacts/phase2-repair1-evidence-backup/` on the same disk (not disaster recovery).

CPU regeneration: `.venv/Scripts/python.exe scripts/phase2_repair_report.py`.
The already-consumed GPU command (do not repeat or delete run gate):

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
$env:PYTHONIOENCODING = 'utf-8'
.venv/Scripts/python.exe -B -m local_vision_agent.pilot_supervisor_repair --root artifacts/phase2-20260927 --authorize-repair1-pilot
```

## Remaining work / next bounded proposal

No new GPU execution is authorized by this report. The repair1 attempt is consumed.
The smallest further language diagnostic would freeze one English instruction requesting
Traditional Chinese output against the existing Chinese instruction, on the same original
upstream query behavior and same fixture. It needs a separately approved, named one-load
attempt under unchanged limits; existing artifacts suffice, no new download or dependency.
Do not guarantee that a prompt change solves model language capability.
If direct Chinese remains inadequate, present explicit product options to the user rather
than silently adding a translator or changing RD-001. A–D real adapter integration remains
pending; no new claims of completeness/hallucination improvement. 10/31 and 11/1 remain goals.

AI assistance: Codex wrote repair controls/tests/report and reviewed raw English/Chinese
responses; human code, semantic and rights review remains pending. No institutional approval
is inferred. Nothing pushed, published or committed after the authorized Phase1 baseline.

## Raw answers

All strings below are real Moondream2 output from the same loaded model. Query templates,
language and token counts differ exactly as frozen before the run; no answer edits.

### caption_first

```json
{
  "caption": "A vibrant red square and a cool blue circle are positioned on the left and right sides of the image, respectively. The square is intact, with no visible cuts or missing parts. The circle has a smooth, solid color and no discernible holes. The image presents these two shapes against a stark white background, creating a contrast that highlights their distinct colors and forms."
}
```

Input/output tokens: 5/55.

### caption_warm

```json
{
  "caption": "A vibrant red square and a cool blue circle are positioned on the left and right sides of the image, respectively. The square is intact, with no visible cuts or missing parts. The circle has a smooth, solid color and no discernible holes. The image presents these two shapes against a stark white background, creating a contrast that highlights their distinct colors and forms."
}
```

Input/output tokens: 5/55.

### query_original_en

```json
{
  "answer": "The image contains a red square and a blue circle."
}
```

Input/output tokens: 12/8.

### query_original_zh

```json
{
  "answer": "圖片中有哪些形狀？它們各是什麼顏色？"
}
```

Input/output tokens: 64/39.

### query_single_suffix_en

```json
{
  "answer": "There are two shapes in the image: a red square and a blue circle."
}
```

Input/output tokens: 11/12.

### query_single_suffix_zh

```json
{
  "answer": "圖片中有哪些形狀？它們各是什麼顏色？"
}
```

Input/output tokens: 63/39.

