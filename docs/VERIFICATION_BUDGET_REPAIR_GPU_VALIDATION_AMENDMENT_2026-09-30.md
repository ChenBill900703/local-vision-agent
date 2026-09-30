# Prospective verification-budget repair GPU validation — 2026-09-30

PROPOSED / FROZEN SPECIFICATION / NOT EXECUTED / NO GPU AUTHORIZATION.
DEVELOPMENT ONLY / NOT FORMAL THESIS RESULT.
Current user authorization is CPU-only. This document does NOT authorize execution.
Future explicit approval must name this scope; revisions require a new dated amendment.

## Source and input

Exact repaired source commit: 538ef24c13686cbf2cc378ae8d078e8645beed34 (verification-budget-repair-cpu-ready).
Any later docs-only checkpoint may contain this source; all src/config hashes must match
this commit before execution. Unexpected drift: STOP. Full CPU suite/Ruff/Mypy must PASS.
Proposed exclusive new run ID: VERIFICATION_BUDGET_REPAIR_OUTDOOR_20260930_V1.
Proposed run directory: artifacts/verification-budget-repair-20260930/runs/VERIFICATION_BUDGET_REPAIR_OUTDOOR_20260930_V1.
One load, ONE input only: outdoor_scene_001, never GPU-executed as of this amendment.
Original: development_images/outdoor_scene_001.jpg
Original SHA256: adaf0193b5a16a49526347ea2cd0561d4cd6580fd038290dbacf4e4dbf76e736.
Approved derivative: artifacts/real-image-development-sanity-20260930/inputs/outdoor_scene_001_edge512.png
Derivative SHA256: 5e86f70d2afbf7725266eb569698a0f371757b3eadd521fdde1ce1d2831f1b77;384x512PNG,193476bytes.
User rights/non-sensitive/resize confirmation in prior ignored sanity evidence; local development
only, no cloud/image upload/Git/publication/identity recognition/formal test use. Keep originals.
Do not substitute indoor or rerun any consumed run. No asset acquisition/install permitted.

## Frozen runtime

InternVL3-2B-Instruct model/tokenizer/template f6c7b60375759170fd49f5e9e298e2178485c5ba.
Weights b69fcfb5cd97b91b52022642d88da91201487aa73750fa8b14a0e6591a5a9e2d.
Controlled patch e9374e89a0a0668af5cdd56ebf43a170fd1ff47798a9027cbdc6223754654c95.
Pinned runtime manifest/dependencies unchanged; validate existing hashes locally before load.
Config configs/agent_internvl_development.toml SHA256 e3bc387c91ed0e3fc816232f0563f9c83d8105401cff6cbe8be7e3eb1d97ab52.

```toml
# Development configuration; no automatic GPU authorization or formal evaluation freeze.
schema = "internvl-development-v1"
adapter = "internvl3-pinned"

[runtime]
preprocessing = "internvl-single-tile-rgb-bicubic448-imagenet-v1"
load_timeout_s = 180.0
session_timeout_s = 1800.0

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

```

Method D only; same finite PROMPTS in agent.py at exact commit, existing triggers/extractor,
FIFO verification within remaining model/tool/iteration/memory capacity; reserved modelcalls0.
Report agent-report-v2; policy bounded-policy-v2-verification-fifo. No ranked/LLM selection.
No forced object/detail/minimumcalls. Unknown candidate count is determined by actual output.
<=8model/toolcalls and iterations;128outputtokens/call;1024input and totaloutput/image.
BF16,cuda:0,eager,batch1,inference_mode,seed0,do_sample=false,temperature0,num_beams1,use_cache=true.
EOS/pad from pinned tokenizer/template; exact rendered prompts/tokenIDs/settings retained.
Same internvl-single-tile-rgb-bicubic448-imagenet-v1; single448x448RGBBICUBIC/ImageNet tile,
aspect ratio changes; no dynamic tiling. Development limitation, not final thesis preprocessing.

## Safety / cleanup / stop

Guard before heavyweight import/allocation:6000MiB estimate,6400MiB ceiling,1536MiB reserve,
5400MiB allocator cap. One worker/one image; no retry, offload, auto mapping, quantization,
second model or cloud/shared-memory fallback. Existing offline flags/Python denial audit;
shared GPU memory UNKNOWN / OBSERVABILITY LIMITATION. No OS firewall guarantee inferred.
Load180s,call60s,image300s,cleanup10s,session1800s. Hardware gate refusal ->no load.
Save resource snapshots/latency/raw calls/trace/coverage/Chinese report, process and cleanup.
Require0allocated/0reserved,workerexit0,Jobempty,device baseline-equivalent(existing64MiB).
On failure preserve exact state/error/raw logs, cleanup and STOP. No hidden repair/retry.

## Expected behavior and acceptance

Scheduler plans slots BEFORE calls, FIFO; no known over-budget attempt. Unselected candidates
remain unresolved with null verification_id and verification_budget_not_available. Actual
attempts/completions/coverage match trace. If candidates exceed slots, status complete with
COMPLETED_WITH_PARTIAL_VERIFICATION and VERIFICATION_BUDGET_EXHAUSTED is acceptable engineering
completion, not full verification. NO_TRIGGER remains an investigation-only result.
Coverage does not measure correctness; valid unresolved responses count as completed checks.
Token_limit/truncated and token counts visible, raw text unchanged;128cap not increased.

PASS: real Adapter/InternVL/Agent executes normally, all attempted verification calls valid,
no extra call or unexpected TOOL_CALL_LIMIT, exact coverage/unresolved evidence links, report
completion (including explicitly bounded partial verification), offline/resource/placement/
cleanup/process recovery PASS AND subsequent user HUMAN development review usable.
Until human review, engineering success is provisional/CONDITIONAL. FAIL on runtime/transport/
OOM/timeout/fallback/limit-bypass/invalidlink/offline/resource/cleanup failure or unusable human review.
All-candidates-verified is NOT required. No RQ2-RQ4, quality improvement or statistics claims.
No automatic baseline READY: future success permits a proposed decision subject to user review.
After engineering acceptance, stop feature expansion; formal experiment design freeze is next,
not formal test execution. This CPU-only phase ends without any execution of this amendment.
