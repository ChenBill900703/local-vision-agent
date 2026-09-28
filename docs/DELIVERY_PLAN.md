# Delivery Plan v2.0 — 唯一 Active Roadmap

日期：2026-09-27。方向：[RD-001](RESEARCH_DIRECTION.md) USER-CONFIRMED / FROZEN。
規格：[REQUIREMENTS v2.0](REQUIREMENTS.md)；評估：[protocol v0.3 PROPOSAL](EXPERIMENT_PROTOCOL.md)。
本文件是計畫，不是授權、實作或完工證據。[ROADMAP](ROADMAP.md) 僅歷史用途。

## 三個目標保持不變

- **2026-10-31**：核心程式功能完成。
- **2026-11-01**：使用者於 Phase 1 指定的工程驗收目標；不是硬體驗證或如期完成保證。
- **2026-11**：正式實驗；須先完成 protocol freeze 及必要核准。
- **2026-12-31**：碩士論文初稿。

若安全／授權／資料或人評準備延遲，據實報告受影響日期與縮減「optional」範圍的提案；不保證準時，不偷跑實驗，也不能擅自改 RQ、硬體或退回分類題目。
投稿、接受、口試另有時程，未指定，不混成 12/31 保證。

## 目前狀態

2026-09-28：InternVL3 受控替換 feasibility **CONDITIONAL PASS — SMALL ENGINEERING BLOCKER**；四項核心真實問答／繁中、離線、預算及清理成功，但工程 gate 過嚴，四項能力探測未執行。本次一次載入額度用完，未整合 Agent。[報告](INTERNVL3_2B_GPU_FEASIBILITY_REPORT.md)；[交接](../SESSION_HANDOFF.md)。10/31／11/1 目標不變，不保證完成。

### 歷史 Moondream2 狀態

**最新 repair1：CONDITIONAL PASS**。清理與 Windows supervisor blocker 已解決並完成真實驗證，英文 query 正確；直接繁中回答仍未通過。本次只再執行一次具名重測，已結束；[修復結果](PHASE2_REPAIR1_RESULT.md)。真實 A–D 整合及語言決策仍待完成，不更改目標日期或研究方向。

### 首次 Phase 2 歷史狀態

**Phase 2 更新：首次授權 pilot 已執行並停止於 blocker（FAIL）**。真實 load/encode/caption 成功，中文 query 未回答；清理與 Windows supervisor 需修正。一次載入額度已用，不自動重試。[完整證據與下一次授權範圍](MOONDREAM2_GPU_FEASIBILITY_REPORT.md)。A–D 真實 adapter 整合尚未開始，10/31／11/1 目標保留但不保證。

### Phase 1 歷史狀態

文件已依 RD-001 校正。Phase 1 已建立 CPU/mock Agent、A–D、繁中報告與安全／失敗測試，見 [實作紀錄](PHASE1_RECORD.md)。Moondream2 尚未介接／hardware validated，正式資料／評估流程未完成。
既有 guard、分類 routing/evaluation、tests、config、CI／lock 是歷史資產，不代表新主線完成。
2026-09-27 使用者已明確批准 Phase 1 實作及 CPU/mock tests；不安裝／升級／下載、不初始化 CUDA／查詢 GPU、不真實推論／訓練／benchmark、不 commit/push。完成本階段即停止；[原文快照](archive/2026-09-27-before-phase1/DELIVERY_PLAN.md) 保留。

## 分階段計畫（原始窗口保留；Phase 2 實際狀態以上方增補為準）

| 目標窗口 | 範圍 | 出口證據／停止條件 |
|---|---|---|
| 至 9/30 | 已獲本次授權；最小契約、CPU/mock 骨架與 feasibility 提案 | PHASE1_RECORD；真實 adapter／GPU 仍待另外批准 |
| 10/1–10/7 | 經另行批准的 Moondream2 acquisition／feasibility | revision/code/license、Windows 相容性、離線／中文與 8GB、安全失敗記錄；不 fit 就停止並報 blocker |
| 10/8–10/18 | adapter、bounded state machine、caption/query、memory、verification、stop、繁中 structured report | 小模組／typed APIs、unit/integration tests、可追溯工具紀錄 |
| 10/19–10/25 | same-model A–D、資料 manifests、評估與 trace-to-report | 對照隔離、失敗分母、圖表重製；mock 不當實驗證據 |
| 10/26–10/31 | 整合與授權後硬體安全驗收、文件／可重現命令 | 核心功能 code target；出具未完成項，不假裝科學結論成立 |
| 2026-11 | protocol 正式凍結後執行正式評估／必要人評 | 全量逐圖證據、A–D公平比較、統計與失敗記錄；受適用審查要求限制 |
| 2026-12–12/31 | 真實結果分析、中文版論文／圖表、限制、重製與來源檢查 | 初稿，不保證接受／畢業；發布需另行授權 |

日期是工作配置提案，不能跳過 implementation → feasibility/pilot → formal evaluation → release 的 phase gates。
文獻整理、合規需求查證與資料設計可在授權範圍內與工程準備並行；不得偷偷先看 test 調整設計。

## 最小交付與 scope control

1. 本地 Moondream2 candidate adapter 與同模型 single-pass baseline（硬體驗證後才稱選定）。
2. B/C/D bounded workflow：明確 query triggers、驗證、停止、錯誤及觀察 trace。
3. 單張／逐張批量、繁中結構報告；不要求聊天 UI 或大網站。
4. 可重現 evaluation／resource measurement／中文圖表，版本化 protocol／manifests／AI assistance 記錄。
5. 安全及單元／整合測試、正式實驗的授權後硬體證據；GitHub-ready，不自行 push。

Detect/point/grounding 僅條件能力；優先關閉未支援的 optional capability，不自行擴大模型堆疊。
Moondream3／3.1、舊分類二級實驗、額外 GUI、額外消融都不是必要交付。
任何必需功能受 blocker 影響需提報，不可以把繁中報告、A–D、公平比較或 GPU 安全默默刪掉。

## 風險與回應

| 風險 | 必要回應 |
|---|---|
| Moondream2 相容性／VRAM／中文未達標 | 保存證據、停止不安全路徑；在 RD-001 內提模型／呈現方案變更確認，不改題 |
| 校方／教授／人評要求尚未確認 | 研究者向實際單位確認；不得 AI 代簽或宣告豁免 |
| 資料無合適物件／caption 標註 | 正式 test 前完善資料與評分設計，不以換有利指標救結果 |
| 四組成本／輸出長度不公平 | 統一條件並完整報成本與長度；不把多次推論說成免費改善 |
| 時程不足 | 先停 optional；必要項如仍受影響，報告時程風險請使用者決定，不自主換題 |
