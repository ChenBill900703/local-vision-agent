# 本地環境與安全驗證

## 2026-09-27 repair1 最新補充

續行修復後，原套件未變；新增 Windows Job／pipe IPC 工程測試，全套 68 項 CPU tests 通過。
一次 GPU 對照確認 cuBLAS 清理將 allocated 8,519,680 bytes 降為 0，最終 reserved 亦為 0。
supervisor 正常退出，job 無殘留；device 回到 used/free 182/7836 MiB。
英文 query 通過本圖，中文原版／單 suffix 皆重複問題。整體 CONDITIONAL PASS，完整繁中能力未驗收。
詳 [repair1 結果](PHASE2_REPAIR1_RESULT.md)；以下首次 Phase 2／Phase 1 區段為歷史。

## 2026-09-27 Phase 2 最新結果

使用者另外批准有限 CUDA／模型取得／單次 GPU pilot。未新增或升級依賴。
RTX 3070 Ti 8192 MiB、driver 591.86、torch 2.7.1+cu126；固定模型真實載入成功。
整體驗收 FAIL：中文 query、allocator 清理及 Windows supervisor 尚有 blocker。
程序退出後 dedicated used/free 回到 182/7836 MiB；shared attribution UNKNOWN。
59 項 CPU tests 通過，3 個 pilot modules strict Mypy 通過。
完整數據／來源／套件版本見 [GPU 報告](MOONDREAM2_GPU_FEASIBILITY_REPORT.md)。
下方 Phase 1 與舊分類相容性記錄皆為歷史；不能當成目前模型需求。

## 2026-09-27 Phase 1 最新補充

使用者批准 CPU/mock 工程測試，沒有批准安裝／升級／下載或 GPU 工作。
既有 Python 3.11.9、Pillow 12.3.0、Ruff 0.16.8、Mypy 1.20.2 可用。
僅查套件 metadata：torch 2.7.1+cu126、transformers 4.57.6；未匯入或初始化它們。
accelerate、einops、pyvips、pyvips-binary 均 **MISSING**；未自行補裝。
CPU/mock 測試与限制見 [PHASE1_RECORD](PHASE1_RECORD.md)。未執行 verify_environment.py、nvidia-smi 或 CUDA API。
以下 2026-09-22 與較早的 2026-09-27 敘述是歷史紀錄；Phase 1 授權取代本回合 documentation-only 限制，不授權 GPU feasibility。

## 授權與範圍

2026-09-22：使用者授權在專案 venv 安裝並固定研究套件、補強安全檢查。
未授權模型／資料下載、GPU 訓練／推論／效能測試或 GitHub 發布。
本次驗證是工程檢查，不是論文實驗資料。

## 固定環境

- Windows x64、專案 Python 3.11.9。系統 Python 3.12 不用來執行此環境。
- PyTorch 2.7.1+cu126、Torchvision 0.22.1+cu126：
  選用官方已發布的匹配組合，不宣稱是最新版本。
  官方來源：https://pytorch.org/get-started/previous-versions/
- Transformers 4.57.6：後續 DINOv2 模型介接；不啟用遠端自訂程式碼。
- NumPy、SciPy、scikit-learn：數值計算、校準、統計及指標。
- Pandas：逐樣本結果與報表；Pillow：圖片讀取與預處理。
- Matplotlib：正式圖表；tqdm：執行進度；Safetensors：安全格式權重介接。
- Ruff、Mypy、Pytest、pytest-cov：格式、型別、測試及覆蓋率。

完整直接與間接版本在根目錄 requirements-win-cu126.lock。
pyproject.toml 的 extras 記錄需求範圍；重現安裝以 lock 為準，不重新解析最新版本。
lock 固定版本，但尚不是含所有 wheel SHA256 的封存檔；乾淨機器重建尚未驗證。
未安裝 CUDA Toolkit、音訊、LLM Agent、量化或 offload 框架。
不自動更新套件；日後安全更新需要記錄版本變動並重新驗證。

## 使用與重建

既有專案環境直接使用以下明確路徑，不必更改系統 PATH：

