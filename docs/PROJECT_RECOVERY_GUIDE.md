# Recovery guide

Read NEXT_AI_START_HERE.md first. Repository evidence overrides chat memory. Verify frozen tag,
source/config/dependency hashes and actual raw records before proposing a fix. Never rebuild
from zero as a first action. Do not reset/delete user changes or ignored evidence. Project
remains frozen until explicit author unfreeze with bounded repair/test authorization.

| Symptom | First checks and stop boundary |
|---|---|
| GUI fails | correct project cwd/.venv/PYTHONPATH, PySide66.8.3 four packages, pip check, application lock ownership; save traceback; CPU mock only; never delete lock of running app |
| Camera unavailable | actual device connected, author-set Windows permission, GUI deviceID/readiness/error; preserve error; stop physical route; no OpenCV/framework swap |
| Model load fails | pinned asset/controlled patch/dependency/config hashes and GpuGuard refusal; no download/reload/model swap without renewed scope |
| CUDA OOM/guard violation | stop scheduling, retain failed raw/evidence, bounded cleanup/process recovery; no offload/shared-memory/precision/limit workaround |
| Worker dies | parent_trace/events/stderr, watchdog and recovery.json, Windows Job/exit/device evidence; do not call exited process a clean allocator unload |
| CSV corrupt | preserve old export, inspect canonical JSON and export_audit; re-export via CPU API while idle; never repair raw answer to fit a CSV |
| Tests fail | stop hardware use, compare frozen source/deps, isolate CPU failure and request bounded repair/unfreeze; don't skip tests |
| Dependencies drift | compare freeze manifest and lock/RECORD hashes; no force upgrade/downgrade/install; propose exact authorized restoration |

Safe recovery priorities: stop new work -> close normally/drain bounded operation -> save all
failure/cleanup evidence -> compare baseline -> minimal repair only if newly authorized -> CPU
checks -> new prospective hardware run authorization (never reuse consumed no-retry allowance).
If process appears orphaned, identify exact recorded owned PID/Job before any termination;
never indiscriminately kill Python/CUDA processes. Verify device recovery only if authorized.

Restore Git snapshots into a separate reviewed location after authorization; ignored evidence
and model assets are not in Git. Local evidence backups have inventory hashes. Verify backup
before relying on it. Do not publish/upload while recovering. Existing private photos remain
private. No feature expansion or research redesign follows from a technical failure.
