# Real InternVL Agent GPU Smoke Result — 2026-09-30

DEVELOPMENT ONLY / PILOT / NOT FORMAL THESIS RESULT

## Verdict

**REAL INTERNVL AGENT GPU SMOKE = PASS**

Engineering acceptance for one synthetic Method D run only. No quality/hallucination metric, A–D comparison or RQ2–RQ4 conclusion.

## Provenance

Run: `INTERNVL_REAL_AGENT_GPU_SMOKE_20260930`; Agent report UUID: `fb37ed6b-50bf-4603-be34-d960a5057260`. Exact source HEAD: `c2ce0b24a61c257db9cdc232f45dd4c95e30521f`. Initial audit was clean; execution dirty state below contains only the prospective amendment.

```text
?? docs/REAL_INTERNVL_AGENT_GPU_SMOKE_AMENDMENT_2026-09-30.md
```

Model/tokenizer/template revision: `f6c7b60375759170fd49f5e9e298e2178485c5ba`. Config SHA256 `e3bc387c91ed0e3fc816232f0563f9c83d8105401cff6cbe8be7e3eb1d97ab52`. Model/controlled/framework file hashes and exact installed versions in `evidence/resume_audit.json`; all verified before load. No asset/dependency changes.

Preprocessing: `internvl-single-tile-rgb-bicubic448-imagenet-v1`; 384x256 -> one448x448 RGB BICUBIC/ImageNet-normalized tile changes aspect ratio. Final thesis preprocessing remains unfrozen.

Source, config and frozen amendment hashes rechecked after execution. Full raw run preserved outside Git; no mock or translator used. Python-only report reconstruction: `.venv/Scripts/python.exe scripts/real_agent_smoke_report.py`.

## Hardware

```text
name, driver_version, memory.total [MiB], memory.used [MiB], memory.free [MiB]
NVIDIA GeForce RTX 3070 Ti, 591.86, 8192 MiB, 246 MiB, 7772 MiB
```

Existing torch2.7.1+cu126 (CUDA12.6 build); BF16/cuda:0/eager, one model, batch1. Planning estimate6000MiB, ceiling6400MiB, reserve1536MiB, allocator cap5400MiB. Model parameters/buffers (including vision/language), inputs, visual embeddings and 28-layer KV cache observed cuda:0. No offload/quantization/auto mapping.

Windows shared GPU memory = UNKNOWN / OBSERVABILITY LIMITATION. Placement checks do not prove zero OS spill.

## Method and state trace

D only; existing bounded-policy-v1 prompts/transitions unchanged; <=8calls/iterations,128output tokens/call,1024input tokens/call and1024total outputtokens;60s/call,300s/image,180s/load,10s/cleanup,1800s/session.

START -> INITIAL_CAPTION -> SCENE_ANALYSIS -> OBJECT_CHECK -> DETAIL_QUERY -> VERIFICATION -> REPORT -> STOP

Actual calls: 6; total outputtokens: 65; stop `COMPLETED`, investigation `NO_TRIGGER`.

## Calls

| Call | State / prompt ID | Input / output tokens | Latency s | Raw answer |
|---|---|---:|---:|---|
| call-1 | INITIAL_CAPTION / caption | 328 / 37 | 2.719 | 這張圖片顯示了兩個簡單的圖形：一個紅色的正方形和一個藍色的圓形。背景是白色的。沒有其他細節或文字。 |
| call-2 | SCENE_ANALYSIS / scene | 322 / 20 | 0.922 | 這張圖片顯示了一個紅色的正方形和一個藍色的圓形。 |
| call-3 | VERIFICATION / verify | 350 / 2 | 0.187 | supported |
| call-4 | VERIFICATION / verify | 329 / 2 | 0.188 | supported |
| call-5 | VERIFICATION / verify | 332 / 2 | 0.172 | supported |
| call-6 | VERIFICATION / verify | 344 / 2 | 0.187 | supported |

## Adaptive behavior

Caption and scene normalized uncertain=false, missing=[]. OBJECT_CHECK and DETAIL_QUERY were decision visits, not model calls. Both additional queries skipped; NO_TRIGGER selected. NO_NEW_EVIDENCE and uncertain/detail branches were NOT exercised on this image (CPU fixtures cover them). No calls forced.

Four literal candidate clauses retained. Caption and scene paraphrases remain separate because duplicate matching is exact-string only; no semantic deduplication claim.

## Verification and traceability

| Claim (literal) | Observation | Verification | Runtime status |
|---|---|---|---|
| 這張圖片顯示了兩個簡單的圖形：一個紅色的正方形和一個藍色的圓形 | call-1 | call-3 | supported |
| 背景是白色的 | call-1 | call-4 | supported |
| 沒有其他細節或文字 | call-1 | call-5 | supported |
| 這張圖片顯示了一個紅色的正方形和一個藍色的圓形 | call-2 | call-6 | supported |

Each observation_id equals call_id and resolves to the raw events.jsonl call; normalized trace/raw answer/request/token counts/evidence links checked for equality. Each verification request matches its candidate exactly. All four explicit responses parsed supported; this is SAME-MODEL support, not independent correctness evidence. No GPT semantic judge or new human-quality approval inferred.

## VRAM checkpoints

All quantities MiB; allocated/reserved are worker allocator values, NVIDIA is whole-device. Peaks cumulative; not estimates.

