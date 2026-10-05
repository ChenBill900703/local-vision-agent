# Project runbook

Read NEXT_AI_START_HERE.md. Commands describe existing interfaces, not new execution approval.
Future hardware/code changes require explicit unfreeze. PowerShell, project root.

## Environment and CPU checks

    Set-Location -LiteralPath 'E:\AI Agent影像辨識專案'
    . .\.venv\Scripts\Activate.ps1
    $env:PYTHONPATH = Join-Path (Get-Location) 'src'
    $env:PYTHONIOENCODING = 'utf-8'
    .venv/Scripts/python.exe --version
    .venv/Scripts/python.exe -m pip check
    .venv/Scripts/python.exe -m unittest discover -s tests -q
    .venv/Scripts/python.exe -m ruff check src tests scripts
    .venv/Scripts/python.exe -m mypy --strict src/local_vision_agent

Explicit .venv executable needs no activation; if policy blocks activation, do not weaken
Windows policy. Expected180tests/39typed modules. Do not pip-install broad optional ranges;
exact installed versions/lock hashes are in freeze manifest. No automatic dependency repair.

## CPU MOCK GUI

    .venv/Scripts/python.exe -m local_vision_agent.windows_app

Default explicit MOCK/FakeCamera: no physical camera or model. 開啟圖片 -> 開始分析;
分析 shows report; 詳細資料 trace/calls; 歷史紀錄 history/review/exports. Synthetic output
is not recognition. Author review is qualitative, not truth. Storage artifacts/windows-app/.

## REAL GUI — renewed scoped authorization required

    .venv/Scripts/python.exe -m local_vision_agent.windows_app --authorize-development-gpu --storage artifacts/windows-app-author-approved-new-run --max-frames 3 --max-session-seconds 1800 --interval-seconds 5

Use NEW ignored directory. Camera selector/Open -> preview/readiness -> Close -> Reopen.
No devices/errors means STOP. Only after approved TEST A succeeds, ONE approved original
manual JPEG/PNG -> 開始分析 once (automatic normalization). Keep SAME model/worker for
camera auto: one session,max3frames,5s post-analysis wait,saveOFF. No fourth/extra manual
frame/reload/concurrency. Existing limits/guard/offline/watchdog remain. Current no-device
blocker means real route NOT validated. Follow frozen physical checklist/addendum with new scope.

## Export and CPU-only history

While idle select export button in 歷史紀錄; four buttons export summary/calls/session/all.
Output folder is shown; JSON canonical. To re-export cleanup records, close original app, open
same existing storage in DEFAULT CPU mode and do not trigger any analysis:

    .venv/Scripts/python.exe -m local_vision_agent.windows_app --storage artifacts/windows-app-author-approved-new-run

Or use existing API from CPU Python while no app writes that directory:

    from pathlib import Path
    from local_vision_agent.app_storage import AppStorage
    from local_vision_agent.app_export import export_bundle
    path = Path('artifacts/windows-app-author-approved-new-run')
    assert path.is_dir()
    print(export_bundle(AppStorage(path), 'all'))

Enter via .venv/Scripts/python.exe after setting PYTHONPATH. No app_export CLI exists.
Missing metrics remain NA; retain both before/after-cleanup exports. See export schema docs.

## Safe shutdown / legacy entry

Stop auto, close Webcam, close app normally; wait for bounded current work and cleanup/QThread.
Never kill unrelated Python or force-terminate Qt thread. Inspect cleanup sidecars: allocator0,
worker exited, Job empty, baseline recovery; fake cleanup is not hardware proof.
real_agent.py legacy CLI remains one-image lifecycle, not a Webcam loop. Actual parameters:
--config --assets --image --input-id --evidence-dir --method A/B/C/D --authorize-development-gpu.
No legacy real run is authorized by this document. For failures use PROJECT_RECOVERY_GUIDE.md.
