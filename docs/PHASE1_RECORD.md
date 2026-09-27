# Phase 1 工程紀錄 — 2026-09-27

範圍：最小工程骨架與可行性驗證準備。RD-001 未更改；未進入下載、GPU feasibility 或正式評估。
授權者：使用者；證據為本 chat 2026-09-27「請開始本專案第一階段」訊息，明確允許程式／設定／測試／文件與無 CUDA、無模型下載的 CPU 測試。合理工程細節由 Codex 決定，非使用者逐項批准數值，亦非教授／機構核准。

## 閱讀、保留及修改

完整閱讀 AGENTS、README、RESEARCH_DIRECTION、REQUIREMENTS、EXPERIMENT_PROTOCOL、DELIVERY_PLAN、ENVIRONMENT；檢查既有四個 core 檔案、三份 tests、模型設定、pyproject、check script、ignore 及 Git 狀態。
初始 Git 狀態所有既有檔案皆 untracked，不能用空 diff 宣稱沒有修改。未 reset、commit、push、清理或刪除使用者檔案。
舊分類 modules/tests、GpuGuard、依賴 lock、pyproject、scripts、CI、RD-001 保持原樣。

- 新增七個模組：contracts、image_input、agent、mock_adapter、tool_executor、reporting、mock_cli。
- 新增 `configs/agent_mock.toml`；必要限制全部明列，缺漏拒絕執行；新 loader 拒絕舊模型設定。
- `configs/models.toml` 關閉全部模型，新增 LEGACY 說明；原始 bytes 保存在階段前快照。
- 新增 `tests/test_agent.py`，25 項測試；保留並重跑原有 27 項純 CPU 測試。
- 更新 AGENTS/README/REQUIREMENTS/EXPERIMENT_PROTOCOL/DELIVERY_PLAN/ENVIRONMENT 的阶段與授權；原文先快照。新增 ENGINEERING_CONTRACT、MOONDREAM2_FEASIBILITY 與本紀錄。
- 保留 10/31 核心程式、11 月實驗、12/31 初稿目標，補記本次指定 11/1 工程驗收；均非完成保證。

## 最終驗證

環境：既有 Windows Python 3.11.9；未安裝／升級。執行命令在 ENGINEERING_CONTRACT。

| 檢查 | 實際結果 |
|---|---|
| `python -B -m unittest discover -s tests -v` | **52 tests，OK，exit 0**；最後一次輸出 1.990 秒，僅測試耗時，不是模型 benchmark |
| Ruff check 七個新 source files + 新 test file | **All checks passed，exit 0** |
| Mypy `--strict` 七個新 source files | **Success: no issues found in 7 source files，exit 0** |
| 新入口 import 檢查 | 子程序確認無 torch、transformers、torchvision、legacy routing/evaluation 匯入 |
| Windows spawn timeout 整合測試 | 故意讓 mock 等待 30 秒；0.3 秒 deadline 中止 worker，active children 集合恢復，測試通過 |
| Git 最終清單 | 仍 untracked；本次新增檔皆程式／設定／測試／文件／歷史快照；未產生待提交的資料、權重或 runs |

覆蓋：A 一次回應；B/D 調查軌跡相同；C 固定與 D 自適應分支；detail-only trigger；固定去重／無新證據停止；partial verification 保留未檢查 claim；每張 memory reset；claims 與 evidence IDs；supported/contradicted/unresolved；malformed/empty/oversized output；全部必要 limits 的合法性與缺漏；工具／模型／迭代／記憶／輸出上限；兩層 deadline；工具失敗／unsupported／cleanup failure；batch 停止／錯圖繼續；PNG/JPEG／尺寸／損壞／缺檔；CLI、JSON 與繁中報告。
cleanup failure 分支使用注入錯誤測試，沒有故意製造無法終止的 OS process。歷史 GpuGuard 測試使用合成快照與 subprocess mock，沒有真實 NVIDIA 查詢。
首輪 49 tests 已過；新增三項邊界測試及格式修正後以 52 tests 為最終紀錄。未對歷史程式擴大重構或將其靜態檢查問題混成本次需求。

## 真實工程功能與 mock 邊界

真實已執行驗證的是：設定拒絕／圖片 CPU 解碼與 hash、有限控制流程、記憶與 linkage、失敗與停止、子程序終止、A–D 介面、繁中固定報告格式與 JSON。
所有 caption、場景／物件／細節、verification verdict、output token 數均來自 **mock scripted fixtures**；synthetic 8×8 測試圖片與這些語意沒有關聯。沒有真實影像辨識、模型品質或論文結果。
Report 一律標 MOCK_NOT_RESEARCH_EVIDENCE；model latency/VRAM 為 null。Astra 只生成／檢查程式及文件，不在 runtime。

## 未完成與限制

1. 真實 Moondream adapter／schema normalization／claim extraction、tokenizer、繁中內容與 offline 能力尚未驗證。
2. 工具程序 timeout 已測；per-image 是調度 deadline，未硬中斷主程序 I/O／Pillow／報告。現行每工具 spawn 只適用 mock；下一階段需單模型長駐受控 worker 及完整 GPU 清理，不可直接拿來測量正式推論。
3. GPU preflight integration、allocator/runtime placement、OOM handling、shared-memory 監測與硬體 VRAM／速度未實作／未驗證。6400 MiB + 1536 MiB 只是安全規劃規則。
4. 既有環境缺 accelerate、einops、pyvips、pyvips-binary；其中 pyvips 有上游 Pillow 路徑，是否採用待版本化審核，不能據缺套件直接宣稱模型無法運作。
5. 官方固定版另引用未固定的 starmie-v1 tokenizer，候選 SHA 已查到但權利／本地解析未完成；remote-code 完整審閱未完成。
6. 正式資料、manifests、metrics、thresholds、評分詞彙、人評／機構與投稿規定仍未凍結。沒有任何研究改善、倫理豁免或發布核准證據。

## 下一階段許可及停止

[MOONDREAM2_FEASIBILITY](MOONDREAM2_FEASIBILITY.md) 已列可審閱提案：固定模型／tokenizer 候選、license／imports、缺依賴、最多 5 GB 下載／12 GB 磁碟、至多 3 張使用者有權 development 圖、明確 call/token/image/timeout budgets、GPU preflight／單模型／no offload、離線／繁中／OOM/timeout evidence。
下載、依賴安裝、已審閱 remote code 執行、GPU 查詢／CUDA／有限推論須後續各自明確批准。formal evaluation／release 另有 gate。
本階段到此停止；未安裝／升級、未下載模型／資料、未查詢 GPU／初始化 CUDA、未真實推論／訓練／benchmark、未 commit/push／發布。

## AI 協作與人工核驗

Codex／GPT-6 Astra（development assistant）於 2026-09-27 協助讀取文件、設計工程契約、產生上述新程式／測試／文件、查閱官方來源、執行 CPU tests/Ruff/Mypy、解釋限制。
工具：本機檔案編輯、唯讀 Git、既有 Python CPU 測試／靜態檢查、web 官方文字查核；未使用雲端模型作系統 runtime 或 judge。
一般本機執行 sandbox 起初未能啟動，經工具審核後使用已授權的工作目錄操作；未改全域 Git safe.directory，只在唯讀 Git 命令加單次路徑設定。
人工理解、程式／來源核驗及研究者簽認 **待完成**；自動測試通過不取代人工審查、學校審查或研究證據。
