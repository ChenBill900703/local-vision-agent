# InternVL3 Agent Capability Result — 2026-09-28

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

Run ID: `INTERNVL3_AGENT_CAPABILITY_PILOT_20260928`. Started `2026-09-28T14:30:34.213804+08:00`.
Commit `cb171216dac7f7fd99aa6b9a2776de4bd1311af4`.

Run-start dirty state:

```text
M AGENTS.md
 M README.md
 M docs/DELIVERY_PLAN.md
 M docs/ENVIRONMENT.md
 M src/local_vision_agent/pilot_supervisor_repair.py
?? SESSION_HANDOFF.md
?? docs/INTERNVL3_2B_GPU_FEASIBILITY_REPORT.md
?? docs/INTERNVL3_AGENT_CAPABILITY_PILOT_AMENDMENT_2026-09-28.md
?? docs/INTERNVL3_PILOT_AMENDMENT_2026-09-28.md
?? docs/INTERNVL3_STATIC_REVIEW_2026-09-28.md
?? scripts/internvl_acquire.py
?? scripts/internvl_prepare.py
?? scripts/internvl_report.py
?? src/local_vision_agent/capability_gate.py
?? src/local_vision_agent/internvl_policy.py
?? src/local_vision_agent/internvl_worker.py
?? tests/test_capability_gate.py
?? tests/test_internvl_policy.py
```

## Exact prompts and raw responses

### control
Prompt:

```text
What shapes are in the image, and what color is each shape?
```
Raw response (unmodified):

```text
The image contains two shapes: a red square on the left and a blue circle on the right.
```
Worker status `healthy`, stop `eos`; engineering receipt accepted. Semantic rating: USER HUMAN REVIEW PASS, never an execution gate.

### scene
Prompt:

```text
這張圖片主要是什麼場景？
```
Raw response (unmodified):

```text
這張圖片主要展示了一個紅色的正方形和一個藍色的圓形。背景是白色的。
```
Worker status `healthy`, stop `eos`; engineering receipt accepted. Semantic rating: USER HUMAN REVIEW PASS, never an execution gate.

### objects
Prompt:

```text
請列出畫面中明顯可見的主要物件。
```
Raw response (unmodified):

```text
畫面中有一個紅色的正方形和一個藍色的圓形。
```
Worker status `healthy`, stop `eos`; engineering receipt accepted. Semantic rating: USER HUMAN REVIEW PASS, never an execution gate.

### detail
Prompt:

```text
背景中還有哪些明顯且可以確認的物件？
```
Raw response (unmodified):

```text
在這張圖片中，背景中沒有明顯且可以確認的物件。
```
Worker status `healthy`, stop `eos`; engineering receipt accepted. Semantic rating: USER HUMAN REVIEW PASS, never an execution gate.

### verification
Prompt:

```text
敘述：圖片中有紅色正方形。請重新檢查圖片，這個敘述是否能由圖片直接支持？若不能確定，請明確說無法確定。
```
Raw response (unmodified):

```text
圖片中有紅色正方形。
```
Worker status `healthy`, stop `eos`; engineering receipt accepted. Semantic rating: USER HUMAN REVIEW PASS, never an execution gate.

## Latency and tokens

GPU synchronization before/after operations; query totals include telemetry overhead. Every call recomputes visual features and uses fresh KV. Warm compute is not cached replay.

| Query | input tokens | output tokens | visual s | generation s | query s |
|---|---:|---:|---:|---:|---:|
| control | 318 | 21 | 0.500 | 1.297 | 1.844 |
| scene | 312 | 25 | 0.031 | 1.015 | 1.093 |
| objects | 315 | 19 | 0.047 | 0.766 | 0.844 |
| detail | 315 | 17 | 0.047 | 0.688 | 0.766 |
| verification | 342 | 8 | 0.031 | 0.344 | 0.422 |

model_loaded: 29.656s.

image_ready: 0.015s.

cleanup_done: 0.188s.

Total generated tokens90;5calls;1image;1load;session36.344s. Load includes asset verification/framework setup, not transfer alone.

## VRAM checkpoints

MiB; peaks cumulative from CUDA baseline across load and all queries. Device telemetry is whole-device, not exact per-process attribution.

| Stage | allocated | reserved | peak allocated | peak reserved | CUDA free | NVIDIA used/free |
|---|---:|---:|---:|---:|---:|---:|
| cuda_baseline  | 0.000 | 0.000 | 0.000 | 0.000 | 7091.000 | 341/7677 |
| model_loaded  | 3985.220 | 4680.000 | 4429.578 | 4680.000 | 2385.000 | 5047/2971 |
| image_ready  | 3986.863 | 4680.000 | 4429.578 | 4680.000 | 2385.000 | 5047/2971 |
| visual_done control | 3995.743 | 4682.000 | 4429.578 | 4682.000 | 2367.000 | 5065/2953 |
| call_done control | 4004.985 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5073/2945 |
| visual_done scene | 3995.743 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5073/2945 |
| call_done scene | 4004.931 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5073/2945 |
| visual_done objects | 3995.743 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5073/2945 |
| call_done objects | 4004.849 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5073/2945 |
| visual_done detail | 3995.743 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5073/2945 |
| call_done detail | 4004.794 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5073/2945 |
| visual_done verification | 3995.744 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5073/2945 |
| call_done verification | 4005.287 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5073/2945 |
| before_cleanup  | 8.125 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5073/2945 |
| cleanup_done  | 0.000 | 0.000 | 4429.578 | 4688.000 | 7047.000 | 385/7633 |

Before process: used/free182/7836MiB. After exit: 182/7836MiB.

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
