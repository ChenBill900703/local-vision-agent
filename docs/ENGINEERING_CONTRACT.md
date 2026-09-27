# Minimal Engineering Contract v1 — Phase 1 CPU/mock

日期：2026-09-27。RD-001 不變。使用者已授權自行決定合理工程細節及 CPU 測試；本契約是工程決策，不是 GPU、模型能力或科學假設已獲證實。
實作：`contracts.py`、`image_input.py`、`agent.py`、`mock_adapter.py`、`tool_executor.py`、`reporting.py`、`mock_cli.py`。
全部位於 `src/local_vision_agent/`。不加入套件、不 import torch/transformers、不呼叫 GpuGuard 的真實查詢路徑。

## 輸入與輸出

- `ImageInput(input_id, path)`：本地單張 PNG/JPEG，依實際格式辨識，不以副檔名判斷；拒絕多影格。ID 非空、最多 128 字元。同一 batch 不可重複 ID。
- 讀取最多 bytes 上限 + 1；解碼前檢查尺寸，完整解碼驗證。EXIF transpose 後轉 RGB；不自動縮圖。RGBA 轉 RGB 忽略 alpha、不作背景合成；正式實驗須另凍結透明像素政策。
- `ImageInfo` 留原始 bytes SHA256、正規化尺寸與格式。mock 只收到 metadata、不分析像素；未實作真實 adapter 的像素傳遞／embedding cache。
- `Agent.run(item, Method)` 每張建立獨立記憶。`run_batch(list, Method)` 逐張執行，不支援多圖共同上下文；空 batch、重複 ID、超量 batch 在開始前拒絕。
- `Report` JSON v1 包含 run/input ID、method、模型 fixture ID/revision、政策版本、limits、input hash、observations、claims、states、status、stop_reason、investigation_stop。
- 每筆 observation 保留 call ID、state、工具名、prompt ID／文字、token 上限、answer 或 error。每項 claim 連回 observation IDs；verification 留原 claim 與額外 verification ID，不覆寫來源。
- 繁中 Markdown 為非模型格式化：簡述／場景／細節、敘述與驗證、未確定／衝突、停止原因、資源摘要。模型文字 HTML escape，不能變成命令或連結工具。
- `MOCK_NOT_RESEARCH_EVIDENCE` 永久標籤；peak VRAM/model latency 為 null。模擬文字、synthetic pixels、mock tokens 都不是論文數據。未實作正式 manifest／評分器／圖表，也未聲稱真實模型能生成繁中。

## 介面、控制流程與比較

`VisionAdapter` Protocol：model_id、revision、is_mock、capabilities，以及 `invoke(Request, ImageInfo) -> Answer`。
`Request` 限 caption/query、固定 prompt ID、prompt、output token 上限、可選 claim。
`Answer` 包含 text、claims、uncertain、missing(object/detail)、verdict、output_tokens；不可把自由模型文字當工具名。未來 Moondream parser 需另測，現在沒有自然語言 claim 抽取器。

執行入口只接受精確 `MockAdapter` 類型及 `agent-mock-v1` 設定，無 dynamic import／模型 registry／網路 fallback。真實 adapter 尚未 enabled。
可注入 `Executor` 和 clock 只供受信任 CPU 測試；不是執行任意外部 adapter 的安全沙箱。正式入口使用 spawn worker。

| 階段 | v1 決策／上限 |
|---|---|
| START | 檢查必要設定、圖片與 method；真實模型路徑直接拒絕 |
| INITIAL_CAPTION | 恰一次 caption；A 到 REPORT/STOP |
| SCENE_ANALYSIS | B/C/D 恰一次 scene query |
| OBJECT_CHECK | B/D：caption 或 scene uncertain／missing object 才 query；C 固定 query |
| DETAIL_QUERY | B/D：早期 missing detail 或 object uncertain／missing detail 才 query；C 固定 query |
| VERIFICATION | 僅 C/D；對去重後 claims 各一次相同 query，不再回饋調查 |
| REPORT / STOP | 無額外模型呼叫，所有正常／錯誤路徑均有終止紀錄 |

調查 prompt 各最多一次；verification 每個唯一 claim 最多一次。固定優先順序 scene → object → detail；有限庫用盡不重新問。
新增證據在本工程 fixture 中定義為新增唯一 claim 文字；detail 沒有新增 claim 記 `NO_NEW_EVIDENCE`，有新增記 `QUERY_SET_DONE`；無 detail trigger 記 `NO_TRIGGER`。
這不是語意去重或已經驗驗證的充分性判準。B/D 共用調查程式及 budgets，只有 D 追加驗證；C/D 只改調查觸發，verification 完全相同。A 僅一次回應，所有組別相同 per-call 輸出上限。
supported 只指同模型支持；contradicted 與 unresolved 分開，不視為獨立真值，也不校準機率。

## 必填安全設定

