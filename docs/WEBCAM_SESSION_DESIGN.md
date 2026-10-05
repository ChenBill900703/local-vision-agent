# Session data and audit addendum — 2026-10-05

Canonical session.json now retains backend identity, UTC lifecycle, captured/submitted frame IDs and counts, limits, stop and cleanup evidence. Fake metrics are NA, no invented physical release. Existing persistent isolation and sequential scheduling preserved; next wait begins after result display/history update. Device-ID drift refuses before open, Qt readiness gates Start; physical backend verified with stubs only. CPU180tests pass. See THESIS_DATA_EXPORT_IMPLEMENTATION_RESULT.md audit matrix and new hardware checklist. Physical camera and persistent CUDA remain NOT EXECUTED.

---

# Implementation addendum — 2026-10-01

Required persistent reset and CPU/Fake acceptance are implemented:150totalCPUtests/Ruff/strictMypy35/pipcheck PASS. One supervised CPU fixture process handles three image boundaries; real model path remains untested. Bounded verification completion has status complete and may continue; partial execution errors stop. Worker lifetime stays1800s globally, with UI warning and watchdog refusal/cleanup rather than hidden reload. Stop capture keeps healthy service until appclose. Prospective three-frame amendment now frozen separately, NOT EXECUTED. Original pre-implementation design below remains historical; see WINDOWS_UI_IMPLEMENTATION_RESULT.md for actual implemented behavior.

---

# Webcam still-frame session design v1 — 2026-10-01

DESIGN PREPARED / DEPENDENCY GATE. No physical camera/GPU use or CPU READY claim.

## Sequential scheduling

SEQUENTIAL CAPTURE-AFTER-ANALYSIS: capture exactly one still only when idle -> source
validation/normalization -> same Agent -> persist/display result -> waitNseconds -> next
capture. next_due=analysis-result-completed_monotonic+N, not previous capture+N.
DefaultN=5, integer range3–30, reject bool/nonfinite/invalid values.12s analysis+5s wait
means about17s between captures, additionally including capture/storage overhead.
No queue, latest-frame buffer or concurrent GPU request. Live preview is not inference.
At each capture and callback verify active session/generation token, not stopping/busy,
frame count and monotonic deadline; discard stale callbacks safely.

Defaults:20 analysed-frame attempts and30min maximum wall-clock session duration. Count
an accepted inference frame attempt even if it later fails, preventing unlimited failures.
Start deadline when auto mode starts; include loading, waits and capture. At deadline stop
scheduling and drain existing bounded operation; deadline is not permission to interrupt
CUDA unsafely or reset a timeout. Check elapsed time after capture before submitting.
Stop at frame ceiling, deadline, user stop, camera failure or runtime failure. No auto retry.
Partial normal bounded verification is saved accurately and may continue only if session
remains healthy and allowed; runtime/cleanup/safety error stops auto mode immediately.

UUID4 session IDs with UTC timestamp for readability; monotonic per-session frame counter
and UUID-based run directory prevent collisions. Every request/result records session_id,
frame_id,captureUTC,sourceSHA256,dimensions,source type and report reference. Reset counter
only for a new collision-safe session. Frame-save OFF default; ON saves only submitted
analysed frames. Preview buffers never written. Disconnect/read-failure before submission
is a session error, not invented successful frame; history keeps failure with missing N/A.

## Required persistent runtime extension (not yet implemented)

Current InternVLAdapter.begin_image rejects a second image (`ONE_IMAGE_PER_WORKER`),
real_agent.run_development creates a fresh adapter for each invocation, and the worker
RPC has begin_image/invoke/unload only. Reusing it as-is cannot meet the requirement.
Introduce an explicit persistent-session path using the SAME backend/adapter and bounded
Agent, preserving legacy one-image CLI default. No second inference pipeline.

First valid source request validates/normalizes before first GPU load; load once on demand.
For every image create fresh Agent/report state; fresh observations, candidate claims,
verification flags/counters, evidence links, total tokens, image timeout and image metrics.
Explicit end_image/reset_image RPC acknowledged before next begin_image; release image
pixel/visual/KV tensors and all per-image references, retain only model/tokenizer and
session-global resource/watchdog/offline state. Per-image trace IDs namespaced by frame
and session even when Agent call IDs restart at call-1. Evidence is append-only with frame
boundaries, never overwrite previous report or confuse prior frame resource snapshots.
Session limits and model lifecycle counters are never reset at frame boundaries.

Existing session watchdog1800s remains global from worker start. If manual work consumed
part of that lifetime, automatic mode must display/use remaining runtime time; do not
extend watchdog or silently reload the model. At expiry stop/unload and require explicit
new session. Model can persist across manual and camera images within this bound. Physical
GPU validation must establish per-frame reset and memory behavior; CPU Fake proof alone
cannot demonstrate allocator cleanup or persistent CUDA correctness.

Application/session shutdown: stop schedule -> release camera -> drain bounded active work
-> unload model -> verify allocator/process/Job/device recovery -> exit. Stop auto mode
ends capture session; healthy model service may remain for manual work until shutdown or
existing session deadline, with all image state cleared. Camera-close/error stops new work;
existing in-flight analysis ends safely. No forcibly killed Qt thread, second model or retry.

## CPU/Fake acceptance matrix (all pending)

Implement FakeCamera and injected fake analysis service/clock, explicitly labeled simulation.
Tests1–23 from user request map to: manual request+invalid ingress; camera open/close;
finish-then-wait scheduling/interval boundaries; busy rejection/no queue; collision-safe
session/frame IDs; actual Agent fresh-state and RPC image-boundary resets with distinct
fake claims/evidence; maxframes/deadline; Stop while waiting/loading/analyzing; disconnect/
read failure; application close/cleanup errors; history roundtrip/corruption; saveOFF removes
temporary source and normalized derivatives; saveON retains only analysed fake frame;
error recovery/no retry; legacy CLI/runtime behavior unchanged.
Qt tests additionally cover queued signal delivery/thread ownership, lifecycle/disposal,
stale result rejection and close during analysis. No fragile pixel assertions. Full CPU
suite, Ruff and strict Mypy required. No physical camera, CUDA initialization or inference
in this phase; no mock fallback in a real request.

## Future amendment gate

Only after WINDOWS UI and WEBCAM INPUT are CPU READY create
`WINDOWS_WEBCAM_GPU_VALIDATION_AMENDMENT_2026-10-01.md`; it is deliberately NOT frozen now.
Then propose ONE separately authorized local physical camera/non-sensitive scene session,
max3 analysed frames, wait5s after completed analysis, one model load, same pinned BF16/
cuda0/P1/8calls/128tokens/guards/offline/timeouts, no retries. Require source/capture
provenance, each frame's reset/unique trace/report/history, bounded resource evidence,
no OOM/timeout/leak, camera release and final model/process/device cleanup. Freeze exact
source/config/dependency hashes after implementation, never invent future commit hashes.
No physical run is authorized by the design or eventual amendment alone.
