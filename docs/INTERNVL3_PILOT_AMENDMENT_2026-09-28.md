# InternVL3 initial pilot — frozen before execution

PILOT / EXPLORATORY / NOT FORMAL THESIS RESULT

User-confirmed implementation amendment, 2026-09-28; no research-direction change.
One exclusive run ID `INTERNVL3_INITIAL_GPU_PILOT`, one load, no retry on error/OOM.
Prior Moondream checkpoint/evidence immutable. Source selection/security/license/estimate:
[static review](INTERNVL3_STATIC_REVIEW_2026-09-28.md).

Selected model/tokenizer/config/processor/template SHA:
`f6c7b60375759170fd49f5e9e298e2178485c5ba`, OpenGVLab/InternVL3-2B-Instruct.
Weights SHA256 `b69fcfb5cd97b91b52022642d88da91201487aa73750fa8b14a0e6591a5a9e2d`.
685 BF16 tensors, 4,177,914,880 tensor bytes, largest tensor465,942,528 bytes.
Controlled optional-import patch SHA256
`e9374e89a0a0668af5cdd56ebf43a170fd1ff47798a9027cbdc6223754654c95`.
Runtime manifest validates all local assets and selected installed Transformers source.

## Execution contract

- Existing Python3.11.9/torch2.7.1+cu126/Transformers4.57.6; no installs/upgrades.
- Preflight before heavyweight imports; estimated6000MiB, ceiling6400MiB,
  dedicated free reserve1536MiB, allocator cap5400MiB. No auto map or offload.
- Batch1 BF16 cuda:0, eager attention, no flash/apex/kernels substitution.
- Offline flags + deny/audit Python networking throughout the ONE load and all queries;
  no second online-then-offline load. This satisfies offline test in same bounded session.
- Original synthetic-shapes-v1 hash
  `7a902b90e90b2c89ff91cd78a23f5a8b9d42bb4ca15a24775736ee9afb1d463f`;
  384x256 source, single448x448 tile, no thumbnail/additional crops. No real images:
  none provided with verified rights/consent/development split for this turn.
- Source limits512edge/262144pixels/10MiB; <=1024 complete input tokens including image
  and system tokens; <=128 generated tokens/call; <=8 calls and1024 generated tokens/image.
- Load180s, call60s, image300s, cleanup10s, session1800s. Windows Job and pipe deadlines;
  independent NVIDIA sampling with fail-closed stale telemetry. Exclusive run directory.
- Greedy generation: temperature0, do_sample=False,num_beams1,max_new_tokens128,
  EOS=tokenizer(template.sep.strip()),pad=tokenizer.pad_token_id,use_cache=True.
  Temperature is inactive with greedy generation; exact GenerationConfig logged.
- No prompt search; fresh conversation/KV each call. Standard pinned internvl2_5 system
  prompt and single-turn wrapper reproduced exactly from upstream chat; raw generated
  tokens, unmodified decoded response and special-token decoding all retained.
- Visual extraction once per query, passed as visual_features to upstream generate;
  this is real repeated visual compute, not cached replay. Extraction and generation
  measured separately with synchronization. Inspection includes params/buffers/pixels/
  visual embeddings/input IDs/masks/returned KV. Unsupported/unobservable KV fails closed.

## Exact order and prompts

1. A: `What shapes are in the image, and what color is each shape?`
2. B: `圖片中有哪些形狀？它們分別是什麼顏色？請只使用繁體中文回答。`
3. C: `請使用繁體中文簡潔描述這張圖片的主要內容。`
4. D: `Answer in Traditional Chinese only. Describe the main visible contents of this image.`

User semantic/language criteria apply (correct red square/blue circle; predominantly
Traditional Chinese, no echo, no invented major objects). PARTIAL is not PASS.
For safe optional-probe scheduling, frozen `internvl_policy.probe_gate` accepts only
conservative fixture wording with both correct color/shape pairs, no unsupported words,
simplified Chinese, uncertainty or contradiction. This deliberately may reject a valid
paraphrase. It is NOT a general semantic judge, GPT judge or thesis metric. If not accepted,
skip all probes and report the scheduling limitation separately from reviewed raw output.
Never change its vocabulary after observing this run. No automatic translation.

Only when all four pass this conservative gate, continue exactly:

5. `這張圖片主要是什麼場景？`
6. `請列出畫面中明顯可見的主要物件。`
7. `背景中還有哪些明顯且可以確認的物件？`
8. `敘述：圖片中有紅色正方形。請重新檢查圖片，這個敘述是否能由圖片直接支持？若不能確定，請明確說無法確定。`

Verification claim fixed in advance, usable only if C actually expresses it (gate requires
the pair); it is not independent ground truth. Report capability usability and limitations.
One synthetic fixture cannot establish general quality or research improvement.

## Stop / evidence / handoff

Any OOM/runtime/security/resource failure: save complete error, no retry/change of
precision/tile/model; cleanup and exit. Preserve all negative results. No natural failure
may be hidden by further prompt variants. Require zero allocated/reserved after cleanup,
process-tree exit and device recovery; shared-memory spill proof remains UNKNOWN.
Save provenance/dirty state/source hashes, all prompts/token IDs/raw responses/settings,
VRAM checkpoints and latency, telemetry/errors/cleanup and offline audit.
Produce feasibility report and SESSION_HANDOFF; stop before real adapter integration.
