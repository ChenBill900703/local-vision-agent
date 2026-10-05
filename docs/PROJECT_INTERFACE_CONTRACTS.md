# Frozen public interface contracts

Actual implementation names below are authoritative; no replacement API is proposed.
All source paths are relative to src/local_vision_agent/. Python3.11, explicit types.

## Camera — app_camera.py

CameraBase(QObject): devices() -> list[str] display labels; identity() -> dict[str, Any]
with camera_backend_type,camera_id,camera_display_name; ready() -> bool;
open(index:int) -> None; capture(identifier:str) -> None; close() -> None.
Signals frame(str,object) carries request ID and QImage; error(str) reports failure.
QtCamera(preview:QVideoWidget) uses QMediaDevices/QCamera/QMediaCaptureSession/QImageCapture;
backend QT_MULTIMEDIA_PHYSICAL, byte device ID encoded hex. Enumeration caches IDs; changed
index-to-ID mapping raises CAMERA_DEVICE_LIST_CHANGED before opening. Invalid index raises
CAMERA_UNAVAILABLE. ready requires active camera and ready-for-capture. One pending capture;
not-ready/busy raises CAMERA_NOT_READY, negative capture result CAMERA_CAPTURE_FAILED.
Only matching capture ID emits copied image; close clears pending, stops/detaches/disposes
camera. stop() is a software request, not independent proof of physical driver release.
FakeCamera() implements same contract; backend FAKE/id fake-camera-0; synthetic64x48 pixels,
no physical measurements. Delayed callbacks are generation-guarded; failure is injectable.
Only GUI thread manipulates these QObjects; preview stream is never recorded.

## Image / source — contracts.py, source_input.py

ImageInput(input_id:str,path:Path), immutable. ImageInfo(sha256:str,width:int,height:int,
format:str), immutable. prepare_source(item:ImageInput,source:SourceImageLimits,
model_limits:Limits,directory:Path) -> tuple[ImageInput,dict[str,Any]].
Validate original before model load: compressed32MiB, decoded32MP, edge10000, JPEG/PNG, strict
single image decode. Return original bounded path or aspect-preserving <=512 normalized PNG;
provenance retains original bytes/hash/dimensions/orientation and model input identity.
Original is never modified. Errors AgentError code, fail closed; limits required, no defaults.

## Persistent analysis — app_session.py

AnalysisSession(Protocol): analyze(item:ImageInput,input_directory:Path) -> Report;
close() -> dict[str,Any]. PersistentAnalysisSession(assets:Path,directory:Path,
config:RuntimeConfig) is lightweight at construction; first valid analyze lazily loads once.
Same InternVLAdapter(...,persistent_images=True) and supervised child for subsequent inputs.
Busy/closed/duplicate ID -> SESSION_CLOSED_BUSY_OR_DUPLICATE_INPUT. Invalid source before
runtime is recoverable; active runtime failure closes/poisons session, no retry/reload.
Agent(config.limits,adapter,executor=adapter).run(bounded,Method.D) produces fresh per-image state.
end_image RPC must acknowledge image_cleared before another image; trace cleared only after ack.
Report runtime_metadata contains source_input,frame_trace,image_end,model_runtime, timings,
evidence links and pending session cleanup. last_attempt retains source/receipts on failure.

Persist: model/tokenizer, worker PID, session identity, global1800s watchdog and resource/offline
policy. Reset: pixels/image references, image deadline, calls/output-token counters, peak image
stats, Agent observations/candidates/verification/report/state trace and per-input evidence
namespace. No conversational memory. Same call-N IDs may recur but are joined with input ID.
close unloads once and caches cleanup result; repeated close preserves prior failure rather
than inventing success. No safe recovery by silently moving tensors to CPU/disk.

## Agent/report — agent.py, contracts.py, reporting.py

