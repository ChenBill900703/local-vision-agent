# Windows Webcam physical validation checklist — 2026-10-05

**PROSPECTIVE / NOT EXECUTED / WAITING FOR AUTHOR HARDWARE AND EXPLICIT GPU AUTHORIZATION**.
For the author's hardware-ready Friday; no calendar appointment or availability assumed.
Use [2026-10-05 scope addendum](WINDOWS_WEBCAM_VALIDATION_SCOPE_ADDENDUM_2026-10-05.md).
Old2026-10-01 amendment alone does NOT authorize the new manual image plus3 Webcam frames.

## PRECHECK — complete before real model load

- [ ] Obtain explicit scoped author execution approval, rights-confirmed local manual image and
  ONE non-sensitive camera scene; no private screens/documents/credentials/unconsented people.
- [ ] Connect ONE physical Webcam; Windows camera/privacy permissions enabled. No identity task.
- [ ] Correct project .venv; verify exact current CPU manifest source/config/dependency hashes,
  installed versions/model assets+controlled code; no drift. Record HEAD+dirty diff+hashes.
- [ ] Run full CPU suite/Ruff/strict Mypy/pip check. Expected current180tests/39modules; any fail STOP.
- [ ] Create a NEW ignored evidence/storage directory and record exclusive consumed-run gate.
  Never reuse an old run directory. No installation/download/cleanup deletion as a workaround.
- [ ] With authorization only, record GPU/driver/baseline/resources. Existing GpuGuard/preflight,
  reserve/allocator/placement/offline/timeouts must pass. A safety refusal stops BEFORE load.
- [ ] Open real GUI (separate explicit GPU mode; default mode is MOCK). Select the expected
  physical camera name/ID, not FakeCamera. Max auto frames3, interval5, save frame OFF.
  Real mode starts no model until valid input analysis. Do not press analysis during preview test.

## TEST 1 — physical preview only

- [ ] Select camera -> 開啟 Webcam -> check live preview and readiness.
- [ ] 關閉 Webcam -> verify stopped -> reopen and verify preview/readiness again.
- [ ] Record local physical observation separately; calling stop() is not alone proof of release.
  If device permission/compatibility/error fails, STOP; no backend replacement or automatic retry.

## TEST 2 — one manual real GPU image through GUI

- [ ] Select the ONE approved original local JPEG/PNG; record SHA256/dimensions, no hand resizing.
- [ ] 開始分析 exactly once; original validation/normalization -> existing InternVL MethodD.
- [ ] Retain exact raw report/trace/prompts/token IDs, source/normalized provenance, calls/tokens,
  truncation/verification/unresolved budget/latency/VRAM. Confirm result and history exist.
- [ ] Export CSV while idle and verify fields/raw response/JSON hash joins. No edits to answers.
- [ ] Keep this SAME healthy persistent model/worker loaded for Test3. No second load/retry.
  Failed/partial execution error stops entire session. Normal budget-limited completion is retained.

## TEST 3 — ONE physical Webcam Agent session

- [ ] Open the selected camera if needed, start auto once; max3 frames,5s after each completed
  analysis/save/display. No inference FIFO, no manual request during auto, no fourth capture.
- [ ] Confirm3 unique frame IDs; record each independent report, calls/tokens, source hashes,
  latency, VRAM, claims/verdicts/coverage/truncation/stop reasons and history references.
- [ ] Verify one model load/worker PID shared with manual test,3 fresh per-frame Agent states,
  no cross-frame claims/evidence/conversation, acknowledged image reset and global watchdog intact.
- [ ] Verify no OOM/timeout/offline/guard/placement violations; saveOFF frames/derivatives removed.
- [ ] At3frames stop; export all CSVs while idle. Check3 Webcam rows+1 manual row, call rows match
  actual receipts, one physical session row, no invented zero/cleanup success or skipped calls.
- [ ] Close app; verify camera release, model unload allocator0, worker exit/empty Job/process tree,
  device baseline recovery. Keep actual physical observation separately from software requests.
- [ ] Re-export from saved JSON after cleanup via a CPU-only app open (no additional analysis),
  to include cleanup sidecars. Preserve both pending-cleanup and final export bundles; never rewrite
  raw earlier exports to imply cleanup had already succeeded.

## CLOSEOUT

- [ ] On any safety/resource/process failure STOP, preserve partial/failed records, no retry.
- [ ] Preserve raw run inventory SHA256 and separate local backup; do not upload/private-frame judge.
- [ ] Run post-run CPU/Ruff/Mypy/pip check; write dated result and present ALL raw visual answers
  and verification results for author DEVELOPMENT HUMAN SANITY REVIEW, not GPT judging.
- [ ] Technical status only TECHNICAL PASS / HUMAN REVIEW PENDING or FAIL; do not automatically
  claim persistent multi-frame CUDA or application engineering acceptance from UI appearance.
- [ ] Stop. No formal evaluation, extra image/session/prompt tuning or push.
