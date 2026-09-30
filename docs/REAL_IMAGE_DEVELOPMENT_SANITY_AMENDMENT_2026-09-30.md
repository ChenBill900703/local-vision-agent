# Real Image Development Sanity — prospective amendment, 2026-09-30

DEVELOPMENT ONLY / NOT FORMAL THESIS RESULT. Frozen BEFORE GPU execution.
User full request and rights statement retained under ignored artifacts/real-image-development-sanity-20260930/evidence.
User separately approved local aspect-preserving <=512 derivatives, EXIF removal, original preservation,
and confirmed no specified sensitive content. Images never sent to development assistant/cloud;
privacy suitability is USER-ATTESTED, not independently visually reviewed by assistant.
No identities inferred. No public release, Git image inclusion, or formal test use.

## Exact images and rights

TWO authorized inputs; user self-photographed or has rights to supply for this local development task.
Original inputs both exceeded pixel/edge limits and were refused BEFORE GPU. Original bytes unchanged.
Explicitly approved derivatives: EXIF transpose -> RGB -> LANCZOS thumbnail longestedge512 -> metadata-free PNG.
This input preparation is separate from unchanged model preprocessing. No content retouching.

```json
[
  {
    "path": "development_images\\indoor_desk_001.jpg",
    "sha256": "7263bdd7ec21160c7097500873845b5061b83adb09dd03b6ef46b1729f49722b",
    "bytes": 3745234,
    "width": 4624,
    "height": 3472,
    "format": "JPEG",
    "input_gate": "IMAGE_PIXELS_LIMIT",
    "rights_confirmed": true,
    "privacy_confirmation": "USER_CONFIRMED_NON_SENSITIVE",
    "gpu_attempted": false,
    "derivative": "artifacts\\real-image-development-sanity-20260930\\inputs\\indoor_desk_001_edge512.png",
    "derivative_sha256": "1268d6188c74182ce06918daee12055a9d8168706bae7ff21d6392493e6f3d1a",
    "derivative_width": 512,
    "derivative_height": 384,
    "derivative_bytes": 227687,
    "derivative_input_gate": "PASS",
    "conversion": "EXIF transpose, RGB, LANCZOS aspect-preserving thumbnail max512, metadata-free PNG",
    "run_id": "REAL_IMAGE_SANITY_20260930_INDOOR_DESK_001"
  },
  {
    "path": "development_images\\outdoor_scene_001.jpg",
    "sha256": "adaf0193b5a16a49526347ea2cd0561d4cd6580fd038290dbacf4e4dbf76e736",
    "bytes": 3437516,
    "width": 3472,
    "height": 4624,
    "format": "JPEG",
    "input_gate": "IMAGE_PIXELS_LIMIT",
    "rights_confirmed": true,
    "privacy_confirmation": "USER_CONFIRMED_NON_SENSITIVE",
    "gpu_attempted": false,
    "derivative": "artifacts\\real-image-development-sanity-20260930\\inputs\\outdoor_scene_001_edge512.png",
    "derivative_sha256": "5e86f70d2afbf7725266eb569698a0f371757b3eadd521fdde1ce1d2831f1b77",
    "derivative_width": 384,
    "derivative_height": 512,
    "derivative_bytes": 193476,
    "derivative_input_gate": "PASS",
    "conversion": "EXIF transpose, RGB, LANCZOS aspect-preserving thumbnail max512, metadata-free PNG",
    "run_id": "REAL_IMAGE_SANITY_20260930_OUTDOOR_SCENE_001"
  }
]
```

## Frozen execution

Source HEAD447fe603bdeceb6ec606b559ab6039ba096d801d, branch main.
All src hashes match preceding real smoke; previous raw smoke hashes unchanged.
Resume dirty state only untracked development_images/. Ignore rule now prevents Git inclusion.
93 CPU tests PASS(10.358s), Ruff PASS, strict Mypy28 PASS; asset/framework hashes verified.
Model/tokenizer/template: OpenGVLab/InternVL3-2B-Instruct f6c7b60375759170fd49f5e9e298e2178485c5ba.
Weights b69fcfb5cd97b91b52022642d88da91201487aa73750fa8b14a0e6591a5a9e2d.
Controlled patch e9374e89a0a0668af5cdd56ebf43a170fd1ff47798a9027cbdc6223754654c95.
Exact asset/source hashes and dependencies in evidence/resume_audit.json.
No model/runtime/source/config/dependency change. BF16/cuda:0/eager/batch1/inference_mode/seed0.
Greedy do_sample=false,temperature0,num_beams1,use_cache=true; max_new_tokens128 or remaining budget.
Pinned template and tokenizer supply EOS/pad/BOS; fully rendered prompts and IDs logged.
One448x448RGB BICUBIC/ImageNet tile, no thumbnail/dynamictiling:
internvl-single-tile-rgb-bicubic448-imagenet-v1. ASPECT RATIO CHANGES; DEVELOPMENT LIMITATION;
final thesis preprocessing remains unfrozen.
Method D only, bounded-policy-v1; literal-sentence-claims-explicit-verdict-v1.

## Exact finite prompt library

```json
{
  "caption": "以繁體中文描述圖片的場景、重要物件與可見細節；不確定時明示。",
  "scene": "以繁體中文描述可見場景，不推測不可見的背景。",
  "object": "以繁體中文檢查重要物件；看不清楚的物件請標示未確定。",
  "detail": "以繁體中文描述可見細節；不要推測看不見的屬性。",
  "verify": "檢查候選敘述，回報 supported、contradicted 或 unresolved；非獨立真值："
}
```
Verification appends actual candidate verbatim. No forced queries, no prompt tuning, no semantic judge.
START/caption/scene/object decision/detail decision/verification/report/stop obey existing controller.
All observations/claims start fresh per image; one separate safe worker lifecycle per image.
Indoor FIRST. Outdoor only after indoor execution and cleanup PASS. Any failure: stop, no retries.
Each run directory exclusive under artifacts/real-image-development-sanity-20260930/runs/; immutable after run.

## Exact active configuration

```json
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
```
GPU preflight before heavy imports:6000MiB estimate,6400MiB ceiling,1536MiB reserve,5400MiB cap.
No CPU/disk offload,auto mapping,quantization,secondmodel,cloud/shared-memory fallback.
Cleanup requires allocated0/reserved0/exit0/Jobempty/baseline recovery(existing64MiB tolerance).
Existing HF offline flags/Python audit; native network proof not claimed; sharedGPU memory UNKNOWN.

## Evidence and prospective acceptance

Save raw prompts/responses/tokenIDs/counts, observations/claims/verification/evidence links/states,
Chinese report, latency/resource checks and cleanup. No raw rewriting; same-model supported not ground truth.
User HUMAN review of ALL raw responses follows execution: reasonable scene/main objects/plausibility,
blatant nonexistent objects/usable Traditional Chinese/sensible verification. No formal metrics.
PASS requires suitable rights-confirmed inputs, prechecks and real pipeline/budgets/offline/cleanup PASS
AND human finds development behavior usable. Until human review, verdict CONDITIONAL.
Runtime error/OOM/timeout/malformedRPC/fallback/offline/resource/cleanup failure: FAIL and stop.
Bounded partial report is retained, not promoted to full engineering PASS; no repair/rerun here.
No A/B/C, prior-run repeats, dataset/model acquisition, installs, public release or formal experiments.
Baseline READY decision only AFTER sanity PASS including human review. Otherwise retain blockers.
