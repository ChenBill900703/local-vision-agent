# Combined smartphone input + verification budget GPU validation — 2026-09-30

FROZEN PROSPECTIVE SPECIFICATION / NOT EXECUTED / PENDING EXPLICIT AUTHORIZATION.
DEVELOPMENT ONLY / NOT FORMAL THESIS RESULT.
Current authorization CPU ONLY. Do NOT execute based on this document.

## Exclusive scope and source

Proposed new run ID SMARTPHONE_COMBINED_OUTDOOR_20260930_V1.
Proposed evidence directory artifacts/smartphone-source-repair-20260930/runs/SMARTPHONE_COMBINED_OUTDOOR_20260930_V1.
Exclusive immutable raw run; auto-normalized input sibling <run>-input retained privately.
ONE original outdoor image, ONE load/session, Method D only, no retries/additionalcalls/runs.
Exact source commit bdf9dd2cb3b5657cf2e33a0efa5829b5b614c694 (smartphone-source-input-cpu-ready).
Any subsequent docs-only HEAD must match this exact src/config/tests; unexpected drift STOP.
Before execution: verify source/assets/config/image/dependency hashes, fullCPUtests/Ruff/Mypy.
Old derivative-based VERIFICATION_BUDGET_REPAIR_OUTDOOR_20260930_V1 remains NOT EXECUTED,
not to be used. Do not edit old amendments, rerun indoor, synthetic or consumed pilots.

## Original input and rights

User-facing input MUST be development_images/outdoor_scene_001.jpg (3472x4624 JPEG).
Original SHA256 adaf0193b5a16a49526347ea2cd0561d4cd6580fd038290dbacf4e4dbf76e736.
User confirmed rights/local-only/development/non-sensitive; no formal test use, public release,
Git image inclusion, cloud upload or identity recognition. Retained prior rights statements apply;
no independent assistant visual review asserted. No new image acquisition.
Do NOT supply the existing edge512 derivative as input. Program must validate original,
record original path/hash/bytes/dimensions/format, strict decode, EXIFtranspose/RGB/LANCZOS
aspect-preserving <=512 automatically, then original448single-tilemodelpreprocessing.
The internal derivative and source provenance are local ignored evidence only.

## Configuration / model freeze

Config SHA256 05b5d92a28659630cd5a5e2f9593ffd06241ab2c4f7a5379c82f7e43f41f20d1.
```toml
# Development configuration; no automatic GPU authorization or formal evaluation freeze.
schema = "internvl-development-v2"
adapter = "internvl3-pinned"

[runtime]
preprocessing = "internvl-single-tile-rgb-bicubic448-imagenet-v1"
load_timeout_s = 180.0
session_timeout_s = 1800.0

# These image limits apply ONLY to normalized/internal model-facing input.
[limits]
max_tool_calls = 8
max_model_calls = 8
max_iterations = 8
per_call_timeout_s = 60.0
per_image_timeout_s = 300.0
cleanup_timeout_s = 10.0
max_input_bytes = 10485760
max_pixels = 262144
max_image_edge_px = 512
max_input_tokens = 1024
max_output_tokens = 128
max_total_output_tokens = 1024
max_response_chars = 8192
max_memory_entries = 8
max_batch_images = 1

[source_image_limits]
max_compressed_bytes = 33554432
max_decoded_pixels = 32000000
max_source_edge_px = 10000
formats = ["JPEG", "PNG"]

```
Source policy32MiB/32MP/10000edge,JPEG/PNG, strictdecode; conservative RAMplan~2.97GiB
on32GBhost, not measured peak/hard cap. Source validation occurs before GPU load.
Model normalized/internal input <=10MiB/262144pixels/512edge; one448x448RGBBICUBIC tile,
ImageNet normalization, no dynamic tiling. Aspect ratio changes in model stage. Fine detail,
tiny text,small signs,distant objects may be lost. Usability test, not high-resolution understanding.
Model/tokenizer/template InternVL3-2B-Instruct f6c7b60375759170fd49f5e9e298e2178485c5ba.
Weights b69fcfb5cd97b91b52022642d88da91201487aa73750fa8b14a0e6591a5a9e2d;
controlled patch e9374e89a0a0668af5cdd56ebf43a170fd1ff47798a9027cbdc6223754654c95.
Pinned dependencies/assets unchanged. BF16,cuda:0,batch1,eager,inference_mode,seed0.
Greedy do_sample=false,temperature0,num_beams1,use_cache=true,128maxnewtokens or remaining;
EOS/pad/template from pinned assets; render exact prompts/tokenIDs/settings to evidence.
Finite PROMPTS/claim extraction/triggers at source commit unchanged; Method D only.
FIFO remainingcall planner,8maxcalls/iterations; zero reserved modelcalls; report schema v2.
Unselected candidates unresolved/null verification_id/verification_budget_not_available;
coverage completed/candidates (not correctness). COMPLETED_WITH_PARTIAL_VERIFICATION and
VERIFICATION_BUDGET_EXHAUSTED are accepted bounded completion, no extra overbudget attempt.

## Safety / evidence / stop

Preflight before heavyweight import:6000MiB planningestimate/6400ceiling/1536reserve/5400cap.
No offload/auto mapping/sharedmemoryfallback/quantization/secondmodel/fullresolution CUDA.
Load180s,call60s,image300s,cleanup10s,session1800s. Stop-beforeload if guard refuses.
Existing offline flags/Python networkdenial; missingasset/fetch/runtime/OOM/timeout ->STOP.
Retain original/normalized metadata/hashes,sourceconfig,call/state/request/rawanswers,
renderedprompts/tokens,coverage/evidencelinks/truncation,Chinese report,latencies/VRAM/checkpoints,
errors/stopreason,cleanup/process exit/device recovery. Never rewrite raw output.
Require allocated0/reserved0,workerexit0,Jobempty,devicebaseline equivalent(existing64MiB).
Windows sharedGPU memory UNKNOWN; no OS/native-network guarantee from Python audit.
One load only; cleanup on failure, preserve partial trace, no silent repairs/retries.

## Prospective acceptance

PASS engineering behavior only if originalphone accepted with correct CPU sourceprovenance,
autobounded normalization and unchanged modelbounds; actualAdapter/RPC/InternVL/MethodD succeeds;
FIFO never exceeds availablebudget; attemptedchecks valid; unverifiedclaims unresolved;
coverage matches actualtrace; generation tokenlimit/truncated explicit; report completes;
offline/resource/placement/cleanup/processrecovery PASS AND userhumanreview development usable.
Bounded partial verification allowed; allclaimsverified not required. Actual branches may skip
queries; do not force them. Humanreview PENDING means CONDITIONAL, not assumed approval.
FAIL on source/runtimetransport/budgetbypass/invalidprovenance/invalidlinks/offline/resources/
cleanup failure or unusable humanreview. No prompttuning, limitincrease or modelchange.
Future engineering baselineREADY only subject to user review after this run; no RQ2-RQ4,
hallucination-reduction/A-D superiority/generalaccuracy claims. Formal design freeze later.
This amendment is prospective and immutable; new corrections need new dated specification.
