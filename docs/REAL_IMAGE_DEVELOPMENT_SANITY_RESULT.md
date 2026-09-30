# Real Image Development Sanity Result — 2026-09-30

DEVELOPMENT ONLY / NOT FORMAL THESIS RESULT. PRIVATE LOCAL DEVELOPMENT RECORD; no publication or formal metrics.

## Verdict

**REAL IMAGE DEVELOPMENT SANITY = CONDITIONAL**

One indoor run produced a valid partial report but exhausted the unchanged8-call budget before verifying all8 candidates. Outdoor NOT RUN. Safety/runtime transport succeeded; full phase acceptance is not established. Human semantic review received: overall usable with truncation/incomplete-verification limitations. No baseline READY decision created.

## Provenance

HEAD `447fe603bdeceb6ec606b559ab6039ba096d801d`; branch main. Initial dirty state only untracked development_images/. Execution dirty state retained verbatim in provenance.json; current changes are ignore/docs only. Previous smoke and all runtime hashes unchanged. Frozen amendment and evidence under artifacts/real-image-development-sanity-20260930/evidence.

## Images and rights basis

User explicitly confirms self-photographed/authorized, local development-only, no public release/Git/cloud/identity recognition; separately approves aspect-preserving512 derivatives and non-sensitive contents. Assistant did not view/upload the photographs; privacy suitability is user-attested. Original photos unchanged.

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

Both originals16,054,528pixels failed input gate before GPU. Local approved RGB/LANCZOS512 metadata-free PNG derivatives passed. No random internet substitution.

## Runtime/config

InternVL3-2B-Instruct f6c7b60375759170fd49f5e9e298e2178485c5ba; BF16/cuda:0/eager/batch1, one worker, unchanged D prompts/controller/parser/config/dependencies. <=8calls/iterations,128output/call,1024input/call and totaloutput/image,60s/call,300s/image,180s/load,10s/cleanup. Planning6000MiB/ceiling6400/reserve1536/cap5400. No offload or fallback.

internvl-single-tile-rgb-bicubic448-imagenet-v1: approved512 input -> one448x448 tile with aspect-ratio change. Known DEVELOPMENT limitation; no dynamic tiling/final thesis freeze.

## Per-image state trace

REAL_IMAGE_SANITY_20260930_INDOOR_DESK_001: START -> INITIAL_CAPTION -> SCENE_ANALYSIS -> OBJECT_CHECK -> DETAIL_QUERY -> VERIFICATION -> REPORT -> STOP

Indoor status partial; stop TOOL_CALL_LIMIT; investigation NO_TRIGGER. Outdoor reserved ID REAL_IMAGE_SANITY_20260930_OUTDOOR_SCENE_001 NOT RUN; no outdoor worker or GPU load.

## Raw responses

### call-1 / INITIAL_CAPTION / caption

Input tokens328; output tokens128; latency5.656s; model stoptoken_limit.

Exact request:
```text
以繁體中文描述圖片的場景、重要物件與可見細節；不確定時明示。
```

Raw answer (unaltered):
```text
這張圖片展示了一個室內空間，地面鋪有白色方形地磚。在圖片中央，有一個圓形的座椅，座椅的靠背和坐墊部分是黃色的，而座椅的底座部分是灰色的。座椅的設計非常現代，弧形的靠背和坐墊看起來非常舒適。

在座椅的右側，有一個黑色的背包，背包靠在座椅上。在背景中，可以看到一些白色的櫃子和儲物櫃，櫃子上方有幾扇窗戶，窗戶上掛著白色的百葉窗。窗戶旁
```

### call-2 / SCENE_ANALYSIS / scene

Input tokens322; output tokens111; latency4.469s; model stopeos.

Exact request:
```text
以繁體中文描述可見場景，不推測不可見的背景。
```

Raw answer (unaltered):
```text
這張圖片展示了一個室內場景，其中有一個圓形的黃色和灰色相間的座椅。座椅的設計非常現代，由幾塊不同顏色的布料拼接而成。地板是白色方形地砖，牆壁是白色的，上面有幾扇窗戶，窗戶上掛著百葉窗。在座椅旁邊，有一個黑色的背包，以及一些其他物品，如掃帚和紙箱。整個場景看起來像是在一個辦公室或公共區域。
```

### call-3 / VERIFICATION / verify

Input tokens344; output tokens2; latency0.172s; model stopeos.

Exact request:
```text
檢查候選敘述，回報 supported、contradicted 或 unresolved；非獨立真值：這張圖片展示了一個室內空間，地面鋪有白色方形地磚
```

Raw answer (unaltered):
```text
supported
```

### call-4 / VERIFICATION / verify

Input tokens360; output tokens2; latency0.172s; model stopeos.

Exact request:
```text
檢查候選敘述，回報 supported、contradicted 或 unresolved；非獨立真值：在圖片中央，有一個圓形的座椅，座椅的靠背和坐墊部分是黃色的，而座椅的底座部分是灰色的
```

Raw answer (unaltered):
```text
supported
```

### call-5 / VERIFICATION / verify