Agent(limits:Limits,adapter:VisionAdapter,*,executor:Executor|None=None,
clock:Callable[[],float]=time.monotonic); run(item:ImageInput,
method:Method) -> Report; run_batch(items:list[ImageInput],method:Method)->tuple[Report,...].
Methods A-D remain implemented. Application selects D. Request(tool,prompt_id,prompt,
max_output_tokens,claim=None); Answer(text,claims,uncertain,missing,verdict,output_tokens,
generation_stop_reason,truncated). Same-model verdict is not ground truth.
Report is immutable dataclass, schema agent-report-v2; input/run/model IDs, states,
observations(request/answer/error), claims, limits, completion/stop, verification budget,
coverage, runtime metadata. status complete/partial/failed. Normal incomplete verification:
status complete, completion COMPLETED_WITH_PARTIAL_VERIFICATION, stop VERIFICATION_BUDGET_EXHAUSTED.
Execution error is distinct. Missing measurements None, not zero. to_json(Report)->str and
to_markdown(Report)->str preserve raw text; display-only, never execute model output.

## Scheduling / worker — app_controller.py, app_worker.py

SessionLimits(interval_s:int=5,max_frames:int=20,max_duration_s:int=1800), strict integer bounds
3–30/1–20/1–1800, bool rejected. AppController(clock:Callable[[],float]=time.monotonic):
select_image()->None,start_auto(limits)->None,request(source:str)->str|None,
complete(identifier:str,success:bool)->bool,stop()/recover()/close()->None.
Only one pending ID; reject busy requests, no FIFO. Next_due is completion+interval;
MainWindow refreshes it after display. Stop disarms; active bounded work drains safely.
AppRequest(identifier,source,path,directory,captured_at,session_id,save_frame=False,frame=None)
is frozen; IMAGE or WEBCAM, frame optional QImage. AnalysisWorker(session,storage,config)
QObject slots prepare_preview(identifier,path),analyze(AppRequest),close(); signals preview,
result,error,closed. No widgets in worker. Captured PNG encoding/provenance runs in worker.

## Storage / author review — app_storage.py

AppStorage(root:Path); path(relative:str)->Path confines resolved paths, rejects escapes/root.
allocate(identifier:str)->Path exclusive alnum/hyphen owned directory; save(directory:Path,
data:dict[str,Any],name:str='result.json')->Path atomic temp+replace; load(relative:str)->dict
validates windows-app-result-v1 and16MiB limit; history()->list[tuple[str,dict|None]] retains
corrupt entries as None; read_json(relative)->dict; sessions()->list[tuple[str,dict|None]].
review(relative)->dict defaults NOT_REVIEWED; update_review(relative,rating,note)->dict atomic
review.json with UTC. Ratings only NOT_REVIEWED/USABLE/PARTIALLY_USABLE/UNUSABLE; note<=10000.
Raw result/report/status unchanged. remove_frame(directory) deletes only marker-owned frame.png
and input/normalized.png; purge_ephemeral only explicit saveOFF owned records. No user originals.
I/O/path/schema errors propagate/read errors are displayed. Storage QLockFile prevents duplicate
GUI ownership. JSON result,review,session,session_cleanup and capture metadata are canonical.

## Export — app_export.py, app_export_schema.py

export_bundle(storage:AppStorage,kind:str='all')->Path, kind allowlist all/analysis_summary/
model_calls/webcam_sessions; new owned export directory. analysis_row(data,review=None)->dict,
call_rows(data)->list[dict],session_row(session,analyses)->dict,engineering_summary(rows)->dict.
analysis_summary.csv43columns,model_calls.csv16,webcam_sessions.csv32; exact schema/mappings:
THESIS_DATA_EXPORT_DESIGN.md. engineering_summary.json descriptive only; export_audit.json hashes,
errors/denominators. CSV UTF8BOM/CRLF/safe quoting, apostrophe guard on leading formula text,
canonical unchanged. Missing blank/null; real0 retained. REAL/MOCK/UNKNOWN explicit partitions.
No skipped call fabricated; actual backend receipts or clearly marked answered mock invocations.
Malformed history audited, not invented success. Export while app idle, not during active writer.

## Cleanup — MainWindow / session / transport

closeEvent marks closing, prevents work, releases camera and waits for queued worker.close,
then QThread completion. Never forcibly terminate QThread. end_image clears image resources
without unload. Final transport unload requires allocator allocated/reserved0, successful
worker exit, empty Windows Job and baseline device recovery within existing64MiB tolerance,
within cleanup10s (active operation drain measured separately). Failure remains explicit.
Worker creates cleanup.json and per-result session_cleanup.json; WebcamRecord retains cleanup
receipts. Fake cleanup cannot set physical success. Source/API tests prove only their tested scope.
