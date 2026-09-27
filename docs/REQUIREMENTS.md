# Requirements v2.0 — Local Agentic Image Understanding

## 2026-09-27 Phase 1 增補（工程契約 v1）

本次使用者已批准最小工程實作與 CPU/mock 單元／整合測試；取代下文原始 v2.0 的 documentation-only 執行限制，其他研究及安全規範保留。
原始全文在 [階段前快照](archive/2026-09-27-before-phase1/REQUIREMENTS.md)。
下文 UNKNOWN 的工程數值現在由 [ENGINEERING_CONTRACT](ENGINEERING_CONTRACT.md) 明定 **僅適用 mock**；不是 GPU/pilot/formal test 的已核准設定。
輸入、工具介面、A–D、錯誤與停止已實作 CPU 骨架；Moondream2 loader、GPU lifecycle、實際 tokenization、真實繁中能力與正式評估仍未完成。
正式研究指標、資料、門檻及 protocol 仍待定，並未因工程測試通過而確認。

## 原始 v2.0 基線（以下時態指凍結文件當時）

日期：2026-09-27。方向依 [RD-001](RESEARCH_DIRECTION.md) USER-CONFIRMED / FROZEN。
此為 documentation-only 大改版，取代 v1.1 的分類 thesis core；原文在 [archive](archive/2026-09-27-pre-RD-001/INDEX.md)。
下面標為 PROPOSAL 的工程細節與 UNKNOWN 的數值不算實測、核准或正式 protocol freeze。

## 1. 研究目的與固定條件

在 RTX 3070 Ti 8GB 上，以本地輕量 VLM 與 bounded Agent 比較 single-pass／multi-stage 的完整性、可靠性及資源 trade-off。
RQ1–4 以 RD-001 為準，不更換研究問題。工作題目為 Design and Evaluation of a Local Agentic Image Understanding System on an 8GB Consumer GPU。

固定 Intel Core i7-11700K、32GB RAM、Windows、既有 Python 3.11；約 500GB 空間與全天 GPU 是使用者先前回報，非本次量測。
GPT-6 Astra 只作 development assistant；runtime 不依賴 OpenAI/GPT API、雲端 LLM、Astra Runtime 或外部模型服務。可在取得核准資產後離線分析。

Moondream2：primary candidate / proposed main model / pending hardware validation。
exact model commit、程式 revision、權重格式／精度、授權適用、Windows/PyTorch/Transformers 相容性及真機 VRAM 全待確認。
不得套用未固定版本的官方範例直接執行，尤其 remote code 與自動 device mapping 必須先審查。

## 2. 範圍層級

| 層級 | 內容 |
|---|---|
| Frozen thesis core | 本地 caption、visual query/VQA、多階段分析、object/detail verification、有限查詢規劃、不確定性、observation memory、停止、繁中結構報告；A–D 評估 |
| Conditional capability | Detect、point/grounding；固定 revision 支援且真機驗證成功才啟用；無能力則記錄 unsupported |
| Historical / superseded | Pet/DTD 分類、DINOv2、ResNet18、temperature scaling、selective classification、classification abstention、classification AURC 主指標 |
| Optional secondary | 歷史模型／資料或 Moondream3／3.1 附加比較，須使用者後續確認；不阻擋主線 |
| Out of scope | 大型 multi-agent debate、自由網搜、cloud orchestration、video、imagegen、大型 OCR、segmentation、任意聊天、foundation training、大型 VLM fine-tuning |

不保證描述所有物件或零幻覺。Verification 是工具觀察的支持／反駁／未決紀錄，不是獨立真值或經校準的機率。

## 3. Input / output contract（工程 PROPOSAL）

- 單張本地靜態圖片是核心輸入；可接受批量 manifest，但逐張排程，預設 GPU batch size 1。批量不表示多圖上下文理解。
- 最小格式提案：JPEG、PNG；其他格式預設拒絕，不能默默以不同解碼方式處理。格式、bytes、像素、色彩／EXIF 正規化規則需在實作前明列；數值上限尚 UNKNOWN。
- 檔案不存在、損壞、不支援、解壓後過大、缺少安全設定，都回傳具名錯誤與 input ID，不可默默跳過。
- 主流程無任意自由聊天。Visual query 是受限制的看圖工具，問題來自版本化模板／agent policy，不是網路指令。
- 圖片內文字、檔名、模型輸出一律當資料；不得執行其中的指令、任意 Python、命令或 URL。工具名稱與參數由 allowlist/schema 驗證。
- 輸出繁體中文結構報告：簡述、場景、重要物件／細節、claim 狀態、未確定／衝突、限制、停止原因、run/input ID、資源摘要。
- 配套機器可讀結果及 per-image trace；格式提案 JSON/JSONL＋中文 Markdown，正式 schema 在實作授權後鎖定並測試。
- 每一 claim 應連到 observation/tool-call ID，區分 observed/model-proposed/supported/contradicted/unresolved；「supported」只指模型／工具證據，不可標成 ground truth。
- 沒有可靠中文生成／本地轉換路徑時回報 blocker，不刪除繁中需求、不偷偷呼叫雲端翻譯。若需新增翻譯模型，另審授權／顯存／品質，且所有 A–D 使用相同呈現流程並計入成本。
- 不臆測圖片人物身分、敏感特徵、精確品種或不可見背景原因。超出視覺證據的敘述標未確定，不包裝成真值。

