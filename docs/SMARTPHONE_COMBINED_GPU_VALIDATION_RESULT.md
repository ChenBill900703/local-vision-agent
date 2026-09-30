# Final closeout — 2026-10-01

**COMBINED GPU VALIDATION = PASS — ENGINEERING / DEVELOPMENT ONLY**

The author has now supplied DEVELOPMENT HUMAN SANITY REVIEW, satisfying the prospective
engineering-usability condition. All14 raw/input inventory SHA256 entries, runtime source
hashes, original/normalized provenance,8-call trace/6checks/2budget-unresolved/75%coverage,
cleanup and retained pre/post110CPU/Ruff/strictMypy29 logs were re-audited without GPU use.
[Baseline decision](ENGINEERING_BASELINE_DECISION.md). This is NOT semantic accuracy PASS.

## DEVELOPMENT HUMAN SANITY REVIEW

> DEVELOPMENT HUMAN SANITY REVIEW：整體可用，主要場景與主要物件大致能辨識，但保留明顯語意錯誤與 hallucination。原圖中的裝飾主要為松果，不宜描述為金色球形飾物；聖誕樹底座的顏色／材質／四腳描述不準確；Caption 提到的「帶有透明蓋子的灰色杯子」在原圖中未見，視為明顯 nonexistent-object hallucination。背景主要為窗戶／遮光簾，描述為淺灰色背景牆亦不精確。Caption 與 Scene 均因 128-token limit 截斷。同模型 verification 對部分不準確 claim 仍回答 supported，顯示 over-acceptance/self-confirmation limitation。基於本階段僅驗證 engineering usability，我評為 development-usable；這不代表 accuracy、hallucination reduction 或 verification correctness PASS，也不作正式論文結果。

Exact author statement retained in `artifacts/formal-design-20261001/evidence/human_review.json`;
read-only audit in `closeout_audit.json`. No numeric thesis score derived. No rerun, raw
output edit or incorrect-claim relabeling. Previous technical audit and raw report retain
their historical pending-review state; this dated addendum supplies the final decision.
Feature expansion frozen; next is [formal-design author review](FORMAL_EXPERIMENT_DESIGN.md).

---

The following is the unmodified 2026-09-30 technical report, including its then-pending
review language and original model outputs. Those historical status lines do not override
this dated closeout.

# Smartphone Combined GPU Validation Result — 2026-09-30

DEVELOPMENT ONLY / NOT FORMAL THESIS RESULT. Private local evidence; no publication.

**COMBINED GPU VALIDATION = TECHNICAL PASS / HUMAN REVIEW PENDING**

## Provenance

Run SMARTPHONE_COMBINED_OUTDOOR_20260930_V1; exact execution HEAD 54137bf9f0aa4bc39915bd69b3556b89ea5a9adf; frozen source bdf9dd2cb3b5657cf2e33a0efa5829b5b614c694; execution dirty state ''. Runtime/config unchanged before/after. Config SHA256 05b5d92a28659630cd5a5e2f9593ffd06241ab2c4f7a5379c82f7e43f41f20d1. Full source/model/controlled/dependency hashes retained in evidence/preflight_audit.json.

## Original and automatic normalized input

```json
{
  "policy": "smartphone-source-v1",
  "source_path": "E:\\AI Agent影像辨識專案\\development_images\\outdoor_scene_001.jpg",
  "source_sha256": "adaf0193b5a16a49526347ea2cd0561d4cd6580fd038290dbacf4e4dbf76e736",
  "source_bytes": 3437516,
  "source_width": 3472,
  "source_height": 4624,
  "source_format": "JPEG",
  "oriented_width": 3472,
  "oriented_height": 4624,
  "source_image_limits": {
    "max_compressed_bytes": 33554432,
    "max_decoded_pixels": 32000000,
    "max_source_edge_px": 10000,
    "formats": [
      "JPEG",
      "PNG"
    ]
  },
  "normalized": true,
  "model_input_path": "E:\\AI Agent影像辨識專案\\artifacts\\smartphone-source-repair-20260930\\runs\\SMARTPHONE_COMBINED_OUTDOOR_20260930_V1-input\\normalized.png",
  "model_input": {
    "sha256": "5e86f70d2afbf7725266eb569698a0f371757b3eadd521fdde1ce1d2831f1b77",
    "width": 384,
    "height": 512,
    "format": "PNG"
  },
  "conversion": "EXIF transpose/RGB/LANCZOS aspect-preserving <=512/metadata-free PNG"
}
```

