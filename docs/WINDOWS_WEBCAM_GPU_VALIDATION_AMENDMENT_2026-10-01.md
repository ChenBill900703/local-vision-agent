# Windows Webcam GPU validation amendment — 2026-10-01

**PROSPECTIVE / FROZEN / NOT EXECUTED / PENDING EXPLICIT AUTHORIZATION**
**DEVELOPMENT / EXPLORATORY / NOT FORMAL THESIS RESULT**
Run ID: `WINDOWS_WEBCAM_GPU_VALIDATION_20261001_V1` (UNCONSUMED).

## Purpose and scope

Validate only the implemented Windows still-frame application on ONE local physical Webcam,
ONE rights-confirmed non-sensitive scene, ONE persistent InternVL load and at most THREE
independent Method D frame analyses. Attempt to obtain three records; any failure stops with
fewer records and is not retried/replaced. No manual image analysis in this session, no extra
image, camera, prompt search, model, dataset, installation, tuning or formal experiment.
Existing engineering baseline refers to the earlier path; this amendment supplies no new PASS.

## Frozen implementation and environment

Base HEAD: `cf4ec1455b8a12026d0ebd849e3a6cb1b9514cce`, authorized dirty implementation.
Exact source/config/tests/scripts/locks and all installed versions are pinned in
`WINDOWS_UI_CPU_READY_MANIFEST_2026-10-01.json`.
Manifest SHA256: `11e09549fa3d076415e79984948bc0546f8b971d97a95e438e7aaed3b7933920`.
Freeze this manifest and compare bytes before execution; do not silently regenerate it to
accept drift. Record HEAD, dirty status/diff and this amendment hash in new ignored evidence.
Any executable/config/model/dependency drift means STOP BEFORE LOAD and a prospective revision.
Documentation-only changes must be identified and recorded; never substitute commit identity
for the actual dirty source hashes. No future commit hash is invented.

Model/tokenizer: OpenGVLab/InternVL3-2B-Instruct revision
`f6c7b60375759170fd49f5e9e298e2178485c5ba`; existing reviewed local controlled code only.
Validate all assets/transformers code against existing runtime_manifest (its SHA is pinned in
CPU manifest), not merely filename presence. Config `configs/agent_internvl_development.toml`
SHA256 `05b5d92a28659630cd5a5e2f9593ffd06241ab2c4f7a5379c82f7e43f41f20d1`.
Qt four-package set6.8.3; existing inference distributions unchanged. No new download.

## Authorization and preflight gates (not execution permission)

Future user approval must authorize ONE physical camera/non-sensitive scene, local capture
and transient normalized files, GPU/driver queries, CUDA initialization, one persistent model
load and <=3 frames under this amendment, plus final resource/cleanup checks. The author must
confirm no private documents, credentials, identifiable private screen content, avoidable
unconsented people or identity-recognition task in view. Save frames OFF; hashes/provenance,
raw model text and telemetry remain private. Do not upload frames to any development assistant.

Before capture/load: reserve exclusive new run directory/consumed gate (never reuse), record
camera identifier/Qt device selection and hardware/driver status. Verify source/dependency/
config/assets hashes, full CPU150 tests, Ruff, strict Mypy and pip check; archive exact logs.
Check process/available RAM/disk and existing GPU guard: RTX3070Ti8GB, estimate6000MiB,
process planning ceiling6400MiB and1536MiB reserve after estimate. Existing post-CUDA-init
check and5400MiB allocator fraction remain mandatory before weights. Safety refusal, wrong
device, failed camera permission, unexpected drift or occupied run gate STOP with no load/retry.
No CPU/disk offload, auto device map, shared-memory fallback or second load.

## Execution prescription — do not run in the CPU implementation phase

