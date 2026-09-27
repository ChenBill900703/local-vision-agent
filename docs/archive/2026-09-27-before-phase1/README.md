# Local Agentic Image Understanding on RTX 3070 Ti 8GB

本專案研究「完全本地的輕量視覺 Agent」，比較同一個視覺模型的 single-pass 與 bounded multi-stage analysis，評估資訊完整性、hallucination／可靠性，以及時間與顯存成本。

研究方向已於 **2026-09-27 USER-CONFIRMED / FROZEN（RD-001）**。工作題目：
**Design and Evaluation of a Local Agentic Image Understanding System on an 8GB Consumer GPU**。

目前仍為 **DOCUMENTATION ONLY**。文件完成不代表系統完成；不得因本 README 或時程而自行開始實作、下載、GPU 工作、測試或發布。

## 先讀什麼

1. [AGENTS.md](AGENTS.md)：執行邊界、安全、品質及學倫規範。
2. [RD-001](docs/RESEARCH_DIRECTION.md)：最高層級專案研究決策；僅使用者明確批准可變更方向。
3. [REQUIREMENTS v2.0](docs/REQUIREMENTS.md)：目前需求與尚未驗證的契約。
4. [EXPERIMENT_PROTOCOL v0.3](docs/EXPERIMENT_PROTOCOL.md)：Agent 實驗提案，**尚未正式凍結**。
5. [DELIVERY_PLAN v2.0](docs/DELIVERY_PLAN.md)：唯一 active roadmap。
6. [RESEARCH_SOURCES](docs/RESEARCH_SOURCES.md)、[ENVIRONMENT](docs/ENVIRONMENT.md)：來源及歷史環境證據。

[docs/ROADMAP.md](docs/ROADMAP.md) 與 [archive](docs/archive/2026-09-27-pre-RD-001/INDEX.md) 只供歷史追溯，不是第二套需求或時程。根目錄沒有另一份 ROADMAP.md。

## 研究什麼

- RQ1：輕量 VLM 能否在指定 8GB 環境作為 fully local Agent 的視覺核心？
- RQ2：多階段流程能否比 single-pass 提高重要視覺資訊的完整性？
- RQ3：verification 能否降低可觀察的錯誤物件描述／hallucination／未驗證敘述？
- RQ4：品質變化需要付出多少 latency、peak VRAM、inference calls 與計算成本？

Null／negative／無顯著差異都保留，不以「一定比傳統方法好」作為必須製造的結論。系統不保證完整理解所有影像、零幻覺、論文接受或畢業。候選貢獻是受限硬體上可追溯的 bounded workflow 及受控實驗；新穎性尚待文獻與教授確認。

## Runtime 與功能

Image → Local Vision Agent → Lightweight VLM → Multi-stage analysis → Verification → Structured Traditional Chinese Report。

Moondream2 是 **primary candidate / proposed main model / pending hardware validation**，不是已驗證的選定版本。
Agent 使用有限狀態、有限迭代、有限工具；不需要額外 LLM controller。
核心含 caption、visual query/VQA、物件與細節驗證、observation memory、不確定性與停止條件、繁體中文結構化報告。
Detect、point/grounding 僅在 exact revision 支援且硬體驗證通過後啟用，不是第一版必做的獨立偵測系統。

GPT-6 Astra 只協助開發與研究紀錄；**不是 runtime**。正式系統不得依賴 OpenAI/GPT API、雲端 LLM、Astra Runtime 或外部線上模型服務。模型與必要資產未來經批准取得後，主要分析須能斷網執行。

最低實驗比較：

| 組別 | 設計 | 目的 |
|---|---|---|
| A | 同一 Moondream2 的 single-pass | 必要 baseline |
| B | 多階段＋adaptive bounded query，無 verification | 與 D 比較驗證機制 |
| C | fixed-query＋verification | 與 D 比較自適應查詢 |
| D | adaptive bounded query＋verification | 完整 proposed Agent |

所有組別固定同一 backbone/revision，避免把換強模型的效果誤當成 Agent 效果。

## 不研究什麼／舊方案如何處理

Pet/DTD、DINOv2-Small linear classifier、ResNet18、temperature scaling、selective classification、classification abstention 與 AURC primary metric 已 **SUPERSEDED**。不再是 thesis core 或新系統前置條件；附加使用須另行確認。

第一版不含大型 multi-agent debate、自由網路搜尋、cloud orchestration、video、image generation、大型 OCR、segmentation、任意聊天、foundation model training、大規模 VLM fine-tuning。
Moondream3／3.1 只列 related/future work 或另行批准的 optional comparison。

## 主研究資源與 GPU 安全