Input tokens345; output tokens2; latency0.172s; model stopeos.

Exact request:
```text
檢查候選敘述，回報 supported、contradicted 或 unresolved；非獨立真值：座椅的設計非常現代，弧形的靠背和坐墊看起來非常舒適
```

Raw answer (unaltered):
```text
supported
```

### call-6 / VERIFICATION / verify

Input tokens343; output tokens2; latency0.156s; model stopeos.

Exact request:
```text
檢查候選敘述，回報 supported、contradicted 或 unresolved；非獨立真值：在座椅的右側，有一個黑色的背包，背包靠在座椅上
```

Raw answer (unaltered):
```text
supported
```

### call-7 / VERIFICATION / verify

Input tokens351; output tokens2; latency0.156s; model stopeos.

Exact request:
```text
檢查候選敘述，回報 supported、contradicted 或 unresolved；非獨立真值：這張圖片展示了一個室內場景，其中有一個圓形的黃色和灰色相間的座椅
```

Raw answer (unaltered):
```text
supported
```

### call-8 / VERIFICATION / verify

Input tokens344; output tokens2; latency0.172s; model stopeos.

Exact request:
```text
檢查候選敘述，回報 supported、contradicted 或 unresolved；非獨立真值：座椅的設計非常現代，由幾塊不同顏色的布料拼接而成
```

Raw answer (unaltered):
```text
supported
```

## Adaptive behavior

Caption/scene uncertain=false and missing=[]; no object/detail model calls. NO_TRIGGER. Each produced4 distinct literal candidates, total8. Two observation calls left6 slots;6 verifications consumed them. Attempting the next verification was refused BEFORE another model call. No9th call. This is a demonstrated coverage/budget mismatch, not evidence of model-load or GPU failure. No-new-evidence branch not exercised.

Caption hit128outputtoken cap and ended mid-sentence; preserve exact truncation. Scene raw text includes simplified「砖」; no OpenCC/translation or correction applied. User subsequently reviewed overall usability with the stated limitations; no assistant visual judging or per-claim correctness score.

## Verification

{"text": "這張圖片展示了一個室內空間，地面鋪有白色方形地磚", "observation_ids": ["call-1"], "status": "supported", "verification_id": "call-3"}

{"text": "在圖片中央，有一個圓形的座椅，座椅的靠背和坐墊部分是黃色的，而座椅的底座部分是灰色的", "observation_ids": ["call-1"], "status": "supported", "verification_id": "call-4"}

{"text": "座椅的設計非常現代，弧形的靠背和坐墊看起來非常舒適", "observation_ids": ["call-1"], "status": "supported", "verification_id": "call-5"}

{"text": "在座椅的右側，有一個黑色的背包，背包靠在座椅上", "observation_ids": ["call-1"], "status": "supported", "verification_id": "call-6"}

{"text": "這張圖片展示了一個室內場景，其中有一個圓形的黃色和灰色相間的座椅", "observation_ids": ["call-2"], "status": "supported", "verification_id": "call-7"}

{"text": "座椅的設計非常現代，由幾塊不同顏色的布料拼接而成", "observation_ids": ["call-2"], "status": "supported", "verification_id": "call-8"}

{"text": "地板是白色方形地砖，牆壁是白色的，上面有幾扇窗戶，窗戶上掛著百葉窗", "observation_ids": ["call-2"], "status": "unresolved", "verification_id": null}

{"text": "在座椅旁邊，有一個黑色的背包，以及一些其他物品，如掃帚和紙箱", "observation_ids": ["call-2"], "status": "unresolved", "verification_id": null}

Six explicit supported results parsed; two candidates remain unresolved with verification_id=null. Same-model support is not truth; subjective wording such as comfort is preserved, not independently endorsed. Raw/normalized/request/token/evidence links audited.

## Traditional Chinese reports

