# Data views addendum — 2026-10-05

Implemented three native views: 分析 retains preview/controls/report; 詳細資料 shows inert full trace/calls/claims; 歷史紀錄 adds author rating/note and four CSV export actions. Result/review/session JSON canonical; exports derived with spreadsheet escaping. Review/export disabled while auto/analysis active. Read-only text, no model command execution. See THESIS_DATA_EXPORT_DESIGN.md and implementation result; no overall architecture redesign or new dependencies.

---

# Implementation addendum — 2026-10-01

User accepted design and explicitly approved the four-package installation. Implemented and CPU READY;150CPUtests/Ruff/strictMypy35/pipcheck PASS. See WINDOWS_UI_IMPLEMENTATION_RESULT.md. Layout uses stacked native preview, horizontal controls, result and history; MODEL_LOADING is represented by the busy loading/analysis label. Stop camera retains a healthy model session until app close/watchdog. Runtime lifetime warning is shown; no automatic reload after global1800s expiry. Physical camera/GPU behavior unverified. The original prospective design/installation proposal below is retained as history.

---

# Windows UI design v1 — 2026-10-01

DESIGN PREPARED / DEPENDENCY AUTHORIZATION REQUIRED. Not implemented or CPU READY.
[Scope decision](THESIS_SCOPE_SIMPLIFICATION_DECISION.md).

## One local application

PySide6/Qt Widgets main window only, no HTTP/REST/browser/server/C# bridge. Both manual
JPEG/PNG and captured stills create ImageInput and share prepare_source, existing InternVL
adapter, Agent, report rendering, measurements and failure handling. Manual files never
require user resizing. Do not wrap run_development in a per-frame loop: that entry currently
loads/unloads for each invocation. Its existing CLI behavior must remain unchanged.

Aspect-preserving preview, left source controls, readable Traditional Chinese result panel,
and local history table. Controls: 開啟圖片,開始分析; device selector,開啟 Webcam,
開始自動分析,停止自動分析,關閉 Webcam. Exact interval label:
**分析完成後等待：5 秒** (integer3–30, default5); never promises a result every5 seconds.
Saving checkbox **保存已分析的 Webcam 影像**, defaultOFF. Display finite session limits.

Result fields: Chinese report, source IMAGE/WEBCAM, status, input/frame ID, capture/input
and completion timestamps, calls, output tokens, truncated yes/no, verification coverage,
stop reason, total latency, peak allocated and peak reserved VRAM. Missing measurements
show N/A, never invented0. Same-model supported is not truth; retain uncertainty/errors.
History rows include timestamp/source/ID/status/calls/latency/coverage/report reference;
selection reads the saved report/metadata without inference. Report text rendered as plain
text or safe Markdown with external navigation/images disabled; model text never executable.

## Ownership and responsiveness

Qt main thread owns widgets, camera objects and timer. A QObject worker moved to one
QThread owns the analysis session/transport. Queued signals carry immutable request/result
records; worker never accesses widgets. GPU remains in existing supervised child process.
Only one active request; reject concurrent manual/automatic requests rather than queuing.
Disable Analyze while auto mode, loading, analyzing or stopping. GUI may show live preview
independently, but no new inference capture while analysis is active.

Controller states: IDLE,IMAGE_READY,MODEL_LOADING,ANALYZING_IMAGE,WEBCAM_PREVIEW,
WEBCAM_AUTO_ANALYZING,STOPPING,ERROR, plus an explicit busy flag and finite-session fields.
Open valid manual image -> IMAGE_READY; Analyze -> loading if needed then analyzing;
completion -> IMAGE_READY, persist outcome first. Camera open -> preview; auto start ->
sequential capture; stop disarms timer immediately, drains bounded current work, releases
camera/session and restores safe nonbusy state. A stale callback must match session/request
ID before affecting UI. ERROR preserves failure record, closes resources as required and
permits explicit safe return to IDLE, never hidden retry. A poisoned runtime cannot be reused.

