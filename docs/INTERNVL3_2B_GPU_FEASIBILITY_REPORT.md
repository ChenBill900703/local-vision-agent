# InternVL3-2B GPU feasibility report — 2026-09-28

**PILOT / EXPLORATORY / NOT FORMAL THESIS RESULT**

## Verdict

**CONDITIONAL PASS — SMALL ENGINEERING BLOCKER**

One real offline GPU load completed. English QA, direct Traditional Chinese QA,
Traditional Chinese caption and English-instruction-to-Traditional-Chinese output
all describe the fixture correctly. Safety, observed placement and cleanup passed.
This is a development-fixture inspection, not a GPT runtime judge or formal metric.
User/author review of raw answers remains required before accepting the candidate.

The four Agent capability probes were **NOT RUN**. The development scheduler's
conservative lexical gate rejected valid English words `left`/`right` and Chinese `了`.
This is an assistant-authored engineering restriction, not a demonstrated model failure.
The gate and raw results are preserved unchanged. No post-result whitelist changes,
second load, extra prompts, fallback or Agent integration were performed.
Full adoption gate is therefore incomplete; do not label ADOPT or full feasibility PASS.

## Candidate selection / rights / environment

Selected **OpenGVLab/InternVL3-2B-Instruct** at
`f6c7b60375759170fd49f5e9e298e2178485c5ba` for weights/config/tokenizer/processor/template.
The official -hf conversion maps the default InternVL3-2B checkpoint; Instruct explicitly
omits MPO. They are not established as equivalent checkpoints, so the user rule selected
the Instruct distribution. Only this distribution's weights were acquired.
See [official Instruct source](https://huggingface.co/OpenGVLab/InternVL3-2B-Instruct/tree/f6c7b60375759170fd49f5e9e298e2178485c5ba),
[official hf source](https://huggingface.co/OpenGVLab/InternVL3-2B-hf/tree/cb57a075cb75a2e6d1b668b128d48bb00ae321d2)
and [complete static comparison/review](INTERNVL3_STATIC_REVIEW_2026-09-28.md).

Local research usage supported by retained MIT/Apache and linked Qwen grants.
Card metadata inconsistency and third-party notice obligations remain recorded:
**PUBLIC RELEASE RIGHTS = UNKNOWN**. No weights/code redistribution authorized.
Separate pinned official model/base/tokenizer/template license evidence is in evidence/.

Existing Windows/Python3.11.9, torch2.7.1+cu126, CUDA runtime12.6,
torchvision0.22.1+cu126, transformers4.57.6, numpy2.4.6, Pillow12.3.0,
safetensors0.8.0, tokenizers0.22.2, packaging26.3. NVIDIA driver591.86.
**No dependencies installed, removed or upgraded.**
No timm/einops/accelerate/kernels packages introduced.

## Immutable provenance / execution

Weights4,177,999,192 bytes, SHA256
`b69fcfb5cd97b91b52022642d88da91201487aa73750fa8b14a0e6591a5a9e2d`.
685 BF16 tensors (4,177,914,880 bytes); header inspected before execution.
Controlled optional-import patch SHA256
`e9374e89a0a0668af5cdd56ebf43a170fd1ff47798a9027cbdc6223754654c95`.
Every acquired asset has pinned URL, expected/actual size, purpose and SHA receipt.
`runtime_manifest.json` verified model/code/tokenizer assets plus installed code hashes.
The optional flash/apex/DropPath dependency paths are disabled in a separate retained
copy; standard eager inference math and weights unchanged. No floating remote execution.

Run ID: `INTERNVL3_INITIAL_GPU_PILOT`.
Raw root: `artifacts/internvl3-20260928/runs/INTERNVL3_INITIAL_GPU_PILOT`.
Exact prompts/complete rendered system+image template, token IDs, requested generation
config, timing and placement are in `events.jsonl`; parent copy `pipe_events.jsonl`.
All four responses below are copied from raw data without correction.
Started: `2026-09-28T02:48:53.402954+08:00`. Commit: `cb171216dac7f7fd99aa6b9a2776de4bd1311af4`.
Run-start dirty state (full source hashes in provenance.json):

```text
M AGENTS.md
 M README.md
 M src/local_vision_agent/pilot_supervisor_repair.py
?? docs/INTERNVL3_PILOT_AMENDMENT_2026-09-28.md
?? docs/INTERNVL3_STATIC_REVIEW_2026-09-28.md
?? scripts/internvl_acquire.py
?? scripts/internvl_prepare.py
?? src/local_vision_agent/internvl_policy.py
?? src/local_vision_agent/internvl_worker.py
?? tests/test_internvl_policy.py
```
Acquisition payload ledger: **4,190,306,324 bytes**, within5GB. Transport overhead is not packet-metered.

One persistent worker/load, original synthetic fixture only (development, not formal test),
SHA256 `7a902b90e90b2c89ff91cd78a23f5a8b9d42bb4ca15a24775736ee9afb1d463f`.
384x256 source -> one448x448 RGB normalized tile; no thumbnails/multiple crops.
The official single-tile path changes aspect ratio: limitation, no universal image-quality claim.
No additional real images used because no suitable rights-confirmed images were provided.

Frozen [amendment](INTERNVL3_PILOT_AMENDMENT_2026-09-28.md) retains exact A–D prompts,
planned probes, scheduling gate, estimate, image/token/deadline/stop policy.
Batch1, BF16, eager, cuda:0, no CPU/disk offload, no auto map, no second model.
Greedy do_sample=False, temperature0 (inactive/ignored by greedy path), num_beams1,
max_new_tokens128, use_cache=True, EOS151645/pad151643.
Transformers supplies BOS151643 from pinned model defaults (logged warning); requested
pre-generation config and this effective default are both retained. No sampling retries.

## English and Traditional Chinese raw results

### A_english — fixture content/language PASS
```text
The image contains two shapes: a red square on the left and a blue circle on the right.
```

### B_direct_zh — fixture content/language PASS
```text
圖片中有兩個形狀：一個紅色的正方形和一個藍色的圓形。
```

### C_caption_zh — fixture content/language PASS
```text
這張圖片顯示了一個紅色的正方形和一個藍色的圓形。
```

### D_instruction_zh — fixture content/language PASS
```text
這張圖片顯示了一個紅色的正方形和一個藍色的圓形。
```

No question echoes, translation, OpenCC or cloud inference. Chinese answers contain the
correct red-square/blue-circle pairs in useful Traditional Chinese. This establishes only
the tested fixture's language route; it does not establish general multilingual quality.

## Agent capability probes

Scene / objects / background detail / claim verification: **NOT RUN** due to scheduler
gate false-negative. Core query interface works, but separate probe usability remains
unverified. Same-model verification would not be independent truth even if executed.
No A–D Agent integration, formal dataset, training, benchmark or prompt search performed.

## GPU preflight and resource measurements

RTX3070Ti8192MiB, before used214/free7804MiB; existing VMware and a permission-limited
GPU process recorded in hardware-before.txt. Estimate6000MiB UNMEASURED before run;
ceiling6400, reserve1536, allocator cap5400. Actual preflight and post-init checks passed.
CUDA available; one CUDA device. Allocator baseline0/0; observed context allowance713MiB.
Measurements below are bytes converted to MiB, rounded to3 decimals; peak columns are
cumulative across load and calls, not individual-call peaks. Dedicated telemetry is
device-wide; CUDA and NVIDIA accounting differ on Windows and are not interchangeable.

| Checkpoint | allocated MiB | reserved MiB | peak allocated MiB | peak reserved MiB | CUDA free MiB | NVIDIA used/free MiB |
|---|---:|---:|---:|---:|---:|---:|
| cuda_baseline  | 0.000 | 0.000 | 0.000 | 0.000 | 7091.000 | 373 / 7645 |
| model_loaded  | 3985.220 | 4680.000 | 4429.578 | 4680.000 | 2385.000 | 5079 / 2939 |
| image_ready  | 3986.863 | 4680.000 | 4429.578 | 4680.000 | 2385.000 | 5079 / 2939 |
| visual_done A_english | 3995.743 | 4682.000 | 4429.578 | 4682.000 | 2367.000 | 5097 / 2921 |
| call_done A_english | 4004.985 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5105 / 2913 |
| visual_done B_direct_zh | 3995.744 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5105 / 2913 |
| call_done B_direct_zh | 4005.205 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5105 / 2913 |
| visual_done C_caption_zh | 3995.743 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5105 / 2913 |
| call_done C_caption_zh | 4004.958 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5105 / 2913 |
| visual_done D_instruction_zh | 3995.743 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5105 / 2913 |
| call_done D_instruction_zh | 4004.985 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5105 / 2913 |
| before_cleanup  | 8.125 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5105 / 2913 |
| cleanup_done  | 0.000 | 0.000 | 4429.578 | 4688.000 | 7047.000 | 417 / 7601 |

Peak allocated **4429.578 MiB**; peak reserved **4688.000 MiB**. Sampled device-wide peak **5105 MiB**; minimum dedicated free **2913 MiB**.

Sampled device usage is not a continuous per-process peak. Before/after Windows counters
are retained, but model PID/LUID attribution during inference and inter-sample spill are
not proven: **Windows shared GPU memory = UNKNOWN / OBSERVABILITY LIMITATION**.
Do not claim zero shared-memory spill. No shared-memory fallback was configured.

## Latency

GPU operations synchronized before/after. Cold load includes asset verification,
preflight, framework import, constructor and tensor loading; not weights-transfer-only.
Query totals include measurement overhead; visual+generation subtotals exclude some of it.
Every query recomputes visual features. Later calls are warm executions, not cached replay.

| Operation | total seconds | visual seconds | generation seconds | input tokens | output tokens |
|---|---:|---:|---:|---:|---:|
| model_loaded | 29.797 | — | — | — | — |
| image_ready | 0.031 | — | — | — | — |
| cleanup_done | 0.203 | — | — | — | — |
| A_english | 1.641 | 0.391 | 1.203 | 318 | 21 |
| B_direct_zh | 0.937 | 0.031 | 0.812 | 326 | 21 |
| C_caption_zh | 0.875 | 0.047 | 0.797 | 318 | 20 |
| D_instruction_zh | 0.859 | 0.031 | 0.781 | 319 | 20 |

Total output tokens: 82; calls4/8; images1/3; supervisor session35.672s.

## Placement / offline / cleanup

All enumerated parameters and buffers including vision/language/projector were cuda:0.
Pixels, input IDs/masks, projected visual embeddings and returned28-layer K/V tensors
were inspected on cuda:0. Full name/dtype/shape records retained. Standard CPU image
decoding/tokenization is preprocessing, not model offload. No opaque cache accepted.

**Offline PASS in tested path:** offline flags and Python socket audit active before
framework imports and throughout the only load+image+English+Chinese calls; zero logged
network attempts. No online recovery fetch. This is not OS-firewall/native-code proof.

**Cleanup PASS:** model/tensor frame released, gc, cuBLAS workspace clearing,
empty_cache/synchronize; allocated=reserved=0. Worker exit0, Job empty, no supervisor
error. Device after process exit used214/free7804MiB exactly matches observed baseline.
CUDA context accounts for nonzero device usage before process exit; not retained weights.

## Errors and warnings

No OOM, runtime exception, timeout, network violation or resource-budget failure.
Full stderr preserved. Three warning classes:

1. Transformers4.57.6 Mistral regex heuristic: static source inspection shows local
   config with null transformers_version reaches warning even for internvl_chat/Qwen2.
   Warning branch sets fix_mistral_regex=False and does not modify pre-tokenizer.
   Local/offline branch does not call remote model_info. Evidence/tokenizer_warning_review.json
   retains config values, original regex and source SHA. No Mistral fix applied, no rerun;
   this warning is not evidence of a Mistral dependency or demonstrated tokenization failure.
2. Temperature ignored because greedy generation is selected, as intended.
3. BOS default151643 filled from pinned model config, documented above.

Earlier CPU test invocation without PYTHONIOENCODING=utf-8 failed one existing CLI
subprocess decoding check under Windows cp950. Re-running with the documented UTF-8
environment passed75 tests (3.044s); no dependency/model change. Ruff and strict Mypy
passed21 modules. CPU tests are engineering tests, not model-quality measurements.

## Remaining work and next authorization

The sole engineering blocker is incomplete capability-probe coverage caused by the
over-restrictive scheduler. Preserve frozen gate and pilot; no edits to make its historical
PASS count improve. A separately dated prospective amendment should define a better
non-GPT acceptance mechanism, then obtain explicit authorization for ONE new bounded
load/session to complete scene/object/detail/verification probes under unchanged safety
limits. No new model download, dependency, precision or prompt search is necessary.
User confirmation is needed before any real adapter integration; formal A–D work remains
separately gated. No further GPU run is authorized by the consumed initial-run gate.

75 CPU tests/real4-query pilot do not prove arbitrary-image reliability, deadline delivery,
RQ2–RQ4 improvements, publication rights or institutional approval. No formal dataset,
repetitions or uncertainty estimate; no advisor/institution confirmation invented.
Moondream original/repair1/final negative evidence and weights remain intact.
Targets10/31 core and11/1 acceptance remain goals, not promises.

## Reproduction / evidence / AI assistance

Report regeneration only (CPU, no GPU/model):
`.venv/Scripts/python.exe scripts/internvl_report.py`.
Tables/raw responses derive directly from run events and samples; assert four expected
core calls and absence of worker errors. Judgment/limitations are explicit narrative.
Do not rerun the supervisor: its exclusive directory is a consumed execution gate.
Evidence backup excludes duplicate large weights but includes raw events, receipts,
source/config/tokenizer, protocols and source snapshot with hash inventory.

Astra assisted source/license review, bounded worker/scheduler, tests and this report.
No Astra/GPT runtime, online judge or translation service was used. Author must verify
source understanding, raw responses and research claims. See [handoff](../SESSION_HANDOFF.md).
