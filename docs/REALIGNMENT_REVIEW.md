# Research Direction Realignment & Freeze — Review Report

日期：2026-09-27。依使用者本次完整校正指示執行，決策：[RD-001](RESEARCH_DIRECTION.md)。
範圍：完整閱讀八份指定文件、官方／論文來源查核、文件修改、唯讀一致性與檔案比對。
**NO SOURCE CODE CHANGES**。本報告不是程式驗收、硬體驗證或正式實驗結果。

## A. Research direction

1. 正式主線為 Local Agentic Image Understanding on RTX 3070 Ti 8GB。
2. 主硬體固定 RTX 3070 Ti、i7-11700K、32GB RAM、Windows／Python 3.11。
3. Moondream2 是主要候選，exact revision／相容性／中文／VRAM 尚待驗證。
4. Runtime 完全本地；GPT-6 Astra 僅為 development assistant。
5. 採有限狀態、有限工具、有限迭代的多階段 caption/query/verification Agent。
6. 同模型 A single-pass、B 無驗證、C 固定查詢、D 完整自適應＋驗證，輸出繁中結構報告。
7. 研究完整性、observable hallucination／可靠性及資源 trade-off；正向、null、negative 都如實保留。
8. 方向 USER-CONFIRMED / FROZEN；protocol 仍 PROPOSAL，實作與實驗尚未授權。

## B. Files changed

| 檔案 | 校正理由 |
|---|---|
| [AGENTS.md](../AGENTS.md) | 換成 RD-001 的 outcome／scope／phase gates，保留安全、學倫、追溯、品質與圖表規範 |
| [README.md](../README.md) | 新研究、排除範圍、runtime、硬體、決策登錄與真實未完成狀態；揭露 legacy config |
| [REQUIREMENTS.md](REQUIREMENTS.md) | v2.0；重寫 Agent／工具／輸入輸出／資源上限／失敗與驗收契約 |
| [EXPERIMENT_PROTOCOL.md](EXPERIMENT_PROTOCOL.md) | v0.3 PROPOSAL；A–D 對照、公平性、指標適用、資料及中文／人評界線 |
| [DELIVERY_PLAN.md](DELIVERY_PLAN.md) | v2.0 唯一 active roadmap；保留 10/31、11 月、12/31 三目標 |
| [RESEARCH_SOURCES.md](RESEARCH_SOURCES.md) | 主線改為本地 VLM、caption/VQA、visual agents、CHAIR／幻覺、grounding／verification 原始來源 |
| [ENVIRONMENT.md](ENVIRONMENT.md) | 只追加 RD-001 與未來 feasibility，原有驗證記錄完整保留 |
| [ROADMAP.md](ROADMAP.md) | 更新歷史標頭、指向 RD-001；舊計畫本文不變，不作 active roadmap |
| [RESEARCH_DIRECTION.md](RESEARCH_DIRECTION.md)（新增） | RD-001、FROZEN 決策及方向／模型變更控制 |
| [archive/2026-09-27-pre-RD-001](archive/2026-09-27-pre-RD-001/INDEX.md)（新增） | 八份校正前快照＋INDEX，保留歷史而非抹除舊方向 |
| REALIGNMENT_REVIEW.md（本檔，新增） | 保存本次 A–G 校正報告與檢查範圍 |

使用者清單寫 ROADMAP.md；實際檔案是 docs/ROADMAP.md，根目錄無該檔。本次審閱／修正實際檔，不建立第二份 roadmap。

## C. Superseded content

- Pet/DTD 分類不再是論文主題；DINOv2-Small linear classifier、ResNet18 不再是必做主模型。
- Temperature scaling／calibration、selective classification、classification abstention、classification AURC 不再是主要研究問題或主要指標。
- 舊 classification routing/evaluation、模型設定與文獻保留為 LEGACY／SUPERSEDED；附加測試需使用者後續確認，不自行加入新主線。
- 舊「禁止 query/detection」範圍不再適用；query/VQA 是核心，detect/point/grounding 僅為有條件能力。
- 舊階段時程與 LLM 決策方案只保留歷史用途，不覆蓋新文件。

## D. Preserved safeguards

- GPU：單一 heavyweight model、load 前 preflight、6400 MiB 規劃上限＋預估使用後 1536 MiB free reserve、batch1、解析度／tokens／calls／iterations／timeout 有界、OOM safe fail。
- 禁止 device_map="auto"、CPU/disk offload、Windows shared GPU memory 作 fallback；不把 preflight 說成 allocator cap 或「絕不 spill」保證。
- 未量測標 UNKNOWN/unmeasured；未完成不得寫 completed。下載、GPU pilot、正式實驗與 release 需各自授權。
- 不 test 調參、不 cherry-pick、不捏造數據／引用／顯著性／核准；保留失敗、negative/null 及 post-hoc amendments。
- 保存 run/commit/dirty state、依賴、model/data revisions、manifests/hash、input IDs、prompts、agent config、stop policy、seed、逐圖結果／trace／failure／latency／VRAM。
- 模組分離、typed interfaces、未來 unit/integration/hardware tests、trace-to-table/figure、中文報告、可再製圖表、AI assistance 紀錄與人工核驗。
- 適用授權／倫理／學校／投稿要求需證據，不因公開資料就自行宣告豁免。

## E. Remaining UNKNOWN