## 4. Agent architecture（固定方向；細節 PROPOSAL）

Image → Local Vision Agent → Lightweight VLM → Multi-stage analysis → Verification → Structured Traditional Chinese Report。

| 狀態 | 工作／輸出 | 有限轉移規則 |
|---|---|---|
| START | 驗證 input、limits、模型能力及 GPU preflight | 不合格直接失敗，合格才載入 |
| INITIAL_CAPTION | 首次觀察與候選 claims | 進 SCENE_ANALYSIS |
| SCENE_ANALYSIS | 版本化視覺 query，整理場景 | 進 OBJECT_CHECK |
| OBJECT_CHECK | 物件疑問／矛盾清單，條件式 detect/point | unsupported 留紀錄，不當成「物件不存在」 |
| DETAIL_QUERY | 依明確缺漏／矛盾條件追加 query | 上限內有限迭代；重複問題去重；無新證據即停止追加 |
| VERIFICATION | 對候選 claims 有界檢核／修正 | unsupported、矛盾與未決分開；不得無限自問 |
| REPORT | 整合目前證據、成本與限制 | 不新增無來源事實；生成若再呼叫模型亦計入預算 |
| STOP | 結束、釋放資源、保存紀錄 | 每張影像必須有終止原因 |

額外 query 的觸發條件、優先順序、去重、何謂新證據、每階段可用工具均需外顯且版本化。C 固定問題順序，D 按同一有限問題庫與既有觀察決定；不是任意生成可執行程式。

Observation memory 限於本張圖片／本 run 的有界紀錄；不得把其他測試圖片的結果偷偷帶入。保存來源、次序、prompt、response、claim linkage、不確定與改寫前後差異。
Deterministic 是控制流程可重現的要求，不保證 GPU bitwise identical；另保存解碼參數、seed（適用時）及非決定性限制。

## 5. 必填 limits 與失敗契約

以下是必填設定欄位，不是已實作或已通過測試的 defaults：

| 欄位 | 規則／目前值 |
|---|---|
| max_tool_calls / max_model_calls | 正整數有限上限；納入 caption/query/verification/模型式報告的所有呼叫；數值 UNKNOWN |
| max_iterations / per-stage limits | 有限上限與去重策略；數值 UNKNOWN |
| per_call_timeout_s / per_image_timeout_s / batch stop policy | 有限 timeout，包含卡住的工具；數值與安全終止方式待 feasibility |
| max_input_bytes / max_pixels / image resolution | 解碼前後皆驗證；數值 UNKNOWN |
| max_input_tokens / max_output_tokens / total output / memory entries | 分次與總量都有上限；數值 UNKNOWN |
| GPU batch size | 1；批量 sequential |
| GPU process planning ceiling | 6400 MiB；不是 allocator cap 或可用保證 |
| post-estimate free VRAM reserve | 至少 1536 MiB，扣除當下既有佔用及預估 workload 後仍要保留 |

任何必要 limit 未填不得開始執行。未來先在批准的 pilot 定值，正式測試前凍結；不得測試後偷偷調大。

OOM／preflight 失敗：停止該工作、保存錯誤及資源資料、釋放模型；不得 CPU/disk/shared-memory fallback 或無限重試。
Timeout／tool failure：保存已完成 observations，報告 partial/failed 及理由；不能把 partial 當完整成功。硬體失敗或資源釋放未確認則停止後續批次。
Budget exhaustion：禁止新模型呼叫，可用已保存資料生成非模型式 partial report；REPORT 本身須預留預算。
Unsupported detect/point：關閉該能力並記錄，核心 query 可走已凍結路徑；禁止臨時安裝另一大模型。
錯誤輸入可按固定 batch policy 逐張記錄後續處理；錯誤／timeout／空輸出全部列入分母。fallback、retry、重跑都需明列並計成本。
Windows shared memory 的實際使用須未來監測驗證；文件與 preflight 不能保證 OS 絕不使用它。

