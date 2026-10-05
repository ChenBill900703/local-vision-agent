# Local Vision Agent

Frozen backup research prototype for local image understanding on an8GB consumer GPU.
Manual JPEG/PNG and repeated Webcam still frames share a bounded Agent, Traditional Chinese
report, local JSON history, qualitative author review and derived CSV export.

**FROZEN WITH KNOWN BLOCKER:** final Qt enumeration found0cameras. CPU software/export checks
passed; physical Webcam and persistent multi-image CUDA remain unvalidated.
[Start here](docs/NEXT_AI_START_HERE.md) · [Final outcome](docs/PROJECT_FINAL_VALIDATION_RESULT.md).

## Architecture / requirements

Native PySide6 GUI -> validated source/normalization -> persistent supervised InternVL3 ->
bounded caption/query/verification Agent -> report/history/export. Repeated stills, not video.
Windows/Python3.11, RTX3070Ti8GB target,32GBRAM. InternVL3-2B-Instruct pinned revision
f6c7b60375759170fd49f5e9e298e2178485c5ba, BF16 cuda:0 batch1; existing reviewed local assets
and locked environment. No automatic install/download. [Architecture](docs/PROJECT_ARCHITECTURE.md)
and [interfaces](docs/PROJECT_INTERFACE_CONTRACTS.md).

## CPU quick start

PowerShell from repository root:

    $env:PYTHONPATH = Join-Path (Get-Location) 'src'
    .venv/Scripts/python.exe -m local_vision_agent.windows_app

Default is explicit MOCK/FakeCamera, not recognition. 開啟圖片 -> 開始分析; report in 分析,
trace in 詳細資料, local records/review/export in 歷史紀錄. Real mode needs explicit author
unfreeze/hardware approval; see [runbook](docs/PROJECT_RUNBOOK.md). Webcam must be ready;
one analysis at a time, wait5s after completion, then next still. Stop/close normally.

## Testing / export

    .venv/Scripts/python.exe -m unittest discover -s tests -q
    .venv/Scripts/python.exe -m ruff check src tests scripts
    .venv/Scripts/python.exe -m mypy --strict src/local_vision_agent
    .venv/Scripts/python.exe -m pip check

CPU baseline180tests/39typed modules. JSON canonical; reviews separate; CSV analysis/calls/
sessions and engineering_summary.json are derived, UTF8/Excel-safe and preserve NA versus0.
[Export schemas](docs/THESIS_DATA_EXPORT_DESIGN.md).

## Safety / scope

8calls/128output tokens per call; bounded input/time/GPU limits, no offload/cloud fallback.
Same-model verification is not truth; hallucination and truncation remain limitations.
No general accuracy/novelty/formal benchmark claim. Private frames/assets/evidence ignored,
not for publication. No push approved; repository license unresolved.
Stop features until explicit unfreeze; next primary research work is advisor-directed paper
reproduction. [Limitations](docs/PROJECT_KNOWN_LIMITATIONS.md) ·
[Recovery](docs/PROJECT_RECOVERY_GUIDE.md) · [Context](docs/PROJECT_RESEARCH_CONTEXT.md).
