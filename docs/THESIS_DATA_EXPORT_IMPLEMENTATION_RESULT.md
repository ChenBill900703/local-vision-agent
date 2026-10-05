# Thesis data export implementation result — 2026-10-05

REAL LOCAL AGENT ENGINEERING BASELINE = READY (historical tested path).
WINDOWS UI = CPU READY. MANUAL IMAGE ANALYSIS = CPU READY. WEBCAM AUTO ANALYSIS = CPU READY.
THESIS DATA EXPORT = CPU READY.
PHYSICAL WEBCAM VALIDATION = WAITING FOR AUTHOR HARDWARE / NOT EXECUTED.
REAL PERSISTENT MULTI-FRAME CUDA = NOT YET VALIDATED.

## Resume audit and scope

Author request c18948da-6576-4ded-9e8d-cd2afd7dbaba explicitly approved this application/data-layer
completion; retained in artifacts/thesis-export-20261001/evidence/user_authorization.txt.
Work began10/01 and resumed/completed10/05 after an automatic approval-service usage-limit
interruption. The rejected command did not execute; subsequent checks below are actual results.
No new dependency, GPU query/CUDA initialization, inference, physical camera, formal evaluation,
commit or push. HEAD cf4ec1455b8a12026d0ebd849e3a6cb1b9514cce remains; working tree dirty.

Audit against previous CPU manifest: Agent, prompts/contracts, FIFO, source normalization and
limits, model/policy, GPU guard, real CLI, adapter/backend/RPC/transport and report renderer
unchanged. Existing installed distributions unchanged. Prior combined raw14file hashes unchanged.
Existing dirty work from earlier phases retained. No existing evidence/negative result rewritten.

## Implementation

New app_export_schema.py defines43 summary,16 call and32 session columns in fixed order.
app_export.py creates UTF-8-BOM CSV derivatives, engineering_summary.json and export_audit.json.
No canonical output mutation; formula injection protection applies to derivative text only.
Partial/failure/NA/real0 preserved; actual received calls only, no fabricated skipped calls.
app_receipts.py joins existing worker start/done evidence for failed attempts by input+call ID.
app_webcam_record.py records camera/backend/session/attempt identities, limits, UTC lifecycle,
capture/submission counts, stop and cleanup evidence. Real hardware success is not inferred.

app_storage.py adds atomic review sidecar with four allowed author ratings, free text and UTC;
canonical result bytes/status untouched. app_session.py retains existing receipts/provenance
on failure; no changes to persistent model policy or per-image fresh Agent logic. app_worker.py
retains mock source provenance, analysis timing and cleanup sidecars. app_camera.py checks stable
device IDs against enumeration and avoids stale camera errors; readiness gates Start control.
windows_app.py preserves native architecture and adds 分析 / 詳細資料 / 歷史紀錄 tabs, read-only
trace/calls/claims, author review controls and four export buttons. Queued analysis/session model
and capture->analyze/save/display->wait5s sequence retained; no inference queue/concurrency.

Application snapshots/exports stay private in ignored artifacts storage. History item selection
performs no inference. No model-controlled shell command or automatic open-folder feature.
[Exact schemas and mapping](THESIS_DATA_EXPORT_DESIGN.md).

## Tests, sample and screenshots

**180 CPU tests PASS** (previous150 +30 new), **Ruff PASS**, **strict Mypy PASS39 modules**,
**pip check PASS**. Logs/commands: artifacts/thesis-export-20261005/validation/.
Tests cover summary/call/session exports, column/row order, deterministic bytes, Chinese,
quotes/commas/CRLF/empty/formula prefixes, NA versus zero, atomic author review and timestamps,
canonical bytes unchanged, fake multi-frame aggregation, partial/failed/truncated/coverage,
missing results, empty/corrupt history/review/session, safe paths, cleanup evidence, failed call
receipts, UI tabs/buttons and Qt physical-backend lifecycle/device-drift via stubs.
Existing persistent worker/Agent isolation, interval/limits, source validation, saveOFF/ON,
Stop, shutdown and original CLI tests remain passing. No physical compatibility inferred.

CPU-only demo: artifacts/thesis-export-20261005/demo/; one synthetic manual image and3 actual
FakeCamera requests, one fake analysis session. Injected scheduling clock advances5s after each
completion, so this is not measured real camera throughput. Four complete mock records,12mock
calls,120scripted output tokens; all4 NOT_REVIEWED, no author review invented. Real GPU measurement
count0, hardware metrics/cleanup unavailable. Wall-clock CPU latencies are not GPU/model timings.
Exports: demo/history/export-aa364f5dd89c44abab4fba36ed7d0d4c/.
Screenshots analysis.png, details.png, history.png rendered offscreen and visually inspected:
Chinese readable, three views/controls present, fields scrollable, history long IDs elided but
full values available via opened details/canonical JSON. This is software GUI sanity only.

## Webcam software audit

| Area | Evidence / disposition |
|---|---|
| QtMultimedia / Fake separation | Real backend uses QCamera/QMediaCaptureSession/QImageCapture; only Fake preview chooses synthetic QLabel. Common request/session path independent of Fake pixels. |
| Enumeration / selection | Cached physical device ID checked before open; device list drift refuses before start. Stub tested; actual Windows permission unknown. |
| Open / close / reopen | Stub verifies start, stop, detach, disposal; stale previous QCamera errors ignored. Real driver release not proven. |
| Preview / still capture | Qt video output separate from memory-only still capture; no preview recording. Readiness gates Start; capture ID matches pending request, stale frames ignored. |
| Identities / timestamps | UUID session/input IDs, per-session frame counter, UTC capture/complete/start/end, monotonic scheduler. |
| Temp images / save flag | DefaultOFF removes owned PNG/normalized derivative after consumers; ON retains submitted frames; originals never deleted; existing tests pass. |
| Sequential scheduling | One active request; next_due reset after display/history update; interval3–30/default5; no queued inference; maxframes/time stops. |
| Stop / app close | Timer disarmed; camera closed; bounded active analysis drains; persistent worker closes once; session stop/cleanup recorded. |
| Disconnect / errors | Camera error stops, logs; storage failure refuses capture; model errors remain failed records; no automatic retry. |
| Persistent isolation | Prior tests still prove one CPU fixture PID/load with3 fresh Agent states and image reset; CUDA version still unvalidated. |

Residual hardware risks: actual Qt camera readiness/driver signal ordering, Windows permission,
preview/capture compatibility, real persistent CUDA memory reset, real resource/cleanup recovery.
No evidence from fake/stub tests resolves these. Hardware checklist includes STOP on failure.
Original three-frame amendment is preserved, unexecuted and stale after authorized software
changes; a dated prospective addendum binds new source and explicitly includes the newly requested
manual real-image GUI test. It is NOT execution permission.

Next action: when hardware is available, author confirms rights/non-sensitive scene and explicitly
authorizes [hardware checklist](WINDOWS_WEBCAM_PHYSICAL_VALIDATION_CHECKLIST.md) with
[scope addendum](WINDOWS_WEBCAM_VALIDATION_SCOPE_ADDENDUM_2026-10-05.md). No additional work starts
by inference. Keep10/31 code and11/1 acceptance as goals, not guarantees or scientific claims.
AI assistance: implementation, CPU tests, data mapping/docs and synthetic screenshot review;
not image-semantic judging or replacement for author review. Only descriptive summary provided.