- RTX 3070 Ti 8GB、Intel Core i7-11700K、32GB RAM、Windows、既有 Python 3.11。
- 先前使用者回報可用磁碟約 500GB、GPU 可整天使用；實際空間／空閒 GPU 在未來批准的 feasibility 前重新確認。本次未檢查 GPU。
- 同時最多一個 heavyweight model，預設 GPU batch size 1；批量輸入逐張排程。
- 載入前需 GpuGuard.preflight；規劃 process ceiling 6400 MiB，還需在扣除既有使用量及預估工作量後保留至少 1536 MiB。
- 6400 MiB 是上限而非可用保證，guard 不是硬體配置器上限；桌面佔用會縮小實際可用預算。
- 禁止 device_map="auto"、CPU/disk offload、Windows shared GPU memory 作為 fallback。一般 CPU 圖片解碼／報告生成不等於模型 offload。
- 限制解析度、tokens、calls、iterations、timeout；不符合預算或 OOM 必須記錄並安全停止，不能偷換硬體或偷偷降級。
- 所有模型顯存估算在真機測試前標 unmeasured；本次沒有 Moondream2 VRAM／速度測量。

## 真實完成狀態

| 項目 | 2026-09-27 狀態 |
|---|---|
| RD-001、需求與實驗提案同步 | 文件已校正；非實作成果 |
| Python/套件／CPU 測試 | ENVIRONMENT 保留 2026-09-22 歷史紀錄；本次未重測 |
| src/local_vision_agent/gpu_guard.py | 已有 guard 骨架；不是新模型安全適配／實測證明 |
| routing.py、evaluation.py 及其 tests | LEGACY 分類方案程式；原樣保留，未移植成新 Agent |
| configs/models.toml | LEGACY；仍包含 CLIP/DINOv2/ResNet18 舊設定，文件標示不會停用程式；不得當成新方案執行配置 |
| scripts、lock、CI | 原樣保留；既有驗證／依賴不等於 Moondream2 相容性證明 |
| Moondream2 adapter、bounded Agent、工具／記憶／驗證 | 尚未實作與硬體驗證 |
| 中文報告、資料流程、新評估／圖表、A–D 整合 | 尚未完成 |
| 正式模型 revision、資料集、主要指標／門檻 | UNKNOWN／待決，正式 test 前凍結 |
| 論文實驗結果 | 尚無新方向正式實測結果 |

## 決策登錄

狀態區分 USER-CONFIRMED、PROPOSAL、UNKNOWN、SUPERSEDED；沒有證據不可寫成機構已核准。

| 決策 | 狀態 | 確認者 | 日期 | 證據／下一步 |
|---|---|---|---|---|
| RD-001 方向、RQ1–4、local runtime、A–D | USER-CONFIRMED / FROZEN | 使用者 | 2026-09-27 | 本次完整凍結指示；見 RD-001 |
| 主硬體、Windows、Python 3.11 | USER-CONFIRMED | 使用者 | 2026-09-27 | 本次硬體研究條件 |
| Moondream2 優先候選 | USER-CONFIRMED（候選身分） | 使用者 | 2026-09-27 | 不等於 revision 或 fit 已確認 |
| 10/31 程式、11 月實驗、12/31 初稿 | USER-CONFIRMED（目標） | 使用者 | 2026-09-27 | 不保證完成，詳 DELIVERY_PLAN |
| 中文報告、公開 GitHub 意向、500GB／全天 GPU | USER-CONFIRMED（先前需求） | 使用者 | 先前對話，確切日期未留存 | 本次未重新量測，也未批准 push |
| exact revision、license 適用、中文及硬體能力 | UNKNOWN | 研究者／使用者 | — | 授權後 feasibility，保留來源證據 |
| final dataset、主要指標、門檻、樣本數、人評設計 | PROPOSAL / UNKNOWN | 研究者／指導教授 | — | EXPERIMENT_PROTOCOL 尚未正式 freeze |
| 新穎性、投稿場次、校方／倫理／AI 揭露要求 | UNKNOWN | 指導教授／崑山科技大學資工系研究所／投稿單位 | — | 尚無核准證據，不自行推定 |
| 程式授權、各項資產可公開範圍 | UNKNOWN | 權利人／使用者 | — | 教授「隨意」不取代第三方授權 |
| 舊 Pet/DTD 分類主線 | SUPERSEDED | 使用者 | 2026-09-27 | 歷史保留；附加測試未批准 |

## 下一階段的授權界線

現在只完成文件校正。未來先取得**實作授權**；下載／GPU feasibility 再按明確範圍批准，正式實驗及發布另有 phase gate。
先驗證 Moondream2 revision、remote code、授權、現有 Windows 套件相容性、8GB 峰值、中文輸出與有限工具行為，不擴充成新一輪模型／題目競賽。
模型若有實證 blocker，只能提報受控替換，不得擅自改回分類題目。