Original JPEG passed directly to run_development. Code created new private normalized.png before model load, then existing448x448single-tileRGBBICUBIC/ImageNet path. Identical normalized hash to prior approved derivative is a deterministic-output match, not use of that prior derivative as input. Source bytes unchanged. Rights/non-sensitive suitability user-attested; no cloud image viewing or identity inference. Fine detail may be lost; aspect ratio changes at modeltile.

## Method/state/verification

START -> INITIAL_CAPTION -> SCENE_ANALYSIS -> OBJECT_CHECK -> DETAIL_QUERY -> VERIFICATION -> REPORT -> STOP

Investigation NO_TRIGGER; no object/detail query triggered.8literal claims; FIFO6slots,6attempted/completed,2budget-unresolved;75%coverage. No9thcall. Normal completion COMPLETED_WITH_PARTIAL_VERIFICATION / VERIFICATION_BUDGET_EXHAUSTED. Coverage is not accuracy. Same-model supported is not independent ground truth.

## All raw answers and verification requests

### call-1 / INITIAL_CAPTION

Exact prompt:
```text
以繁體中文描述圖片的場景、重要物件與可見細節；不確定時明示。
```

Raw answer:
```text
這張圖片展示了一個室內場景，主要特點包括：

1. **一棵小型的綠色聖誕樹**：聖誕樹上裝飾有幾顆金色的球形飾物，頂部有一顆白色的星星。聖誕樹放置在一個淺色的木質或塑料底座上，底座有四個腳。

2. **一個灰色的花盆**：花盆放置在聖誕樹的右側，花盆裡似乎有土壤，但沒有明顯的植物。

3. **一個帶有透明蓋子的灰色杯子**：杯子放在花盆
```

input=328, output=128, latency=5.875s, stop=token_limit, truncated=True.

### call-2 / SCENE_ANALYSIS

Exact prompt:
```text
以繁體中文描述可見場景，不推測不可見的背景。
```

Raw answer:
```text
這張圖片展示了一個室內的角落，有一個小型的綠色樹形裝飾物，上面裝飾有金色的球形裝飾品和一個白色的星星頂飾。樹形裝飾物旁邊有一個灰色的花盆，花盆裡似乎有土壤，花盆放在一個銀色的碟子上。整個裝飾物擺放在一個淺色的檯面上，檯面下方是白色的櫃子，櫃子上有兩個門，門上有兩個圓形的把手。檯面的背景牆是淺灰色的，牆上有一條明亮的光
```

input=322, output=128, latency=5.359s, stop=token_limit, truncated=True.

### call-3 / VERIFICATION

Exact prompt:
```text
檢查候選敘述，回報 supported、contradicted 或 unresolved；非獨立真值：這張圖片展示了一個室內場景，主要特點包括：
```

Raw answer:
```text
supported
```

input=342, output=2, latency=0.187s, stop=eos, truncated=False.

### call-4 / VERIFICATION

Exact prompt:
```text
檢查候選敘述，回報 supported、contradicted 或 unresolved；非獨立真值：1. **一棵小型的綠色聖誕樹**：聖誕樹上裝飾有幾顆金色的球形飾物，頂部有一顆白色的星星
```

Raw answer:
```text
supported
```

input=361, output=2, latency=0.203s, stop=eos, truncated=False.

### call-5 / VERIFICATION

Exact prompt:
```text
檢查候選敘述，回報 supported、contradicted 或 unresolved；非獨立真值：聖誕樹放置在一個淺色的木質或塑料底座上，底座有四個腳
```

Raw answer:
```text
supported
```

input=349, output=2, latency=0.219s, stop=eos, truncated=False.

### call-6 / VERIFICATION

Exact prompt:
```text
檢查候選敘述，回報 supported、contradicted 或 unresolved；非獨立真值：2. **一個灰色的花盆**：花盆放置在聖誕樹的右側，花盆裡似乎有土壤，但沒有明顯的植物
```

Raw answer:
```text
supported
```

input=359, output=2, latency=0.172s, stop=eos, truncated=False.

### call-7 / VERIFICATION

Exact prompt:
```text
檢查候選敘述，回報 supported、contradicted 或 unresolved；非獨立真值：這張圖片展示了一個室內的角落，有一個小型的綠色樹形裝飾物，上面裝飾有金色的球形裝飾品和一個白色的星星頂飾
```

Raw answer:
```text
supported
```

input=366, output=2, latency=0.187s, stop=eos, truncated=False.

### call-8 / VERIFICATION

Exact prompt:
```text
檢查候選敘述，回報 supported、contradicted 或 unresolved；非獨立真值：樹形裝飾物旁邊有一個灰色的花盆，花盆裡似乎有土壤，花盆放在一個銀色的碟子上
```