```markdown
# 影像理解報告（本地模型開發驗證，非正式論文結果）



執行 ID：e872fd65-cc75-4f2b-8954-a267fb018989

輸入 ID：<pre>indoor_desk_001</pre>

比較組別：D；狀態：partial

停止原因：TOOL_CALL_LIMIT；調查停止：NO_TRIGGER



## 簡述、場景與細節

INITIAL_CAPTION [call-1]

<pre>這張圖片展示了一個室內空間，地面鋪有白色方形地磚。在圖片中央，有一個圓形的座椅，座椅的靠背和坐墊部分是黃色的，而座椅的底座部分是灰色的。座椅的設計非常現代，弧形的靠背和坐墊看起來非常舒適。

在座椅的右側，有一個黑色的背包，背包靠在座椅上。在背景中，可以看到一些白色的櫃子和儲物櫃，櫃子上方有幾扇窗戶，窗戶上掛著白色的百葉窗。窗戶旁</pre>

SCENE_ANALYSIS [call-2]

<pre>這張圖片展示了一個室內場景，其中有一個圓形的黃色和灰色相間的座椅。座椅的設計非常現代，由幾塊不同顏色的布料拼接而成。地板是白色方形地砖，牆壁是白色的，上面有幾扇窗戶，窗戶上掛著百葉窗。在座椅旁邊，有一個黑色的背包，以及一些其他物品，如掃帚和紙箱。整個場景看起來像是在一個辦公室或公共區域。</pre>



## 敘述與驗證紀錄

<pre>這張圖片展示了一個室內空間，地面鋪有白色方形地磚</pre>

狀態：同模型觀察支持；來源：call-1；驗證：call-3

<pre>在圖片中央，有一個圓形的座椅，座椅的靠背和坐墊部分是黃色的，而座椅的底座部分是灰色的</pre>

狀態：同模型觀察支持；來源：call-1；驗證：call-4

<pre>座椅的設計非常現代，弧形的靠背和坐墊看起來非常舒適</pre>

狀態：同模型觀察支持；來源：call-1；驗證：call-5

<pre>在座椅的右側，有一個黑色的背包，背包靠在座椅上</pre>

狀態：同模型觀察支持；來源：call-1；驗證：call-6

<pre>這張圖片展示了一個室內場景，其中有一個圓形的黃色和灰色相間的座椅</pre>

狀態：同模型觀察支持；來源：call-2；驗證：call-7

<pre>座椅的設計非常現代，由幾塊不同顏色的布料拼接而成</pre>

狀態：同模型觀察支持；來源：call-2；驗證：call-8

<pre>地板是白色方形地砖，牆壁是白色的，上面有幾扇窗戶，窗戶上掛著百葉窗</pre>

狀態：未確定；來源：call-2；驗證：未執行

<pre>在座椅旁邊，有一個黑色的背包，以及一些其他物品，如掃帚和紙箱</pre>

狀態：未確定；來源：call-2；驗證：未執行



## 未確定、衝突與限制

以下為模型觀察；候選敘述不等於客觀真值，未明確驗證者維持未確定。

同模型驗證不是獨立真值；未驗證敘述及反駁內容不得視為事實。



## 資源摘要

工具嘗試次數：8

模型查詢總延遲（秒）：11.125；峰值保留顯存（MiB）：4688.0；缺失值表示未量測。
```

## Resource measurements

```json
{
  "verdict": "CONDITIONAL",
  "executed_images": 1,
  "outdoor": "NOT RUN / halted after indoor partial",
  "stop_reason": "TOOL_CALL_LIMIT",
  "calls": 8,
  "claims": 8,
  "verified": 6,
  "unresolved": 2,
  "output_tokens": 251,
  "peak_allocated_mib": 4429.57763671875,
  "peak_reserved_mib": 4688.0,
  "device_peak_mib": 5137,
  "cleanup": "PASS",
  "offline": "PASS within existing flags/Python audit",
  "human_review": "USER: overall usable with truncation/incomplete-verification limitations",
  "baseline_ready": false
}
```

All worker measurements retained in events.jsonl and parent device_samples.jsonl. Parameters/buffers/vision/language,inputs,visual/KV observed cuda:0. Windows shared GPU memory UNKNOWN / OBSERVABILITY LIMITATION.

## Latency

Load 12.532s; preprocessing 0.031s; sum modelcalls 11.125s; runtime E2E through cleanup before report write 25.609s; worker cleanup 0.172s; parent cleanup 0.969s. Full walltime recorded separately; no repeated benchmark.

## Offline

PASS within existing offline flags/Python network denial; no fetch attempt recorded. Not native/OS firewall proof.

## Cleanup

PASS: allocated0/reserved0, worker exit0, Jobempty, device baseline-equivalent. Outdoor halted despite successful cleanup because indoor execution incomplete.

## Human review

DEVELOPMENT HUMAN SANITY REVIEW — user response:「整體可用，但保留截斷與未完成驗證的限制」。All8 raw responses were presented before review. Exact statement and raw-event/report SHA256 recorded in evidence/human_review.json. This is overall development usability, not per-claim truth or a formal metric. No assistant semantic score. Verdict remains CONDITIONAL; partial verification, truncation and outdoor NOT RUN remain unchanged. No baseline READY or further execution approval inferred.

## Limitations and smallest proposed correction

No runtime repair or retry performed. PROPOSED ONLY: explicitly budget verification candidates against remaining calls, preserve all other claims as unresolved, and expose coverage plus a named verification-budget stop reason. Before implementing, agree whether bounded partial coverage is acceptable for development acceptance; do not silently label it complete. Keep8-call and128token bounds; no higher budget, model/prompt/precision/parser change proposed here. Add CPU coverage for8claims after2calls and freeze separately authorized repair validation before any GPU.

Do not infer general accuracy, improved completeness/hallucination or D superiority. No feature expansion/formal data. Rights-confirmed outdoor input remains available but was not executed.

## Tests

Pre-run93 CPU tests PASS(10.358s), Ruff PASS, strict Mypy28 PASS. No runtime source modifications. Source/asset hashes and prior synthetic raw hashes checked.

## AI assistance

Assistant performed local metadata/hash checks, approved deterministic resize, source/resource/trace audit and report preparation. No photograph sent to cloud/development vision tool, no runtime cloud judge, no independent visual correctness claim.
