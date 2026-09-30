# Local Agentic Image Understanding on RTX 3070 Ti 8GB

**目前：SMARTPHONE SOURCE INPUT = CPU READY；VERIFICATION BUDGET REPAIR = CPU READY。**
原始手機JPEG/PNG由程式自動安全解碼與縮圖，模型仍只接收既有448單tile；110項CPU測試、Ruff、Mypy通過。
COMBINED GPU VALIDATION = PENDING AUTHORIZATION；本階段未使用GPU、未宣告baseline READY。
[輸入修正](docs/SMARTPHONE_SOURCE_INPUT_REPAIR.md)／[新的原圖GPU前瞻文件](docs/SMARTPHONE_COMBINED_GPU_VALIDATION_AMENDMENT_2026-09-30.md)。

**目前：VERIFICATION BUDGET REPAIR = CPU READY / GPU VALIDATION PENDING。**
已完成FIFO額度排程及報告v2；101項CPU測試、Ruff、Mypy通過。本階段未使用GPU。
[修正契約](docs/VERIFICATION_BUDGET_REPAIR.md)／[前瞻GPU修訂（未授權執行）](docs/VERIFICATION_BUDGET_REPAIR_GPU_VALIDATION_AMENDMENT_2026-09-30.md)。
既有natural-image CONDITIONAL不改判，尚未宣告工程基線READY。

**目前 2026-09-30：REAL IMAGE DEVELOPMENT SANITY = CONDITIONAL。**
室內圖於第8次呼叫後依安全上限停止，尚有2個候選敘述未驗證；GPU清理成功，室外圖未執行。
[本次結果](docs/REAL_IMAGE_DEVELOPMENT_SANITY_RESULT.md)／[CURRENT交接](SESSION_HANDOFF.md)。
原合成圖smoke PASS仍有效；本次尚未確認自然圖片工程基線READY。以下較早狀態保留歷史。

**目前 2026-09-30：REAL INTERNVL AGENT GPU SMOKE = PASS。**
原合成圖片、一次載入、Method D 六次真實呼叫，已走完 Agent／Adapter／RPC／persistent worker／繁中報告與清理。
來源與既有整合 checkpoint 相同；不是 A–D 比較或論文假設驗證。無新依賴、下載、模型或政策變更。
[Smoke 結果](docs/REAL_INTERNVL_AGENT_GPU_SMOKE_RESULT.md)／[最新 CURRENT 交接](SESSION_HANDOFF.md)。
真實圖片 sanity 尚未執行，尚不宣告工程基線 READY；[下一階段提案](docs/REAL_IMAGE_DEVELOPMENT_SANITY_PROPOSAL.md)。
下方所有較早日期的狀態保留歷史，不覆蓋目前結果。


**最新 2026-09-28：ADOPT INTERNVL3-2B-INSTRUCT AS PRIMARY VLM CANDIDATE。**
新 capability pilot 的五次查詢與安全／離線／清理通過；使用者於原始輸出後人工確認全部能力及繁中可用。
[採用決策](docs/INTERNVL3_ADOPTION_DECISION.md)／[能力補測結果](docs/INTERNVL3_AGENT_CAPABILITY_RESULT.md)。
已從本地 adoption checkpoint `580d0a92c529b0e4aca692b658ca77d675a4678c` 完成 real adapter／persistent worker／bounded Agent 程式接合與 CPU 測試；新整合的 GPU 端到端驗證尚未執行。不是 RQ2–RQ4 成功。
[整合契約與驗證界線](docs/REAL_INTERNVL_INTEGRATION.md)。以下舊 phase 結果保留歷史。


**目前（2026-09-28）：InternVL3 feasibility = CONDITIONAL PASS — SMALL ENGINEERING BLOCKER。**
一次離線載入及四項英文／繁中核心測試成功，清理歸零；過嚴的工程字詞門檻跳過四項能力探測，因此尚不能完整採用或整合。
[完整實測報告](docs/INTERNVL3_2B_GPU_FEASIBILITY_REPORT.md)、[SESSION_HANDOFF](SESSION_HANDOFF.md)。本次 GPU 額度已用完，停止執行。使用者本次授權為 InternVL3 Safe Migration + Full Local Feasibility。
只評估固定版本 InternVL3-2B-Instruct；[事前修訂](docs/INTERNVL3_PILOT_AMENDMENT_2026-09-28.md)、[靜態審查](docs/INTERNVL3_STATIC_REVIEW_2026-09-28.md)。Moondream2 已封存於本地 checkpoint `cb171216dac7f7fd99aa6b9a2776de4bd1311af4`。不直接整合 Agent、不變更 RD-001、不再調整 Moondream2 中文 prompt。下文舊授權與結果保留歷史。

