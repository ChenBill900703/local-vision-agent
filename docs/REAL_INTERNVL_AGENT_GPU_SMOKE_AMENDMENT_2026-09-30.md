# Prospective Real InternVL Agent GPU Smoke Amendment — 2026-09-30

DEVELOPMENT ONLY / PILOT / NOT FORMAL THESIS RESULT

## Authorization and immutable identity

User attachment retained in artifacts/internvl-real-agent-smoke-20260930/evidence/user_authorization.txt.
ONE new load/session only, Method D only. No A/B/C, retries, model/prompt/policy changes,
downloads, installs, formal experiments or push. Failure: preserve, cleanup, stop and propose repair.
Run ID: INTERNVL_REAL_AGENT_GPU_SMOKE_20260930.
Exclusive run directory: artifacts/internvl3-20260928/runs/INTERNVL_REAL_AGENT_GPU_SMOKE_20260930.
After execution preserve all raw files unchanged; analysis/backup lives outside that directory.
Base source HEAD: c2ce0b24a61c257db9cdc232f45dd4c95e30521f; branch main; initial dirty state CLEAN.
All integration-record source hashes match. Runtime source/config unchanged.
Full source hashes/dependencies/22 pinned asset and framework hashes: evidence/resume_audit.json.
Prechecks: 93 CPU tests PASS (12.038s), Ruff PASS, strict Mypy28 PASS.

## Frozen runtime

Model/tokenizer/template: OpenGVLab/InternVL3-2B-Instruct, f6c7b60375759170fd49f5e9e298e2178485c5ba.
Weights SHA256: b69fcfb5cd97b91b52022642d88da91201487aa73750fa8b14a0e6591a5a9e2d.
Controlled patch SHA256: e9374e89a0a0668af5cdd56ebf43a170fd1ff47798a9027cbdc6223754654c95.
Config: configs/agent_internvl_development.toml SHA256 e3bc387c91ed0e3fc816232f0563f9c83d8105401cff6cbe8be7e3eb1d97ab52.
Fixture: original synthetic_shapes.png, 384x256 white/red-square/blue-circle development fixture.
Fixture SHA256: 7a902b90e90b2c89ff91cd78a23f5a8b9d42bb4ca15a24775736ee9afb1d463f.
Preprocessing: internvl-single-tile-rgb-bicubic448-imagenet-v1: one448x448 RGB BICUBIC tile,
ImageNet normalization, no thumbnail. Aspect ratio changes; NOT final thesis preprocessing.
BF16, cuda:0, eager, batch1, inference_mode; no CPU/disk offload, auto mapping, second model,
quantization, compilation or shared-memory fallback. Seed0; no guarantee of bitwise repeatability.
Greedy: do_sample=false, temperature0, num_beams1, use_cache=true, max_new_tokens128 or remaining
Agent budget; EOS/pad IDs resolved from pinned tokenizer/template and recorded in every call.
Rendered system/chat prompts and token IDs retained unchanged. Query logic is source at base HEAD.

## Exact finite prompt library

```python
{
    "caption": "以繁體中文描述圖片的場景、重要物件與可見細節；不確定時明示。",
    "scene": "以繁體中文描述可見場景，不推測不可見的背景。",
    "object": "以繁體中文檢查重要物件；看不清楚的物件請標示未確定。",
    "detail": "以繁體中文描述可見細節；不要推測看不見的屬性。",
    "verify": "檢查候選敘述，回報 supported、contradicted 或 unresolved；非獨立真值：",
}
```
Verification appends each actual literal candidate; no post-result prompt tuning.
Normalizer: literal-sentence-claims-explicit-verdict-v1; unverified claims unresolved.
Only explicit supported/contradicted/unresolved verdict parsed. Same-model checks are not ground truth.

## Bounds and state contract

{
  "limits": {
    "max_tool_calls": 8,
    "max_model_calls": 8,
    "max_iterations": 8,
    "per_call_timeout_s": 60.0,
    "per_image_timeout_s": 300.0,
    "cleanup_timeout_s": 10.0,
    "max_input_bytes": 10485760,
    "max_pixels": 262144,
    "max_image_edge_px": 512,
    "max_input_tokens": 1024,
    "max_output_tokens": 128,
    "max_total_output_tokens": 1024,
    "max_response_chars": 8192,
    "max_memory_entries": 8,
    "max_batch_images": 1
  },
  "preprocessing": "internvl-single-tile-rgb-bicubic448-imagenet-v1",
  "load_timeout_s": 180.0,
  "session_timeout_s": 1800.0
}

Preflight before heavy imports:6000MiB planning estimate,6400MiB process ceiling,
1536MiB reserve beyond desktop and estimate,5400MiB allocator cap; stop before load if refused.
START -> INITIAL_CAPTION -> SCENE_ANALYSIS -> OBJECT_CHECK decision -> DETAIL_QUERY decision
-> VERIFICATION (one per candidate within bounds) -> REPORT -> STOP.
Object/detail queries only if current triggers require them; preserve actual skipped branches.
No-new-evidence stop is conditional; no forced calls to demonstrate it. Record whether exercised.
Claim/evidence links and raw responses must agree; valid transport is not semantic correctness.

## Measurement and acceptance

Existing worker measurements: preflight/baseline, model_loaded, image_ready, visual_done,
call_done, cleanup_start/done, termination and device recovery; CUDA-synchronized call measurements.
cleanup_start is a timestamp, not a new allocator snapshot; last call snapshot will be explicitly
identified as preceding cleanup, never misrepresented as a fresh reading. Parent GPU sampler spans it.
Parent-only profile callback adds timing for Agent.run, report serialization and file writing;
no model callback, policy changes, or extra query. Retain profile overhead in measured durations.
Launcher SHA256: c17b2da0672b1e7a25bd03ce5886aaa43ef7d5f4b43a4643790e1341fc1096af.
CUDA allocations/peaks, NVIDIA device used/free, worker PID and Job exit are logged where available.
Windows shared GPU memory = UNKNOWN / OBSERVABILITY LIMITATION.
HF offline flags + Python network-denial audit; no claim of native/OS firewall proof.

PASS only if guarded real load/image/Agent calls/normalization/state transitions/selected verification,
trace links/structured Chinese report all complete, no malformed RPC/fallback/OOM/timeout,
resource/offline policy satisfied and cleanup allocator0/reserved0/process exit0/Job empty/device
baseline-equivalent (existing tolerance64MiB) within10s. Any failure gives FAIL and no retry.
No hallucination/quality metric or RQ2-RQ4 claim. Do not mark engineering baseline ready until
separately scoped rights-confirmed natural-image sanity is completed. This amendment is frozen
before execution; corrections require a new dated amendment/run, never edits after observation.