Raw answer:
```text
supported
```

input=357, output=2, latency=0.172s, stop=eos, truncated=False.

## Candidate claims and evidence links

```json
[
  {
    "text": "這張圖片展示了一個室內場景，主要特點包括：",
    "observation_ids": [
      "call-1"
    ],
    "status": "supported",
    "verification_id": "call-3",
    "verification_reason": null
  },
  {
    "text": "1. **一棵小型的綠色聖誕樹**：聖誕樹上裝飾有幾顆金色的球形飾物，頂部有一顆白色的星星",
    "observation_ids": [
      "call-1"
    ],
    "status": "supported",
    "verification_id": "call-4",
    "verification_reason": null
  },
  {
    "text": "聖誕樹放置在一個淺色的木質或塑料底座上，底座有四個腳",
    "observation_ids": [
      "call-1"
    ],
    "status": "supported",
    "verification_id": "call-5",
    "verification_reason": null
  },
  {
    "text": "2. **一個灰色的花盆**：花盆放置在聖誕樹的右側，花盆裡似乎有土壤，但沒有明顯的植物",
    "observation_ids": [
      "call-1"
    ],
    "status": "supported",
    "verification_id": "call-6",
    "verification_reason": null
  },
  {
    "text": "這張圖片展示了一個室內的角落，有一個小型的綠色樹形裝飾物，上面裝飾有金色的球形裝飾品和一個白色的星星頂飾",
    "observation_ids": [
      "call-2"
    ],
    "status": "supported",
    "verification_id": "call-7",
    "verification_reason": null
  },
  {
    "text": "樹形裝飾物旁邊有一個灰色的花盆，花盆裡似乎有土壤，花盆放在一個銀色的碟子上",
    "observation_ids": [
      "call-2"
    ],
    "status": "supported",
    "verification_id": "call-8",
    "verification_reason": null
  },
  {
    "text": "整個裝飾物擺放在一個淺色的檯面上，檯面下方是白色的櫃子，櫃子上有兩個門，門上有兩個圓形的把手",
    "observation_ids": [
      "call-2"
    ],
    "status": "unresolved",
    "verification_id": null,
    "verification_reason": "verification_budget_not_available"
  },
  {
    "text": "檯面的背景牆是淺灰色的，牆上有一條明亮的光",
    "observation_ids": [
      "call-2"
    ],
    "status": "unresolved",
    "verification_id": null,
    "verification_reason": "verification_budget_not_available"
  }
]
```

Raw/normalized/request/claim/verification IDs/token counts/coverage checked for equality and FIFO order. Unselected claims unresolved/null IDs with explicit budget reason. All8validresponses retained.

## Resource snapshots

```json
{
  "status": "COMBINED GPU VALIDATION = TECHNICAL PASS / HUMAN REVIEW PENDING",
  "calls": 8,
  "tokens": 268,
  "coverage": 0.75,
  "allocated_peak_mib": 4429.57763671875,
  "reserved_peak_mib": 4688.0,
  "sampled_device_peak_mib": 5137,
  "human_review": "PENDING",
  "baseline_ready": false
}
```

| Checkpoint | Allocated MiB | Reserved MiB | CUDA free MiB | Device used/free MiB |
|---|---:|---:|---:|---|
| cuda_baseline  | 0.000 | 0.000 | 7091.000 | 405/7613 |
| model_loaded  | 3985.220 | 4680.000 | 2385.000 | 5111/2907 |
| image_ready  | 3986.863 | 4680.000 | 2385.000 | 5111/2907 |
| visual_done  | 3995.744 | 4682.000 | 2367.000 | 5129/2889 |
| call_done call-1 | 4008.186 | 4688.000 | 2359.000 | 5137/2881 |
| visual_done  | 3995.744 | 4688.000 | 2359.000 | 5137/2881 |
| call_done call-2 | 4008.022 | 4688.000 | 2359.000 | 5137/2881 |
| visual_done  | 3995.744 | 4688.000 | 2359.000 | 5137/2881 |
| call_done call-3 | 4005.123 | 4688.000 | 2359.000 | 5137/2881 |
| visual_done  | 3995.744 | 4688.000 | 2359.000 | 5137/2881 |
| call_done call-4 | 4005.643 | 4688.000 | 2359.000 | 5137/2881 |
| visual_done  | 3995.744 | 4688.000 | 2359.000 | 5137/2881 |
| call_done call-5 | 4005.314 | 4688.000 | 2359.000 | 5137/2881 |
| visual_done  | 3995.744 | 4688.000 | 2359.000 | 5137/2881 |
| call_done call-6 | 4005.588 | 4688.000 | 2359.000 | 5137/2881 |
| visual_done  | 3995.744 | 4688.000 | 2359.000 | 5137/2881 |
| call_done call-7 | 4005.779 | 4688.000 | 2359.000 | 5137/2881 |
| visual_done  | 3995.744 | 4688.000 | 2359.000 | 5137/2881 |
| call_done call-8 | 4005.533 | 4688.000 | 2359.000 | 5137/2881 |
| cleanup_done  | 0.000 | 0.000 | 7047.000 | 449/7569 |

