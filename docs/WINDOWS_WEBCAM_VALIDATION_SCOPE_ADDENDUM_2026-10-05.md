# Prospective Webcam validation scope addendum — 2026-10-05

NOT EXECUTED / NO GPU AUTHORIZATION GRANTED. DEVELOPMENT ONLY / NOT FORMAL THESIS RESULT.
New proposed run ID `WINDOWS_APP_MANUAL_WEBCAM_20261005_V1` is UNCONSUMED.
The old `WINDOWS_WEBCAM_GPU_VALIDATION_20261001_V1` and its frozen amendment/manifest remain
immutable NOT EXECUTED history. Its source hash no longer matches the authorized export/UI
completion, and its camera-only scope excludes the subsequently requested manual test.
Do not reuse the old run ID or silently re-freeze its manifest.

Proposed replacement: ONE application/model-worker lifetime, ONE rights-confirmed manual image
then ONE physical Webcam session on ONE non-sensitive scene, <=3 camera frames, one model load,
no retry. <=4 total analyses and <=32 calls (8 per analysis), <=128output tokens/call and
<=1024output tokens/image. Auto capture max3/5s wait/1800s; original global worker1800s,
load180/call60/image300/cleanup10 timeouts stay unchanged across manual+camera. No extra manual
image/session/frame or automatic model reload. Preview close/reopen is camera-only, no inference.

Exact source: base HEAD cf4ec1455b8a12026d0ebd849e3a6cb1b9514cce with authorized dirty tree.
New frozen source/config/tests/locks/distributions: THESIS_DATA_EXPORT_CPU_MANIFEST_2026-10-05.json
SHA256 `f83fc8bf5b38c4f59d19f575c535a2db4cad5aad067e39343c0c6ca87df67df3`. Record actual HEAD/dirty diff at execution; STOP on executable/config/model/
dependency drift. Previous CPU180tests/Ruff/strictMypy39/pipcheck allPASS; rerun before/after GPU.
Original InternVL3-2B-Instruct/tokenizer f6c7b60375759170fd49f5e9e298e2178485c5ba,
reviewed assets/remote code hashes, BF16 cuda:0 batch1 P1 single448, existing prompts/Agent/FIFO,
source32MiB/32MP/10000edge and normalized512 limits, offline enforcement, guard estimate6000MiB,
process ceiling6400MiB/reserve1536MiB/allocator5400MiB remain unchanged. No offload/auto mapping/
shared-memory fallback/download/newdependency. Source/code hash is not evidence of hardware PASS.

Future explicit authorization must cover GPU/driver/resource queries, CUDA initialization and
ONE persistent load, manual image rights and local physical camera/scene/ephemeral capture,
<=3 Webcam analyses, cleanup/device recovery checks. Save frame OFF; raw text/telemetry retained,
private images not committed/uploaded. Approval is separate from required author semantic review.

Use the physical checklist for order. Prospective real launch parameters (DO NOT RUN now):
`--authorize-development-gpu --max-frames 3 --max-session-seconds 1800 --interval-seconds 5`
with a NEW ignored storage directory matching run ID. No real flag used in this CPU completion.

Retain preflight/resources/offline/placement, exact prompts/token IDs and model receipts,
state/claims/verification/budget/stop/truncation, source+normalized provenance, per-input identity,
per-frame reset acknowledgements, latency timing scopes and allocator/device measurements.
One load and same worker identity across all4 inputs, fresh per-image state, correct sequential
waits and no fourth camera capture are required. No OOM/timeout/process failure; afterimage
memory must return to post-load allocated baseline without persistent unexplained growth.
Report missing data as missing; do not tune acceptance after observing results.
Final allocator0/worker exit/jobempty/device recovery and physical camera release required.
Same-model support and author usability ratings are not accuracy/ground truth.
Stop on any failure, preserve evidence and backup, no retries. Postchecks + ALL raw outputs
for human review. No new application CUDA READY until technical criteria and author review.