Use application real mode with a NEW ignored storage directory tied to run ID, options
`--authorize-development-gpu --max-frames 3 --max-session-seconds 1800 --interval-seconds 5`.
Start only the selected physical Webcam auto mode once. No manual input or restarting auto.
Capture1 -> analyze/persist/display -> wait5s -> capture2 -> analyze/persist/display -> wait5s
-> capture3 -> analyze/persist/display -> stop -> close application. Never submit a fourth.
Default save-frame OFF stays OFF; only analyzed stills are transiently written, no preview
recording. A frame is not supplied by a pre-existing derivative or by FakeCamera.

Each source is strictly validated -> provenance/SHA/dimensions -> existing EXIF/RGB/aspect512
normalization -> unchanged single448 preprocessing -> InternVL -> fresh Method D -> report.
BF16/cuda:0/batch1/eager/P1, frozen prompts and greedy decoding unchanged. <=8 calls and
iterations/frame, <=128 output tokens/call, <=1024 input tokens/call, <=1024 output tokens/frame.
Total <=24 calls/3 frames, no extra verification beyond remaining budget.
Original source <=32MiB/32MP/10000edge JPEG/PNG, model-bound input <=512edge/262144pixels.
Existing load180s/call60s/image300s/cleanup10s/global worker1800s ceilings unchanged; app1800s
ceiling includes load, waits and capture. Global model timer never resets between frames.
Draining active bounded work is distinguished from cleanup10s. Failures stop; no retry/reload.
`COMPLETED_WITH_PARTIAL_VERIFICATION / VERIFICATION_BUDGET_EXHAUSTED` is acceptable bounded
completion only when accurately retained; runtime failures/partial errors stop subsequent frames.

## Required observations and acceptance

Preserve exact source commit+dirty diff+manifest/config/dependency/model identities, run ID,
selected physical camera, capture UTC and monotonic timings, source/normalized hashes and
dimensions, retained metadata, each input/session/call identity, state trace, raw responses,
exact prompts/token IDs/token counts, claims/verification/coverage/unresolved-by-budget,
truncation/stop reasons, per-frame and model/load latency with explicit timing boundaries.
Retain parent trace, worker events, offline denial audit, placement, preflight/periodic resource
snapshots, per-image allocated/reserved peaks and after-image reset measurements. Fake/missing
measurements are not admissible physical evidence. No inference based only on readable GUI text.

Technical PASS requires exactly3 independent reports, one load/worker PID, no overlapping
analysis, no fourth capture, each next capture >=5s after preceding persisted/displayed result,
fresh Agent observations/claims/verification/evidence/counters/trace and acknowledged image
clear before next image, unchanged global watchdog, valid histories reloadable without inference,
no OOM/timeout/guard/placement/offline/privacy violations. Verify reset source state via logs;
similar scene content alone cannot prove or disprove state leakage. End-image allocated memory
must return to post-load allocated baseline (no retained image tensors); any positive persistent
excess or unexplained growth is unresolved/fail pending separate review, not silently tolerated.
Same-model supported verdicts are not independent truth or a semantic PASS criterion.

After final close verify camera is stopped/detached/released, per-image temporary PNG/derivative
absent with metadata intact, allocator allocated/reserved zero after model unload, worker exited,
Job/process tree empty and device returned to observed baseline using existing recovery checks.
Camera release must be explicitly checked locally; no extra inference frame or second model.
Preserve cleanup failure truthfully. If blocked, stop and retain partial evidence, no second run.

## Closeout and stop

Hash immutable raw run files and create a separate local evidence backup; never amend raw output.
Run post-run CPU/Ruff/Mypy/pip check, write dated result separating technical from semantic
status, and present ALL raw visual responses/verification outcomes for author DEVELOPMENT HUMAN
SANITY REVIEW. Do not use GPT to judge private frames or silently fix Chinese answers.
Technical outcomes: `WINDOWS WEBCAM GPU VALIDATION = TECHNICAL PASS / HUMAN REVIEW PENDING`
or `WINDOWS WEBCAM GPU VALIDATION = FAIL` (include exact blocker/partial coverage).
Do not claim the new application GPU READY before required human review. Stop; no extra runs,
formal comparisons, release, commit/push, or feature expansion is granted by this amendment.