| 未知項目 | 下一階段必要證據 |
|---|---|
| Moondream2 exact revision／artifact license／remote code | immutable weights/code pin、適用授權與安全審核 |
| Windows／現有 PyTorch/Transformers 相容性 | 經批准的實際載入／工具測試；既有 lock 尚未含 accelerate，不代表相容已成立 |
| Peak VRAM、latency、無 offload／shared-memory 行為 | 指定主硬體與真實工作量測；現在無結果 |
| 繁中生成／本地轉換與其成本、各工具能力 | 統一語言流程、功能／品質檢查；detect/point 不保證可用 |
| Dataset／version／split／counts／rights | 適用標註、獨立真值、manifest、duplicate checks、授權來源 |
| Primary metric／threshold／人評／統計／limits 數值 | test 前正式 protocol freeze；A–D 對照方向已固定 |
| Novelty／教授核准／學校審查／投稿規則 | 實際指導教授、崑山科技大學資工系研究所與目標會議的證據 |
| 10/31 能否完成 | 取決於實作授權、feasibility 與後續進度；日期是目標，不是保證 |

Moondream2 官方面向與 API 來源已登錄，不等於本機驗證。見 [官方 model card](https://huggingface.co/vikhyatk/moondream2)、
[官方 Transformers 文件](https://docs.moondream.ai/transformers/) 及 [來源適用界線](RESEARCH_SOURCES.md)。

## F. Consistency audit

狀態只針對文件；PASS 不表示功能已可執行。完整閱讀／前後文本比對加上關鍵詞巡查，歷史內容按明確標示排除為 active requirements。

| 檢查 | 結果 | 說明 |
|---|---|---|
| AURC 仍是 thesis primary metric？ | PASS | active 主線已移除，只留 superseded 警示／歷史 |
| Calibration 仍是 primary RQ？ | PASS | 改成固定 RQ1–4 |
| DINOv2/ResNet18 仍是必做主模型？ | PASS | 文件明列 LEGACY，不是新需求 |
| Pet/DTD classification 仍主導論文？ | PASS | 歷史／另行確認的 secondary |
| 禁止 Query/Detect 又要求使用？ | PASS | Query 核心、Detect/Point 有條件；舊禁令明示失效 |
| 要求額外 LLM controller？ | PASS | 有限狀態控制足夠 |
| GPT/Astra 被當成 runtime？ | PASS | 明確 development-only，禁止雲端 runtime 依賴 |
| Deadline 衝突？ | PASS | active 統一 2026-10-31／2026-11／2026-12-31 |
| Proposal 寫成 completed？ | PASS | 方向凍結與工程／實驗完成分開 |
| 未測 VRAM 寫成 measured？ | PASS | 全部保留 UNKNOWN／unmeasured |
| Moondream2 寫成 hardware validated？ | PASS | 明確 pending |
| 兩份 active roadmap？ | PASS | 僅 DELIVERY_PLAN；ROADMAP 標歷史 |
| 所有 active 文件同一方向？ | PASS | 指向 RD-001；ENVIRONMENT 追加現況，不竄改歷史 |
| 舊設定的實際停用／新功能完成？ | WARNING | configs/models.toml 舊模型 enabled=true 原樣保留；文件警告不等於程式停用 |
| 正式實驗／8GB 可行性可啟動？ | WARNING | UNKNOWN 與 phase gates 尚未完成；本次未授權或實測 |
| Git diff 能完整證明文件變動？ | WARNING | 原檔均未追蹤，git diff 空白不代表沒修改；採快照與內容／雜湊比對 |

未發現尚未處理的 active 文件方向衝突；未將上述 WARNING 偽裝成已修好。
確認原八份文件快照保留完整本文（換行正規化），ENVIRONMENT 原文保留，ROADMAP 歷史主體保留。
Active 文件及 archive INDEX 的本地 Markdown 連結均檢查存在；snapshot 裡原有相對連結保留歷史語境，不列為 active 連結驗收。
本次沒有執行 unit/integration tests、安裝、模型／dataset 下載、CUDA、推論、訓練或 benchmark。

## G. Git diff summary / 實際操作摘要

| 操作 | 數量／範圍 |
|---|---|
| 修改既有文件 | 8：AGENTS、README、REQUIREMENTS、EXPERIMENT_PROTOCOL、DELIVERY_PLAN、RESEARCH_SOURCES、ENVIRONMENT、docs/ROADMAP |
| 新增文件 | 11：RD-001 文件、本報告、8 份 snapshots、1 份 archive INDEX |
| 刪除 | 0 |
| Source / tests / scripts / config / lock / CI 等非文件 | 0 變更；前後 16 個非文件檔案 SHA256 相同 |
| 專案測試／GPU 工作 | 未執行 |
| Git commit／push／history rewrite | 未執行 |

Git ls-files 為空，git status 將原始及新檔案都列為 untracked。
因此這裡的 modified/added 是相對本次操作前的檔案快照，而不是冒稱 Git 已提供 tracked diff。
git diff --stat／--check 為空只能描述 Git 現況，不能作為完整驗收證據；歷史快照與前後內容／雜湊比對才是本次依據。

**NO SOURCE CODE CHANGES**。只完成研究方向文件校正與凍結；不開始實作。

## AI assistance record（本次）

Codex 協助完整文件閱讀、官方／原論文索引查核、RD-001 文件同步、歷史快照及一致性審閱；
產出均為研究規範／提案而非實驗數據。確認依據為使用者 2026-09-27 指示。
本次未聲稱使用者、教授或學校已人工驗收此文件；研究作者仍需確認內容與後續正式 protocol。
