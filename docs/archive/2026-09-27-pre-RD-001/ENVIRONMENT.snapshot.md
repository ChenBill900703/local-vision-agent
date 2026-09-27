# SUPERSEDED snapshot — 2026-09-27 before RD-001

Historical record only; not active instructions, requirements or execution authorization.
Original path: `docs/ENVIRONMENT.md`. Original text follows unchanged (line endings may be normalized).
Active direction: [RD-001](../../RESEARCH_DIRECTION.md).

---

# 本地環境與安全驗證

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