**歷史（2026-09-27）：最後一次 Moondream2 語言診斷已結束。English control PASS；英文指令要求繁中輸出 FAIL（仍全英文）；cleanup PASS。**
`MOONDREAM2 DIRECT TRADITIONAL CHINESE OUTPUT = REPRODUCIBLE BLOCKER`（本次固定設定）。
依使用者停止規則，停止 Moondream2 prompt tuning，建議 `EVALUATE FALLBACK VLM`，優先另行評估 OpenGVLab/InternVL3-2B-Instruct；尚未批准或執行替代模型下載／載入／整合。
[最終 dated result](docs/PHASE2_LANGUAGE_FINAL_RESULT_2026-09-27.md)。下方 Repair1 與早期結果保留為歷史，不改寫其負面證據。

本專案研究「完全本地的輕量視覺 Agent」，比較同一個視覺模型的 single-pass 與 bounded multi-stage analysis，評估資訊完整性、hallucination／可靠性，以及時間與顯存成本。

研究方向已於 **2026-09-27 USER-CONFIRMED / FROZEN（RD-001）**。工作題目：
**Design and Evaluation of a Local Agentic Image Understanding System on an 8GB Consumer GPU**。

目前為 **Phase 2 repair1：CONDITIONAL PASS**。真實 load／encode／英文 caption/query、Windows supervisor 與 allocator 清理已通過本次有限驗證；中文 query 仍重複問題，完整 Agent／繁中功能尚未驗收。詳見 [修復結果](docs/PHASE2_REPAIR1_RESULT.md) 與 [事前修訂](docs/PHASE2_REPAIR1_AMENDMENT.md)。所有結果為 **PILOT / EXPLORATORY / NOT FORMAL THESIS RESULT**。

首次 pilot 的 FAIL 與原始證據完整保留於 [初次實測報告](docs/MOONDREAM2_GPU_FEASIBILITY_REPORT.md)。使用者要求續行修復後，另完成一次具名 repair1；兩次額度均已使用，不自動追加 GPU 嘗試。

2026-09-27 使用者明確批准 Phase 2 的硬體查詢／CUDA、本地 baseline commit、固定資產取得及一次受限 GPU pilot，取代 Phase 1 對這些項目的禁止。一次載入已使用，不自動重試；無依賴新增／升級、無資料集、無 push／發布。完整授權在 ignored evidence，摘要在 AGENTS.md；[Phase 1 README 快照](docs/archive/2026-09-27-before-phase2/README.md) 保留全部舊狀態與授權歷史。

工程契約與操作方式見 [ENGINEERING_CONTRACT v1](docs/ENGINEERING_CONTRACT.md)，測試及 AI 協作紀錄見 [PHASE1_RECORD](docs/PHASE1_RECORD.md)，下一階段提案見 [MOONDREAM2_FEASIBILITY](docs/MOONDREAM2_FEASIBILITY.md)。

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

Moondream2 是 **primary candidate；固定 revision 已通過有限的 load/encode/英文 caption/query 及清理，繁中與完整 Agent 仍待驗證**，不是正式評估已凍結版本。
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
- Phase 2 實測：GPU dedicated total 8192 MiB，worker 前 used/free 182/7836 MiB；磁碟／資產統計另存 evidence。這些是特定時間快照。
- 同時最多一個 heavyweight model，預設 GPU batch size 1；批量輸入逐張排程。
- 載入前需 GpuGuard.preflight；規劃 process ceiling 6400 MiB，還需在扣除既有使用量及預估工作量後保留至少 1536 MiB。
- 6400 MiB 是上限而非可用保證，guard 不是硬體配置器上限；桌面佔用會縮小實際可用預算。
- 禁止 device_map="auto"、CPU/disk offload、Windows shared GPU memory 作為 fallback。一般 CPU 圖片解碼／報告生成不等於模型 offload。
- 限制解析度、tokens、calls、iterations、timeout；不符合預算或 OOM 必須記錄並安全停止，不能偷換硬體或偷偷降級。
- 6000 MiB 仍是 general workload 的 provisional estimate；本次單圖實測 VRAM／速度見報告，不由單張幾何圖推論最壞情況。