| Checkpoint | Allocated | Reserved | Peak allocated | Peak reserved | CUDA free | NVIDIA used/free |
|---|---:|---:|---:|---:|---:|---|
| Before CUDA/load | N/A | N/A | N/A | N/A | N/A | 246/7772 |
| cuda_baseline  | 0.000 | 0.000 | 0.000 | 0.000 | 7091.000 | 405/7613 |
| model_loaded  | 3985.220 | 4680.000 | 4429.578 | 4680.000 | 2385.000 | 5111/2907 |
| image_ready  | 3986.863 | 4680.000 | 4429.578 | 4680.000 | 2385.000 | 5111/2907 |
| visual_done  | 3995.744 | 4682.000 | 4429.578 | 4682.000 | 2367.000 | 5129/2889 |
| call_done call-1 | 4005.697 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5137/2881 |
| visual_done  | 3995.744 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5137/2881 |
| call_done call-2 | 4005.068 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5137/2881 |
| visual_done  | 3995.744 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5137/2881 |
| call_done call-3 | 4005.342 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5137/2881 |
| visual_done  | 3995.744 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5137/2881 |
| call_done call-4 | 4004.768 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5137/2881 |
| visual_done  | 3995.744 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5137/2881 |
| call_done call-5 | 4004.850 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5137/2881 |
| visual_done  | 3995.744 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5137/2881 |
| call_done call-6 | 4005.178 | 4688.000 | 4429.578 | 4688.000 | 2359.000 | 5137/2881 |
| cleanup_done  | 0.000 | 0.000 | 4429.578 | 4688.000 | 7047.000 | 449/7569 |

Before cleanup: cleanup_start at monotonic 258182.109; nearest device sample offset -0.016s: 5137/2881MiB. No fresh allocator snapshot at cleanup_start; preceding call-6 snapshot shown above, not relabeled as contemporaneous.

Process exit: NVIDIA 246/7772MiB. Peak allocated 4429.578MiB; peak reserved 4688.000MiB; observed device peak 5137MiB (sampling may miss transients).

## Latency

| Component | Seconds |
|---|---:|
| Cold backend load including hash checks/imports | 37.703 |
| Image validation/preprocessing/transfer | 0.031 |
| Sum synchronized model calls | 4.375 |
| Agent image controller + RPC | 4.734 |
| JSON/Markdown report serialization | 0.265 |
| Worker cleanup | 0.219 |
| Parent cleanup through recovery | 1.219 |
| Full invocation through report writes | 44.531 |

Parent profiling overhead included; some substeps below clock resolution record0, not zero-cost claims. Full invocation includes cold load, Agent, measurement, cleanup and report generation; this is one development measurement, not a benchmark distribution.

## Offline / cleanup / errors

Offline PASS within HF offline flags and Python network audit scope; no network-violation event. Native/OS firewall guarantee not asserted. Cleanup PASS: allocated0/reserved0, worker PID12696 exit0, Job empty, device recovered to exact observed baseline. No OOM, timeout, malformed RPC, fallback or runtime error.

Warnings preserved: pinned local tokenizer emits existing Mistral-regex heuristic warning; greedy generation ignores temperature; default BOS151643 supplied. No tokenizer patch, generation change or online repair made. Full stderr retained.

## Traditional Chinese report (verbatim generated artifact)

```markdown
# 影像理解報告（本地模型開發驗證，非正式論文結果）



執行 ID：fb37ed6b-50bf-4603-be34-d960a5057260

輸入 ID：<pre>original-synthetic-shapes-development</pre>

比較組別：D；狀態：complete

停止原因：COMPLETED；調查停止：NO_TRIGGER



## 簡述、場景與細節

INITIAL_CAPTION [call-1]

<pre>這張圖片顯示了兩個簡單的圖形：一個紅色的正方形和一個藍色的圓形。背景是白色的。沒有其他細節或文字。</pre>

SCENE_ANALYSIS [call-2]

<pre>這張圖片顯示了一個紅色的正方形和一個藍色的圓形。</pre>



## 敘述與驗證紀錄

<pre>這張圖片顯示了兩個簡單的圖形：一個紅色的正方形和一個藍色的圓形</pre>

狀態：同模型觀察支持；來源：call-1；驗證：call-3

<pre>背景是白色的</pre>

狀態：同模型觀察支持；來源：call-1；驗證：call-4

<pre>沒有其他細節或文字</pre>

狀態：同模型觀察支持；來源：call-1；驗證：call-5

<pre>這張圖片顯示了一個紅色的正方形和一個藍色的圓形</pre>

狀態：同模型觀察支持；來源：call-2；驗證：call-6



## 未確定、衝突與限制

以下為模型觀察；候選敘述不等於客觀真值，未明確驗證者維持未確定。

同模型驗證不是獨立真值；未驗證敘述及反駁內容不得視為事實。



## 資源摘要

工具嘗試次數：6

模型查詢總延遲（秒）：4.375；峰值保留顯存（MiB）：4688.0；缺失值表示未量測。
```

## Limits and next stage

No real-image sanity performed: no rights-confirmed images supplied. Engineering baseline READY is NOT yet declared. Prepare <=2 non-sensitive rights-confirmed development images and freeze a separate bounded sanity session before execution. All development images stay out of untouched formal test data. Stop feature expansion; formal design freeze comes after engineering acceptance.

## CPU quality checks

Pre-run93 tests PASS(12.038s); post-run93 tests PASS(10.513s). Ruff src/tests/scripts PASS and strict Mypy28 source files PASS before and after smoke. Evidence/source/config/amendment and raw-run reconstruction consistency PASS. CPU process fixtures are not GPU evidence; this new smoke is a real GPU run.

## AI assistance / review

Development assistant audited source/evidence and generated this trace-based engineering report; no runtime cloud/LLM judge, translation, raw-output editing or research-effect claim. Author should review code and exact observations. No new institutional/advisor approval asserted.