Close event: mark closing, disable new work, cancel timer and release camera; defer actual
window destruction while bounded worker shutdown executes; queued status updates remain
safe. Current call finishes or existing watchdog expires, then model unload, Job/process
cleanup, thread completion and exit. Never terminate a QThread or CUDA call unsafely.
Existing call/image/cleanup/session timeout ceilings remain unchanged. Close cleanup timing
must separate remaining active operation time from the10s cleanup allowance.

## Local storage/privacy

Use ignored `artifacts/windows-app/` with exclusive UUID session/run directories and
atomic JSON per result (temporary file -> replace). History index may be reconstructed
from valid record files, so interrupted writes cannot invalidate older records. No SQL.
Confine history/report paths to storage root and validate schema on read; corrupted entry
shows readable error and does not erase other entries. Do not copy manual originals.
Temporary analyzed-camera PNG is private and bounded, cleaned after analysis when saveOFF;
normalization derivatives also removed after last consumer when saveOFF. Retain hashes,
dimensions, timestamps, IDs, prompts/raw reports/resource/error metadata. Never save preview
stream. On startup, purge only validated application-owned abandoned ephemeral frames,
not user files or retained research evidence. Failed deletion is reported, not claimed absent.
Session count is bounded; permanent result/history retention is user-managed, never silently
delete old evidence. No network upload or identity/biometric analysis.

## Missing dependency: concrete installation proposal

Environment audit: existing Python3.11.9; PySide6/PyQt6/OpenCV absent. No camera hardware
enumerated or opened. Proposed exact Windows64 binary set (all version6.8.3):

| Package | Purpose | Wheel bytes |
|---|---|---:|
| PySide6 | Official Qt Python entry package | 561080 |
| PySide6-Essentials | QtCore/Gui/Widgets and required bindings | 72191029 |
| PySide6-Addons | QtMultimedia camera/still capture modules | 127865208 |
| shiboken6 | Required binding runtime | 1150998 |

Official metadata declares Python>=3.9,<3.14 and Windows cp39-abi3 wheels. Total201768315bytes
(about192.4MiB) compressed; installed footprint not yet measured. Proposal: download at
most250MiB, allow at most1GiB incremental project-venv/cache storage, stop if exceeded.
Pin wheel SHA256 recorded in ignored `proposed_dependency_metadata.json`; use binary-only
hash-checked installation into existing project .venv, no build/compiler/system installation.
Do not upgrade torch/transformers/numpy/Pillow/CUDA or other existing packages. Snapshot
before/after distributions, verify pip dependency consistency and run full CPU suite/Ruff/
strict Mypy after implementation. Installation would add these four packages only; unexpected
resolver changes STOP. Selected stable version is a compatibility candidate, not claimed
latest, vulnerability-free or tested on this machine.

Use QtMultimedia QCamera + QMediaCaptureSession + QImageCapture for device selection,
preview and bounded still capture. **CAMERA DEPENDENCY REQUIRED** is satisfied by the
proposed PySide6-Addons package; OpenCV is absent but is not necessary for this selected
backend, so no OpenCV install requested. Physical-device/Windows permission compatibility
remains unverified. Backend failure stops; no silent alternative dependency installation.

Official sources checked2026-10-01:
[PySide6 6.8.3 metadata](https://pypi.org/pypi/PySide6/6.8.3/json),
[QCamera](https://doc.qt.io/qtforpython-6.8/PySide6/QtMultimedia/QCamera.html),
[QImageCapture](https://doc.qt.io/qtforpython-6.8/PySide6/QtMultimedia/QImageCapture.html).
PySide6 offers LGPLv3/GPL/commercial licensing; preserve notices and applicable redistribution
obligations. No packaging/public distribution authorized or claimed license-compliant here.

User section2 explicitly says missing PySide6 -> do not install -> STOP for authorization.
Thus this proposal is reviewable but NOT an executed installation or GUI acceptance result.
