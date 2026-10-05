# NEXT AI — START HERE

LOCAL VISION AGENT v1 = FROZEN / PROJECT FROZEN WITH KNOWN BLOCKER.
BACKUP RESEARCH PROTOTYPE = PRESERVED.
PRIMARY NEXT RESEARCH ACTIVITY = advisor-directed PAPER REPRODUCTION.

Repository evidence overrides chat memory. Stop feature development. Author must explicitly
unfreeze, name bounded changes/tests and separately authorize hardware/acquisition/publishing.
Do not model-shop, broaden scope, retry consumed hardware work or rebuild from zero.

Windows local image-understanding prototype: manual JPEG/PNG or repeated Webcam stills ->
validated aspect512/single448 input -> persistent local InternVL3 -> bounded MethodD Agent ->
Traditional Chinese report, canonical JSON, qualitative author review and derived CSV.
Target RTX3070Ti8GB/i7-11700K/32GB/Windows/Python3.11.9. InternVL3-2B-Instruct revision
f6c7b60375759170fd49f5e9e298e2178485c5ba, BF16 cuda:0 batch1; no offload/cloud runtime.

## Revision and state

Branch main. Exact frozen commit ref: local-vision-agent-v1.0-frozen^{commit}.
Resolve the annotated tag with commands below; expected final tree clean. Pre-freeze parent
cf4ec1455b8a12026d0ebd849e3a6cb1b9514cce is historical, NOT the final release commit.
A file cannot contain its own containing commit hash without changing it. This package uses the
exact immutable tag ref; local post-commit final_git_receipt.json records the resolved literal
HEAD/tag/tree at artifacts/final-closeout-20261005/. Root PROJECT_FREEZE_MANIFEST_2026-10-05.json
contains source/package/model/config/document hashes and commit reference.

## Verified versus missing

Final precheck180CPUtests/Ruff/strictMypy39/pipcheck PASS; postchecks recorded in final report.
Earlier real single-image engineering baseline READY. Current UI/manual/Webcam/export CPU READY.
Final physical enumeration found0devices. No physical camera opened, no new model load/GPU
inference. Physical Webcam and persistent multi-image CUDA NOT VALIDATED; no4real closeout answers.
Mock/stub/synthetic examples do not establish physical compatibility or semantic accuracy.

## First commands — PowerShell from project root

    git status --short
    git branch --show-current
    git rev-parse HEAD
    git rev-parse 'local-vision-agent-v1.0-frozen^{commit}'
    $env:PYTHONPATH = Join-Path (Get-Location) 'src'
    .venv/Scripts/python.exe -m pip check
    .venv/Scripts/python.exe -m unittest discover -s tests -q
    .venv/Scripts/python.exe -m ruff check src tests scripts
    .venv/Scripts/python.exe -m mypy --strict src/local_vision_agent

Do not initialize CUDA or open camera just to resume. Ignored evidence/models/private images
are intentionally outside Git and are not disposable. Verify inventories before recovery.

## Reading order

- PROJECT_FINAL_VALIDATION_RESULT.md, root freeze manifest, CURRENT in ../SESSION_HANDOFF.md.
- PROJECT_ARCHITECTURE.md and PROJECT_INTERFACE_CONTRACTS.md.
- PROJECT_RUNBOOK.md, PROJECT_RECOVERY_GUIDE.md and PROJECT_KNOWN_LIMITATIONS.md.
- PROJECT_RESEARCH_CONTEXT.md; THESIS_DATA_EXPORT_DESIGN.md and its implementation result.
- WINDOWS_WEBCAM_PHYSICAL_VALIDATION_CHECKLIST.md and2026-10-05 scope addendum.
- Historical ENGINEERING_BASELINE_DECISION.md, SMARTPHONE_COMBINED_GPU_VALIDATION_RESULT.md,
  REAL_INTERNVL_INTEGRATION.md and RESEARCH_DIRECTION.md; preserve negative evidence.

Restart hardware only after explicit author unfreeze/new bounded approval and connected
rights-safe device/scene/input. TEST A first; no retry on failure. New run ID required.
Paper reproduction is a separate author/advisor task, not implied permission to change this app.
LOCAL FREEZE COMPLETE / GITHUB PUSH PENDING AUTHOR AUTHORIZATION; no remote configured.