唯一執行設定為 `configs/agent_mock.toml`。所有欄位必填、拒絕額外設定／不明 schema；整數欄位拒絕 bool、小數、NaN、無窮大、零、負數。時間為有限正數。

| 設定 | mock 工程值／單位 |
|---|---|
| max_tool_calls / max_model_calls / max_iterations | 各 12；每次工具嘗試為一次迭代，失敗也佔一次 |
| per_call_timeout_s / per_image_timeout_s | 5 / 60 秒 |
| cleanup_timeout_s | terminate 等 1 秒，再 kill 等 1 秒；仍存活回報 CLEANUP_FAILED |
| max_input_bytes | 10,485,760 bytes |
| max_pixels / max_image_edge_px | 1,048,576 pixels / 1024 px |
| max_input_tokens | 1024；mock 以 UTF-8 bytes 作保守 proxy，非真實 tokenizer 計數 |
| max_output_tokens / max_total_output_tokens | 256 / 2048；mock 回應宣告值，非量測 |
| max_response_chars | 每回應 text + claims 合计 2048 字元 |
| max_memory_entries | observations 最多 12，去重 claims 最多 12 |
| max_batch_images | 16，sequential，每張 reset |

以上只適用 mock 工程測試，不以數值推定 GPU 可承擔。CPU 時間不當 VLM latency。
worker timeout 包括啟動等待；以 monotonic deadline，逾時 terminate/kill 並確認退出，不採 thread timeout 後背景繼續跑。
per-image 是調度 deadline：從圖片處理開始計算，工具取得剩餘時間與 per-call 上限的較小值，返回後再檢查。**本版本不硬性中斷主程序中的檔案 I/O／Pillow 解碼／報告格式化，OS 排程與 cleanup 亦可能超出 deadline。**這些不是正式端到端硬 timeout 保證；真實 adapter 整合前需把整個工作生命週期移入受控 worker。
受控 worker 目前每工具啟動一次，僅適合 mock；真實 GPU 必須改成單一長駐模型生命週期，不能照此反覆載入模型或聲稱量到正式 latency。

## 失敗與分母

| 錯誤／停止 | 行為 |
|---|---|
| INVALID_CONFIG / INVALID_LIMIT / MISSING_LIMITS / INVALID_METHOD | 開始前拒絕；不補安全 defaults，不啟動 adapter |
| REAL_ADAPTER_NOT_ENABLED | 拒絕真實／未知 adapter，沒有自動 mock fallback |
| INVALID_INPUT_ID / IMAGE_IO_ERROR / INVALID_IMAGE / UNSUPPORTED_IMAGE | 該張 failed，無工具 calls；batch 可續下一張 |
| IMAGE_BYTES_LIMIT / IMAGE_PIXELS_LIMIT / IMAGE_EDGE_LIMIT | 拒絕該圖，不偷偷縮圖 |
| TOOL_CALL_LIMIT / MODEL_CALL_LIMIT / ITERATION_LIMIT / MEMORY_LIMIT | 不新增呼叫，保留 partial report |
| INPUT_TOKEN_LIMIT / OUTPUT_LIMIT / INVALID_TOOL_RESULT | 拒絕不合規內容；oversized/malformed payload 不納入 memory，留 error |
| UNSUPPORTED_TOOL / TOOL_FAILURE | 留 call 與 error，不把失败解讀成物件不存在；無 retry |
| TOOL_TIMEOUT / IMAGE_TIMEOUT / CLEANUP_FAILED | 留 partial/failed；停止 batch，其餘輸入仍回報 not_attempted/BATCH_HALTED |
| COMPLETED | 預定流程結束，仍可有 uncertain/unresolved/contradicted，不代表認知完整或辨識正確 |

TOOL_FAILURE 也停止 batch。無成功 observation 為 failed；已有內容為 partial；complete 只代表工程流程完成。
每張都有 report，未嘗試不假稱嘗試；正式分母規則需在 protocol freeze 明列，不能丟棄錯誤後只算成功。
GPU OOM/preflight/offload 安全路徑尚未在新 adapter 實作；不以現有 guard CPU 測試當硬體證明。

## 執行 CPU 測試與 mock

使用既有環境（不安裝）：

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
$env:PYTHONIOENCODING = 'utf-8'
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

本機自行提供一張已獲准的圖片；mock 不辨識它，指令輸出到 stdout，不覆寫既有檔案：

```powershell
.\.venv\Scripts\python.exe -B -m local_vision_agent.mock_cli --adapter mock --config configs/agent_mock.toml --image YOUR_LOCAL_IMAGE.png --input-id mock-example --method D --format markdown
```

`--method A/B/C/D` 選擇比較介面；JSON 是預設格式。不要執行 `gpu_guard` 的 CLI 或 `scripts/check.ps1 -GpuSnapshot`；本次未授權。
舊分類模組仍可被直接匯入作歷史 CPU 測試，但新入口完全不匯入它們；`configs/models.toml` 所有模型停用，原始 bytes 已快照。
