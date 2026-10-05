# Project architecture

Local Windows still-image understanding prototype. One local VLM; deterministic bounded
Agent, no controller LLM/cloud runtime. Runtime model is InternVL3-2B-Instruct pinned
f6c7b60375759170fd49f5e9e298e2178485c5ba, BF16 cuda:0, batch1, single448tile.

Manual JPEG/PNG / Qt Webcam still -> ImageInput -> source validation/normalization ->
PersistentAnalysisSession -> existing adapter/supervised RPC -> InternVL3 -> bounded Agent
caption/query/verification -> Report -> atomic JSON/CSV -> native Windows UI.
Agent drives adapter calls; this sequence describes ownership, not a second inference pipeline.
Webcam is sequential repeated stills, not temporal reasoning. FakeCamera/mock is explicit.

| Source module under src/local_vision_agent | Ownership |
|---|---|
| windows_app.py | main(), MainWindow, Qt controls, timer, view/history, safe close |
| app_camera.py | CameraBase, QtCamera, FakeCamera; preview and still capture |
| app_controller.py | AppController, SessionLimits, one active request, no queue |
| app_worker.py | AnalysisWorker QThread slots; AppRequest; FakeAnalysisSession |
| app_session.py | AnalysisSession protocol, PersistentAnalysisSession lifecycle |
| source_input.py / image_input.py | original bytes validation, provenance, bounded normalization |
| internvl_adapter.py / internvl_transport.py | normalized calls, persistent JSON RPC and watchdog |
| internvl_rpc_worker.py / internvl_backend.py | private child dispatcher and reviewed CUDA backend |
| gpu_guard.py / windows_job.py | resource refusal and process-tree containment |
| contracts.py / agent.py | typed inputs/requests/answers/reports, bounded A-D controller |
| reporting.py | inert structured Traditional Chinese report |
| app_storage.py / app_webcam_record.py | atomic result/review/session/cleanup records |
| app_receipts.py / app_export.py / app_export_schema.py | actual receipts, derived CSV/summary |
| real_agent.py | legacy one-image development CLI, separate default lifecycle preserved |

UI main thread owns widgets/Qt camera/timer. Analysis QObject runs in one QThread and sends
queued signals. Only supervised child imports/executes heavyweight model after preflight.
Model/tokenizer/PID/global watchdog persist; each source has fresh Agent memory, namespace,
report, tensor/reset acknowledgement and per-image budget/deadline. Worker1800s never resets.
Capture -> analysis -> save/display -> wait5s -> next capture. Interval3–30; default20frames,
validation3. Source32MiB/32MP/10000edge; automatic aspect512 -> unchanged448 model path.
Model limit8calls/iterations and128output tokens/call; no offload, device_map=auto or reload.

See PROJECT_INTERFACE_CONTRACTS.md for APIs, PROJECT_RUNBOOK.md for commands and
THESIS_DATA_EXPORT_DESIGN.md for schemas/denominators. Legacy classification is historical,
not active architecture. Assets/evidence/private images live in ignored local directories.
