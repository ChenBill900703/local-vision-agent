# Research Direction Decision — RD-001

- Decision ID：RD-001
- Date：2026-09-27
- Status：USER-CONFIRMED / FROZEN
- Evidence：使用者於 2026-09-27 提供的「研究方向最終校正與凍結」完整指示。
- Responsible confirmer：使用者。指導教授／學校／投稿單位核准仍 UNKNOWN。
- Phase：DOCUMENTATION ONLY；本決策不是實作、下載、GPU 工作或發布授權。

## Decision

The master's thesis core is a fully local agentic image-understanding system running on an RTX 3070 Ti 8GB, with Moondream2 as the primary candidate vision model.

在 RTX 3070 Ti 8GB 消費級 GPU 上，設計、實作與評估完全本地執行的影像理解／影像辨識 Agent。以輕量視覺語言模型進行多階段分析、工具調度與結果驗證，研究相較單次影像描述的資訊完整性、hallucination／可靠性與資源成本。改善是待檢驗的假設，不是保證。

英文工作題目：**Design and Evaluation of a Local Agentic Image Understanding System on an 8GB Consumer GPU**。
題名可依教授要求調整措辭，但不因此改變研究內容。

## Frozen boundaries

| 項目 | 決策 |
|---|---|
| 主研究環境 | RTX 3070 Ti 8GB、Intel Core i7-11700K、32GB RAM、Windows、既有 Python 3.11 環境 |
| 視覺核心 | Moondream2：primary candidate / proposed main model / pending hardware validation |
| Runtime cloud LLM | Not allowed；不得依賴 OpenAI API、GPT API、雲端 LLM、Astra Runtime 或線上模型服務完成主要分析 |
| GPT-6 Astra | Development assistant only；開發、文獻、除錯、真實結果分析與論文協助須留 AI 使用紀錄 |
| 核心比較 | Same-model single-pass vs local multi-stage agent |
| 核心關注 | Completeness、observable hallucination / reliability、resource trade-offs |
| Agent | 有限狀態、有限工具、有限迭代的 bounded workflow；不要求另一個 LLM controller |
| 核心功能 | Caption、visual query/VQA、object/detail verification、observation memory、uncertainty、stopping、繁體中文結構報告 |
| 條件功能 | Detect、point/grounding：僅在選定 revision 正式支援且通過硬體驗證時啟用 |
| 舊分類主線 | SUPERSEDED；不得作為新主線的必做依賴或退路 |
| 時程目標 | 2026-10-31 核心程式、2026-11 正式實驗、2026-12-31 論文初稿；非完工或錄取保證 |

CPU 可處理正常的檔案解碼、控制流程與報告，但不得以 CPU／disk／Windows shared GPU memory 承接放不進 GPU 的模型權重、張量或 KV cache。既有 GPU 安全規範全部保留。外部硬體只能是另行批准的附加比較，不能取代主研究環境。

## Frozen research questions

1. **RQ1**：在 RTX 3070 Ti 8GB 上，輕量 VLM 是否能作為完全本地影像理解 Agent 的可行視覺核心？
2. **RQ2**：相較於單次 VLM Caption，多階段分析是否提高描述／理解的資訊完整性及重要視覺資訊涵蓋程度？
3. **RQ3**：加入 verification 是否降低明顯 hallucination、錯誤物件描述或未經驗證的視覺敘述？
4. **RQ4**：上述品質變化與 latency、peak VRAM、inference calls、computation cost 有何 trade-off？

Null、negative、無顯著改善都可構成有效結果。不得保證完全理解、涵蓋所有物件、零幻覺、發表或畢業。

## Fixed architecture and comparison

Image → Local Vision Agent → Lightweight VLM → Multi-stage visual analysis → Verification → Structured Traditional Chinese Report。

基本流程：START → INITIAL_CAPTION → SCENE_ANALYSIS → OBJECT_CHECK → DETAIL_QUERY → VERIFICATION → REPORT → STOP。
只有明確條件成立才能追加 query；工具次數、迭代、timeout、輸出、影像解析度均須有上限。

A：same-model single-pass；B：multi-stage without verification；C：fixed-query agent；D：full verification + adaptive bounded query。
B 與 D 的 verification 對照、C 與 D 的固定／自適應對照，詳見 [實驗提案](EXPERIMENT_PROTOCOL.md)。

## Superseded and excluded

Pet/DTD 分類、DINOv2-Small linear classifier、ResNet18、temperature scaling、selective classification、classification abstention、classification AURC primary metric 均屬歷史方案，不再是 thesis core。
原始文件保留於 [歷史快照](archive/2026-09-27-pre-RD-001/INDEX.md)；既有程式／設定不刪除，本次只在文件標為 LEGACY。附加分類實驗仍需使用者另行確認。

第一版不做大型 multi-agent debate、任意網路搜尋、cloud orchestration、video、image generation、大型 OCR、segmentation、foundation model training、大規模 VLM fine-tuning、任意聊天。
Moondream3／3.1 與其他較大模型僅屬 related/future work 或另行批准的 optional feasibility comparison，非必要交付。

## Change control

RD-001 是本 repository 最高層級的**研究方向決策紀錄**，不改變系統／開發者指令優先序；其他 active 文件必須與它一致。

- AI 不得因實作困難、既有程式投入、追逐新模型或「另一題較容易」自行改題。
- 任何方向變更只能先提出 PROPOSAL，列明原方向、建議變更、理由、成本及影響。
- 僅收到使用者明確「批准變更研究方向」才可修改 RD-001；保留日期、版本、理由與核准證據。
- 若 Moondream2 feasibility 出現無法排除的 blocker，可提出有證據的視覺模型替換決策，取得使用者確認後更新模型紀錄及 same-model baseline；**不得更換 RQ、8GB 主硬體或 Agent 架構方向**。
- 文件方向凍結不等於實驗 protocol 凍結，不代表模型選定、顯存量測完成或機構核准。
- exact revision、授權適用性、Windows 相容性、實測 VRAM、中文能力、資料集、指標／門檻與機構要求仍須驗證。

Active requirements：[v2.0](REQUIREMENTS.md)。唯一 active 時程：[DELIVERY_PLAN](DELIVERY_PLAN.md)。