## Phase 2 狀態增補

固定 model/tokenizer、完整來源審閱、受控本地 patch、single persistent worker 與 68 項 CPU tests 已完成。repair1 解決清理／監督問題；英文 query 正常回答，中文問題仍未解決。A–D Agent 仍為 Phase 1 mock，尚未接入真實 worker。query 單 suffix 對照未解決中文問題，不擅自取代 upstream 預設。詳見修復報告與 [靜態審閱](docs/PHASE2_STATIC_REVIEW.md)。

## Phase 1 完成時的歷史狀態（保留，不代表最新 GPU 結果）

| 項目 | 2026-09-27 狀態 |
|---|---|
| RD-001、需求與實驗提案同步 | 文件已校正；非實作成果 |
| Python/套件／CPU 測試 | 使用既有 Python 3.11.9；本次 CPU 測試結果見 PHASE1_RECORD；未跑歷史環境驗證腳本 |
| src/local_vision_agent/gpu_guard.py | 已有 guard 骨架；不是新模型安全適配／實測證明 |
| routing.py、evaluation.py 及其 tests | LEGACY 分類方案程式；原樣保留，未移植成新 Agent |
| configs/models.toml | LEGACY；所有 enabled 已關閉，原始設定有快照；新 loader 拒絕此 schema |
| scripts、lock、CI | 原樣保留；既有驗證／依賴不等於 Moondream2 相容性證明 |
| bounded Agent、工具／記憶／驗證、A–D | CPU/mock 骨架已實作；真實 Moondream2 adapter 與硬體驗證尚未完成 |
| 中文報告 | 繁中 JSON／Markdown 結構及 mock 文字已驗證；真實模型繁中語意能力未驗證 |
| 資料流程、新評估／圖表 | 單張／逐張批量輸入契約已實作；正式 manifest、評分、圖表未完成 |
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
| Phase 1 程式／設定／文件／CPU tests | USER-CONFIRMED | 使用者 | 2026-09-27 | 本 chat「請開始本專案第一階段」及明確授權段落；取代 documentation-only |
| 最小工程契約及 mock limits v1 | ENGINEERING DECISION（使用者授權自行決定細節） | Codex 擬定；人工審閱待完成 | 2026-09-27 | ENGINEERING_CONTRACT；非硬體核准／科學 protocol freeze |
| 11/1 驗收目標 | USER-CONFIRMED（目標） | 使用者 | 2026-09-27 | 本次指示；保留 10/31 核心程式及 11 月實驗／12/31 初稿 |
| Moondream2 2025-06-21 / 9a7d402… 候選 | PROPOSAL（官方來源已核對） | Codex 查核；採用待確認 | 2026-09-27 | MOONDREAM2_FEASIBILITY；未下載、未執行、未驗證 fit |
| Phase 2 固定 revision/tokenizer、取得資產、CUDA、baseline commit、一次 pilot | USER-CONFIRMED；一次已使用 | 使用者 | 2026-09-27 | 完整貼文存 artifacts/phase2-20260927/evidence/user_authorization.txt；取代上列 Phase 1 禁止範圍 |
| Phase 2 初次驗收 | FAIL／已停止，非正式研究結論 | Codex 記錄；人工審閱待完成 | 2026-09-27 | MOONDREAM2_GPU_FEASIBILITY_REPORT；不改 RD-001，不自動重試 |
| repair1 修復與一次驗證 | USER-CONFIRMED 續行；已使用 | 使用者 | 2026-09-27 |「請繼續進行 盡量解決掉問題」；PHASE2_REPAIR1_AMENDMENT |
| repair1 結果 | CONDITIONAL PASS；中文未通過 | Codex 記錄；人工審閱待完成 | 2026-09-27 | PHASE2_REPAIR1_RESULT；不得由工程測試宣稱論文改善 |

## 下一階段的授權界線

Phase 2 已取得的資產可保留，不需重新下載。下一次 GPU 載入須另行批准具名 retry 與 blocker 修正方案，維持相同資源／停止上限；不能刪除 initial-pilot 紀錄來繞過一次限制。正式實驗及發布仍需另外授權。
先驗證 Moondream2 revision、remote code、授權、現有 Windows 套件相容性、8GB 峰值、中文輸出與有限工具行為，不擴充成新一輪模型／題目競賽。
模型若有實證 blocker，只能提報受控替換，不得擅自改回分類題目。