## Latency

Backend load31.469s; model preprocessing0.032s; calls12.374s; runtime through cleanup before reportwriting45.906s; total invocation through reportwriting45.922s; parentcleanup0.953s. CPU original normalization included in total, not separately instrumented; no invented substep timing.

## Offline / placement / cleanup

PASS within existing HFoffline/Pythonnetworkdenial; no violation events or downloads. Modelparameters/buffers,vision/language,input/visual/KV cuda:0. All observed budgetchecks pass; no OOM/timeout/malformedRPC/fallback. Windows sharedGPU memory UNKNOWN; no OSfirewall/zero-spill claim.

```json
{
  "measurement": {
    "nvidia": {
      "name": "NVIDIA GeForce RTX 3070 Ti",
      "total_mib": 8192,
      "used_mib": 449,
      "free_mib": 7569,
      "gpu_index": 0
    },
    "cuda_free_bytes": 7389315072,
    "cuda_total_bytes": 8589410304,
    "allocated_bytes": 0,
    "reserved_bytes": 0,
    "peak_allocated_bytes": 4644748800,
    "peak_reserved_bytes": 4915724288
  },
  "latency_s": 0.1720000000204891,
  "device_after": {
    "name": "NVIDIA GeForce RTX 3070 Ti",
    "total_mib": 8192,
    "used_mib": 246,
    "free_mib": 7772,
    "gpu_index": 0
  },
  "job_empty": true,
  "worker_exited": true,
  "parent_cleanup_seconds": 0.9529999999795109,
  "baseline_equivalent": true
}
```

Worker PID21220 exit0,Jobempty,devicebaseline-equivalent. Allocated/reserved0. One load/session only. No retry.

## Chinese structured report

