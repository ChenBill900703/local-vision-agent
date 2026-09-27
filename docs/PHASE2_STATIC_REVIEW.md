# Phase 2 static review / acquisition decision — 2026-09-27

This is the preserved pre-execution decision. Subsequent initial pilot is FAIL overall;
see MOONDREAM2_GPU_FEASIBILITY_REPORT.md. It does not authorize a second attempt.
The actual additional PyTorch allocator cap used was 5400 MiB; process ceiling remains 6400 MiB.

PILOT / EXPLORATORY / NOT FORMAL THESIS RESULT

User authorization: pasted request retained in ignored `artifacts/phase2-20260927/evidence/user_authorization.txt`.
Local baseline (before Phase 2 source/config/dependency edits): `14c675bcaf18f0abb9a099a8def7caf9ad7016b8`, message `baseline-rd001-phase1-complete`; no push.

## Source and usage decision

Moondream2 `9a7d4024050840e001defacec2b00727e89149e6`, release `2025-06-21`, rechecked against official Hub API and [commit](https://huggingface.co/vikhyatk/moondream2/commit/9a7d4024050840e001defacec2b00727e89149e6).
Fixed README declares Apache-2.0. Preserve original README and hashes; no redistribution of weights/code in this commit.
Tokenizer `moondream/starmie-v1@35192e10a54e36eabe0a7cc57a2c1aab371cafc5`; public official repository, no explicit license in its README.
Local research usage evidence: official Apache-declared Moondream2 code intentionally invokes this exact official tokenizer repository; [Hugging Face Terms, Your Content](https://huggingface.co/terms-of-service) grants users use/reproduction of public content through Hub services/functionality. This supports proceeding with the officially intended downloaded tokenizer for this local research pilot; it is not a statement that tokenizer has Apache licensing or unrestricted redistribution rights. Tokenizer public redistribution remains UNKNOWN / RELEASE GATE. No public release is authorized.

Acquisition allowlists record filename, URL, full revision, exact expected bytes and purpose in ignored `model_allowlist.json` / `tokenizer_allowlist.json` **before download**. Actual bytes and SHA256 are separate receipts. Only named artifacts, not entire repositories or GGUF. Weight expected bytes 3,854,538,968; expected SHA256 `70a7d94c0c8349eb58ed2d9e636ef2d0916960f321ecabeac6354b8ba3d7403f` from official LFS metadata.
Artifact HTTP payload ledger caps at 4.9 GB (below 5 GB authorization, allowing metadata/transport margin); new artifacts <=12 GB. No automatic download retries. Evidence backup excludes duplicate weights.

## Complete downloaded Python review (text only before model execution)

Reviewed config.py, hf_moondream.py, moondream.py, vision.py, text.py, region.py, image_crops.py, layers.py, lora.py, rope.py, fourier_features.py, utils.py, weights.py in full. Receipts retain exact upstream hashes.

| Surface | Finding and control |
|---|---|
| Import closure | Active direct core: torch, numpy, Pillow, tokenizers; safetensors for controlled loading; Python standard library. Relative imports among config/moondream/image_crops/vision/text/region/layers/lora/rope/utils. hf_moondream and weights/fourier_features not needed for this loader; reviewed nonetheless |
| Optional imports | pyvips has Pillow branch; torchao only quantized branch. No quantization, no variants. einops absent in active closure. Transformers/accelerate wrapper bypassed, not upgraded |
| Network | Moondream constructor has unpinned Tokenizer.from_pretrained; patch to verified local tokenizer.json. lora.py can download variants from api.moondream.ai; replace with fail-closed variant stub. No other active network use found |
| Commands / writes | No subprocess/exec/shell execution in active model path. lora download/cache writes removed. Model core has no output file writes; our harness saves evidence only |
| Deserialization | Load ONLY verified safetensors. Do not call old weights.py or variant torch.load, and no pickle model artifacts |
| Placement | Construct under explicit cuda:0 default device; load one tensor at a time directly from safetensors onto cuda:0, copying into preallocated CUDA parameters, not a full duplicate GPU state_dict. Inspect every parameter/buffer; inspect encoded caches and compute inputs |
| Precision | BF16 dense parameters, no automatic quantization or precision change. Rotary-frequency buffers float32 and masks bool by design |
| KV/cache | 24 layers, 32 KV heads, context 2048, head dim 64, two BF16 caches: 384 MiB. One image embedding prefix clone (730 positions) about 136.875 MiB. No multiple image cache retention |
| Generation | Active _generate_answer checks EOS and max_tokens. Controller requires <=128, explicit temperature=0/top_p=1, no reasoning. Context budget checks image prefix + full prompt (including duplicated query suffix in upstream) + output <=2048 |
| Image | CPU decode bounded at <=512 edge/262144 pixels/10 MiB. Default crop grid at these dimensions has at most 4 local +1 global crops; inspect actual CUDA input shapes. Do not raise max_crops or enable video |
| Release | Delete encoded caches/model, gc, empty_cache, synchronize; record allocated/reserved and worker exit. Parent can terminate entire worker on deadline; no retry |
| Advanced tools | detect/point/gaze/grounding/reasoning/compile not exposed by pilot commands; variants rejected; no second model |
| Offline | All assets validated before worker. Set HF_HUB_OFFLINE/TRANSFORMERS_OFFLINE, replace tokenizer with local from_file; deny Python socket connection attempts and log them. This is an offline-mode + audited-runtime test, not an OS firewall guarantee |

Dependency decision: **no installs needed for this direct-core pilot**; existing torch 2.7.1+cu126 / transformers 4.57.6 remain unchanged. Use existing tokenizers/safetensors/numpy/Pillow, capture exact metadata in evidence. Optional pyvips/torchao paths are removed/disabled in controlled code. General package internals are trusted installed dependencies, not exhaustively security-audited.

## Controlled changes before first execution

Create a separate local package from reviewed files, preserve upstream bytes untouched. Pin tokenizer to local file, remove optional pyvips/torchao/variant/MPS fallback selection, remove dynamo marking because compilation is disabled, record generated token IDs for exact token counts. Device contexts keep position tensors on CUDA. Preserve algorithms, prompt templates and dense weights otherwise. Store exact unified diff, patch SHA256 and every controlled file SHA256; worker verifies them before import. These changes are engineering controls, not a new model or research direction.

## Provisional memory estimate, before actual load

**UNMEASURED PILOT ESTIMATE: 6000 MiB total workload allowance**, subject to GPU free >=7536 MiB before framework/model loading and process ceiling 6400 MiB. CUDA initialization overhead is included here, not silently ignored.

| Component | MiB allowance / evidence |
|---|---|
| Dense weights including visual encoder, text, region | ceil(3,854,538,968 / 2^20) = 3676; exact tensor header/dtypes to verify after download |
| Full KV caches | 384, formula above |
| One encoded prefix clone | 137 |
| Masks/rotary/other buffers | 16 |
| Single largest weight staging (no whole duplicate) | 256; largest expected embedding/head ~200 MiB |
| Activations / SDPA / crop / GEMM workspace | 640; bounded <=5 crops, inference mode, <=128 outputs |
| CUDA context / library overhead / allocator fragmentation margin | 891 (residual to 6000); initial torch CUDA baseline shows substantial free-memory reduction |

This is a conservative engineering allowance, not a proven upper bound; no training graphs. Assert allocator reserved <=6400 MiB and free dedicated >=1536 MiB at boundaries, monitor parent dedicated usage while running, abort on violation. Allocator fraction provides an additional PyTorch allocation guard, not a driver/Windows hard limit. Compare post-init CUDA free with remaining tensor allowance accounting for already-consumed context; stop if insufficient. If 6000+1536 does not fit actual preflight, do not lower estimate just to pass.
Windows performance counters show multiple adapter LUIDs; initially not mapped unambiguously to NVIDIA. Shared usage attribution may remain UNKNOWN / OBSERVABILITY LIMITATION; never claim zero spill proven.

Acceptance here permits one controlled attempt after all recorded checks, not a guarantee the model will run. Any OOM/timeout/exception ends session; no automatic repair/reload.