```powershell
.\.venv\Scripts\python.exe -m pip check
.\.venv\Scripts\python.exe -B scripts/verify_environment.py
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

重建時先準備 64 位元 Python 3.11 的專案 .venv，取得安裝授權後執行：

```powershell
.\scripts\install_environment.ps1
```

腳本只安裝到專案 .venv，逐步檢查退出碼；不下載模型、不呼叫 CUDA。
安裝不是原子交易，中途失敗需修復／重建環境，不可視為完整完成。
不要將 .venv、pip 快取或第三方套件複製進 Git。

## 安全補強與限制

本次新增測試涵蓋：

- 顯存數值只接受合法整數；拒絕 bool、NaN、無窮大及負值。
- 快照基本一致性、查詢 GPU 與載入 device_map 的一致性。
- 巢狀 quantization_config 的 offload 阻擋；無法檢查的物件直接拒絕。
- nvidia-smi 缺失、逾時、空輸出或 N/A 轉為明確安全錯誤。

目前 GpuGuard 仍是載入前條件與外部量測值的檢查器，並非 GPU 記憶體管理器。
現有 6400 MiB 上限與額外 1536 MiB 餘裕不等於驅動硬限制。
尚需在未來模型介接階段完成並測試：受控工作程序、同時只載入一個模型、
allocator 限制、參數／buffer 實際裝置檢查、輸入限制、OOM 清理與退出。
此文件不得被解讀成「已保證不使用 Windows 共享顯存」。
其他既有路由／評估問題不屬於本次環境安裝，尚未修復。

## 驗證紀錄

- 27 項 CPU 單元測試通過；GPU 查詢使用模擬，不構成真機峰值證據。
- verify_environment.py 通過：CPU tensor、Torchvision NMS、圖片轉換、
  DINOv2 類別匯入、資料表與記憶體中的 PNG 產生。
- 驗證前後 torch.cuda.is_initialized() 均為 False。
- 沒有下載權重，沒有建立或訓練模型。
- 中文字型選擇、正式排版與圖表視覺驗收仍待報告功能實作。

## 授權與 AI 協作

依賴的授權仍由各上游持有人保留；本專案的 MIT 提案不會覆蓋第三方授權。
目前套件以 BSD、MIT、Apache、PSF、MPL 等授權為主，
發行時需保留適用聲明，尤其不要直接重新包裝 CUDA DLL 或套件 wheel。
本次只安裝使用，未發布或轉授權任何依賴；模型和資料集另行審核。
未執行完整弱點掃描，不能宣稱套件不存在已知安全問題。

本次 Codex 協助安裝、整理版本、修改安全驗證及產生測試；
使用者仍需理解及驗證程式。此紀錄不是學校倫理審查通過證明。


---

## 2026-09-27 RD-001 狀態補充（不更改上述歷史紀錄）

目前研究方向以 [RD-001](RESEARCH_DIRECTION.md) 為準：
Local Agentic Image Understanding on RTX 3070 Ti 8GB；Moondream2 為 proposed primary candidate，尚未 hardware validated。
以上原文中「本次」均指 2026-09-22 環境工作，DINOv2／calibration 的套件用途與驗證屬歷史方案，不是目前必做模型或研究問題。
2026-09-27 本次只做文件校正，沒有重跑 27 項測試、環境驗證、CUDA／GPU 查詢、模型載入或 benchmark。
既有環境也不能視為重灌後已復原；安裝／重建需使用者相應授權。

未來另行批准後才進行 Moondream2 feasibility validation，包含：

- exact weights/code revision、授權及 remote-code 安全審閱。
- Windows／Python 3.11／既有 PyTorch/Transformers 相容性；現有 lock 並非 Moondream2 專用 lock。
- [官方 Transformers 文件](https://docs.moondream.ai/transformers/) 目前列出 accelerate 等前置條件；既有 lock 未含 accelerate，僅比對版本文字不能判定實際相容。本次不補裝、不修改 lock。
- 官方範例的 remote-code 需求與上文舊「不啟用遠端自訂程式碼」歷史紀錄分開：新候選須經批准及固定程式 revision 審核，不表示本次已開啟。禁止複製 device_map="auto"。
- caption/query 核心工具、條件式 detect/point、繁中呈現、斷網執行與有限終止。
- preflight、單一 heavyweight model、6400 MiB 規劃上限與 1536 MiB 額外餘裕、image/token/call limits、OOM/timeout cleanup、實際裝置與 shared-memory 監測。
- 真實 peak VRAM／latency 目前 UNKNOWN；未測前不得以模型參數量或既有 CPU 測試宣稱 8GB 可承擔。

Astra 僅開發助手，runtime 完全本地。安全規範見 [AGENTS](../AGENTS.md)，唯一 active 時程見 [DELIVERY_PLAN](DELIVERY_PLAN.md)。


## 2026-09-28 InternVL3 實測補充

既有環境未安裝、升級或移除套件。Python3.11.9、torch2.7.1+cu126、Transformers4.57.6，driver591.86。固定 InternVL3-2B-Instruct BF16/cuda:0/eager 單一 tile，在一次離線 load 中完成四項英文／繁中查詢，峰值 reserved4688MiB，清理 allocated/reserved0。只代表單張 development fixture 路徑。[完整報告](INTERNVL3_2B_GPU_FEASIBILITY_REPORT.md)。四項後續能力探測因工程 gate 過嚴未執行，CONDITIONAL PASS，停止 GPU 工作。

75 CPU tests／Ruff／strict Mypy21 modules 通過；Windows 命令應設 PYTHONIOENCODING=utf-8，未設定時曾造成既有 CLI 測試的 cp950/UTF-8 解碼失敗。無依賴缺失安裝；受控原始碼明確移除未使用的選用加速 import。不是新版通用環境 lock 或全部影像相容性證明。