```markdown
# 影像理解報告（本地模型開發驗證，非正式論文結果）



執行 ID：3010ae26-0f10-4894-aaa5-1e69e2c691fb

輸入 ID：<pre>outdoor_scene_001</pre>

比較組別：D；狀態：complete

停止原因：VERIFICATION_BUDGET_EXHAUSTED；調查停止：NO_TRIGGER



## 調查

調查停止：NO_TRIGGER

## 驗證覆蓋（非正確率）

完成類型：COMPLETED_WITH_PARTIAL_VERIFICATION；驗證停止：VERIFICATION_BUDGET_EXHAUSTED

候選：8；驗證額度：6；嘗試：6；完成：6；額度不足未驗證：2

覆蓋率：75%

## 簡述、場景與細節

## 原始影像與CPU正規化

<pre>{&quot;policy&quot;: &quot;smartphone-source-v1&quot;, &quot;source_path&quot;: &quot;E:\\AI Agent影像辨識專案\\development_images\\outdoor_scene_001.jpg&quot;, &quot;source_sha256&quot;: &quot;adaf0193b5a16a49526347ea2cd0561d4cd6580fd038290dbacf4e4dbf76e736&quot;, &quot;source_bytes&quot;: 3437516, &quot;source_width&quot;: 3472, &quot;source_height&quot;: 4624, &quot;source_format&quot;: &quot;JPEG&quot;, &quot;oriented_width&quot;: 3472, &quot;oriented_height&quot;: 4624, &quot;source_image_limits&quot;: {&quot;max_compressed_bytes&quot;: 33554432, &quot;max_decoded_pixels&quot;: 32000000, &quot;max_source_edge_px&quot;: 10000, &quot;formats&quot;: [&quot;JPEG&quot;, &quot;PNG&quot;]}, &quot;normalized&quot;: true, &quot;model_input_path&quot;: &quot;E:\\AI Agent影像辨識專案\\artifacts\\smartphone-source-repair-20260930\\runs\\SMARTPHONE_COMBINED_OUTDOOR_20260930_V1-input\\normalized.png&quot;, &quot;model_input&quot;: {&quot;sha256&quot;: &quot;5e86f70d2afbf7725266eb569698a0f371757b3eadd521fdde1ce1d2831f1b77&quot;, &quot;width&quot;: 384, &quot;height&quot;: 512, &quot;format&quot;: &quot;PNG&quot;}, &quot;conversion&quot;: &quot;EXIF transpose/RGB/LANCZOS aspect-preserving &lt;=512/metadata-free PNG&quot;}</pre>

接受高解析原圖不表示保留細節；CPU縮小後微小文字、遠處物件可能消失，模型仍只接收一張448×448 tile。

INITIAL_CAPTION [call-1]

<pre>這張圖片展示了一個室內場景，主要特點包括：

1. **一棵小型的綠色聖誕樹**：聖誕樹上裝飾有幾顆金色的球形飾物，頂部有一顆白色的星星。聖誕樹放置在一個淺色的木質或塑料底座上，底座有四個腳。

2. **一個灰色的花盆**：花盆放置在聖誕樹的右側，花盆裡似乎有土壤，但沒有明顯的植物。

3. **一個帶有透明蓋子的灰色杯子**：杯子放在花盆</pre>

輸出 tokens：128；生成停止：token_limit；truncated=true

SCENE_ANALYSIS [call-2]

<pre>這張圖片展示了一個室內的角落，有一個小型的綠色樹形裝飾物，上面裝飾有金色的球形裝飾品和一個白色的星星頂飾。樹形裝飾物旁邊有一個灰色的花盆，花盆裡似乎有土壤，花盆放在一個銀色的碟子上。整個裝飾物擺放在一個淺色的檯面上，檯面下方是白色的櫃子，櫃子上有兩個門，門上有兩個圓形的把手。檯面的背景牆是淺灰色的，牆上有一條明亮的光</pre>

輸出 tokens：128；生成停止：token_limit；truncated=true



## 敘述與驗證紀錄

<pre>這張圖片展示了一個室內場景，主要特點包括：</pre>

狀態：同模型觀察支持；來源：call-1；驗證：call-3；原因：無

<pre>1. **一棵小型的綠色聖誕樹**：聖誕樹上裝飾有幾顆金色的球形飾物，頂部有一顆白色的星星</pre>

狀態：同模型觀察支持；來源：call-1；驗證：call-4；原因：無

<pre>聖誕樹放置在一個淺色的木質或塑料底座上，底座有四個腳</pre>

狀態：同模型觀察支持；來源：call-1；驗證：call-5；原因：無

<pre>2. **一個灰色的花盆**：花盆放置在聖誕樹的右側，花盆裡似乎有土壤，但沒有明顯的植物</pre>

狀態：同模型觀察支持；來源：call-1；驗證：call-6；原因：無

<pre>這張圖片展示了一個室內的角落，有一個小型的綠色樹形裝飾物，上面裝飾有金色的球形裝飾品和一個白色的星星頂飾</pre>

狀態：同模型觀察支持；來源：call-2；驗證：call-7；原因：無

<pre>樹形裝飾物旁邊有一個灰色的花盆，花盆裡似乎有土壤，花盆放在一個銀色的碟子上</pre>

狀態：同模型觀察支持；來源：call-2；驗證：call-8；原因：無

<pre>整個裝飾物擺放在一個淺色的檯面上，檯面下方是白色的櫃子，櫃子上有兩個門，門上有兩個圓形的把手</pre>

狀態：未確定；來源：call-2；驗證：未執行；原因：verification_budget_not_available

<pre>檯面的背景牆是淺灰色的，牆上有一條明亮的光</pre>

狀態：未確定；來源：call-2；驗證：未執行；原因：verification_budget_not_available



## 未確定、衝突與限制

以下為模型觀察；候選敘述不等於客觀真值，未明確驗證者維持未確定。

同模型驗證不是獨立真值；未驗證敘述及反駁內容不得視為事實。



## 資源摘要

工具嘗試次數：8

模型查詢總延遲（秒）：12.373999999894295；峰值保留顯存（MiB）：4688.0；缺失值表示未量測。
```

## Human review and limitations

PENDING: all raw visual answers and6verification answers presented to user. Filename outdoor_scene_001 is an identifier, not ground truth for scene content; model says indoor, user must judge against actual photo. Both visual answers hit128tokenlimit/truncated=true. Literal parser includes an introductory fragment; uncertainty wording似乎 not flagged by existing parser. Preserve these development limitations; no tuning/semantic judging/claim-rewriting. No automatic baselineREADY or formal A-D/RQ claim.

## Tests / next action

Pre-run110CPUtests PASS(11.697s), RuffPASS, strictMypy29PASS. Post-run110CPUtests PASS; RuffPASS; strictMypy29PASS. Exact duration/logs in evidence/post-*.txt. Stop for DEVELOPMENT HUMAN SANITY REVIEW; no more GPU or feature work.