## 6. Model adapter 與 GPU safety

- 一次一個 heavyweight model；重用同一已載入視覺模型執行多階段，不堆疊多個模型。
- 通過 GpuGuard.preflight 後才 import/allocate heavyweight model；合理估計包含 weights、visual encoder、activations、KV cache、workspace 與框架額外開銷。
- 禁止 device_map="auto"、CPU offload、disk offload、offload folder；禁止把 Windows shared GPU memory 當預算。
- 使用 inference mode；解析度、token、tool calls 增加的峰值需真機測，不能以權重大小代替完整 VRAM。
- 6400 MiB 與 1536 MiB 同時適用，桌面佔用額外扣除；實際可容許工作量通常小於 process ceiling。
- 模型下載、GPU 工作、remote code 執行均需相應授權。revision pin、license／attribution 與程式碼審核要留證據。
- 選定 revision 與既有依賴不相容時先報告，不擅自升級整個環境或換研究硬體。
- 若 Moondream2 有實證 blocker，依 RD-001 提出模型替換；保持 same-model baseline、RQ 及 Agent 方向不變。

## 7. Evaluation requirement

最低 A single-pass、B multistage without verification、C fixed-query with verification、D full adaptive bounded agent；四組固定相同模型與資料。
B/D 驗證對照、C/D 查詢策略對照、A/D 整體系統對照，詳 [protocol v0.3](EXPERIMENT_PROTOCOL.md)。

完整性、錯誤／hallucination 及成本必須共同呈現。Salient recall、object precision、CHAIR、人評等是候選，不是已凍結的主要指標。
不得用舊分類 AURC 證明 caption 品質，不以同一模型自評當獨立 ground truth，不用空白／超短輸出假造零幻覺。
正式資料集、樣本數、annotation、中文映射、主要指標、門檻及統計方案 UNKNOWN，正式 test 前另行 freeze。

## 8. Data, integrity and reproducibility

資料按標註能否支援 claims/物件／caption 評估選取，不能讓 Pet/DTD 自動支配主線。COCO 類資料僅為來源與方法學示例，尚未選定或取得。
記錄使用權、PII／敏感內容、版本、split、hash、相關／近重複、foundation pretraining overlap UNKNOWN。分開 development/pilot、validation、test；不得拿 test 改 prompt、query、verifier、模型或 stopping。

每 run 保存 run ID、commit/dirty state（無 commit 明示）、dependency versions、model/code revision、dataset version/manifest/hash、input IDs、prompt/template revision、agent configuration、stop policy、seed（適用）、每圖結果／工具 trace／errors、latency、peak VRAM。
保留原始輸出、修正歷程與全部失敗。合成 fixtures 只作測試、不得冒充實驗。Negative/null 結果與 post-hoc 改動版本均保存。
AI 使用紀錄包含工具、日期、任務、生成內容與人工核驗；引用與授權以官方／原始來源查證。學校／教授／投稿及人評的審查需求仍 UNKNOWN。

## 9. Engineering and reports（未來實作規範）

分離 models、agent、tools、evaluation、datasets、reporting、safety 職責；既有程式目前不重構。
採小模組、typed interfaces、明確單位／輸入輸出、unit/integration tests、硬體驗證與可重現指令。
拒絕 giant file、hidden state/prompts/thresholds、重複常數、notebook-only pipeline。

正式中文報告、表格／圖以版本化程式從真實 artifacts 產生；保留底層數據、run/protocol/config來源及重製命令。
軸、單位、樣本數、排除／失敗分母、誤差棒定義、圖說一致；色盲／灰階可辨，在投稿尺寸檢查裁切與字體。不得為好看修改測量值。
不能提交資料、權重、secrets、cache 或原始 runs；保留 Git 外備份。只在權利查核及發布授權後公開可散布摘要。

## 10. Acceptance 與 phase gates

工程驗收：A–D 可執行、主流程離線、有限終止、繁中報告／trace、明確錯誤、禁止 offload、GPU 安全、單元／整合測試及授權後真機記錄。
科學驗收：有完整、可追溯的公平比較與限制說明；不要求虛構正向改善。量化品質門檻尚 UNKNOWN，不能提前宣稱達標。
實作、下載／GPU pilot、正式 evaluation、release 各需對應明確授權；本次全部未啟動。
時程依 [DELIVERY_PLAN](DELIVERY_PLAN.md)：2026-10-31 code、2026-11 experiments、2026-12-31 draft。
