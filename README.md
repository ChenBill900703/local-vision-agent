# Local Vision Agent：本地影像理解 Agent

這是一個在 Windows 電腦上執行的研究原型。使用者選擇圖片後，系統會用本機的小型視覺語言模型，先描述圖片，再依需要補問問題、檢查敘述，最後產生繁體中文報告。另有 Webcam 連續拍攝單張影像的介面。

**目前狀態：已凍結，作為備用研究專案保存。** 程式與 CPU 測試已完成；最後檢查時 Qt 找不到攝影機，因此實體 Webcam 與持續多張圖片的 CUDA 路徑仍未完成驗證。這個限制有完整保留，沒有把未測試項目寫成成功。

> 本儲存庫為私人備份。包含程式、測試、文件、提交歷史及凍結 tag；不包含模型權重、私人照片、Webcam 影像、虛擬環境或原始私密執行紀錄。

## 先看哪裡？

- 想快速知道做過什麼、為什麼停止：看[開發過程與結果](docs/DEVELOPMENT_HISTORY_ZH_TW.md)。
- 要交給下一位工程師或 AI：先讀 [NEXT_AI_START_HERE](docs/NEXT_AI_START_HERE.md)。
- 要了解如何啟動、測試、匯出：[操作手冊](docs/PROJECT_RUNBOOK.md)。
- 要確認最後的實際結果：[最終驗證紀錄](docs/PROJECT_FINAL_VALIDATION_RESULT.md)。
- 要知道 GitHub 保存了什麼：[私人備份範圍](docs/GITHUB_PRIVATE_BACKUP.md)。

## 已經完成什麼？

| 項目 | 狀態與限制 |
|---|---|
| 本地模型與原本的單張圖片 Agent | 先前已完成實機開發驗證，包含離線與清理檢查 |
| Windows 圖形介面 | 已完成，CPU／模擬測試通過 |
| 手動圖片輸入 | 支援 JPEG、PNG；手機原圖由程式自動驗證與縮放 |
| Webcam 軟體流程 | 已完成模擬及接口測試；實體相機仍待驗證 |
| 同一模型持續處理多張圖片 | 已實作，每張重置 Agent 狀態；真實多張 CUDA 路徑尚未驗證 |
| 歷史紀錄、人工評閱與 CSV | 已完成；JSON 是原始紀錄，CSV 是衍生檔 |
| 最後品質檢查 | 180 項 CPU 測試、Ruff、strict Mypy（39 個模組）、pip check 全部通過 |

這些是工程與開發結果，不代表模型總是正確、已解決幻覺，或完成正式論文實驗。模型仍可能描述不存在的物件；同模型驗證也可能錯誤接受敘述。

## 系統怎麼運作？

```text
手動圖片 / Webcam 單張影像
  → 檢查來源、大小與雜湊
  → 自動縮放及既有模型前處理
  → 本地 InternVL3 + 有上限的 Agent 查詢與驗證
  → 繁體中文報告
  → 本地 JSON 歷史、人工評閱、CSV 匯出
```

Webcam 採「擷取一張 → 分析完成 → 保存與顯示 → 等待 5 秒 → 下一張」，不是每 5 秒保證完成一次推論，也不是影片理解或人物追蹤。沒有雲端模型、第二個模型或無限排隊。

## 環境與模型

- Windows、Python 3.11；既有開發環境為 3.11.9。
- 目標硬體：RTX 3070 Ti 8GB、i7-11700K、32GB RAM。
- 模型：`OpenGVLab/InternVL3-2B-Instruct`，固定版本 `f6c7b60375759170fd49f5e9e298e2178485c5ba`。
- BF16、`cuda:0`、batch size 1、單一 448×448 模型輸入。
- PySide6／Essentials／Addons／shiboken6 均為 6.8.3；Webcam 使用 QtMultimedia，不使用 OpenCV。
- 每張最多 8 次呼叫，每次最多 128 個輸出 token；記憶體與逾時限制不能任意放寬。

完整版本、雜湊與限制見[凍結清單](PROJECT_FREEZE_MANIFEST_2026-10-05.json)。GitHub clone 不會自動包含本機的模型與環境；缺少資產時請依操作／恢復文件核對，不要自動下載或升級。

## 安全啟動：CPU 模擬模式

以下命令假設位於專案根目錄，且既有 `.venv` 已備妥。PowerShell：

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
.venv/Scripts/python.exe -m local_vision_agent.windows_app
```

預設是明確標記的 MOCK／FakeCamera，不會載入真實模型或使用實體相機。介面分為「分析」、「詳細資料」、「歷史紀錄」。歷史紀錄可重新開啟、填寫人工評閱，或匯出 CSV。

真實 GPU 模式的命令在[操作手冊](docs/PROJECT_RUNBOOK.md)，但本專案仍處於凍結狀態。若要重新測試硬體，需作者明確解凍、確認安全圖片／場景並重新指定有上限的驗證範圍。

## 測試與資料匯出

```powershell
.venv/Scripts/python.exe -m unittest discover -s tests -q
.venv/Scripts/python.exe -m ruff check src tests scripts
.venv/Scripts/python.exe -m mypy --strict src/local_vision_agent
.venv/Scripts/python.exe -m pip check
```

匯出包含 `analysis_summary.csv`、`model_calls.csv`、`webcam_sessions.csv` 與 `engineering_summary.json`。缺少的數值留空，不假裝是 0；文字會做試算表公式防護，原始 JSON 不會因此改寫。人工評閱只是工程可用性意見，不是正確率或真值。[完整欄位與計算方式](docs/THESIS_DATA_EXPORT_DESIGN.md)。

## 凍結版本與後續方向

原始工程凍結版本是 `7c0485ff9a83706b72ebc020c151191b0a79c9e7`，tag 為 `local-vision-agent-v1.0-frozen`。此 tag 不會因後續 GitHub 說明文件更新而移動；main 可以包含較新的說明提交。凍結清單中的文件雜湊應對照該 tag，而不是假設較新的 README 仍有相同雜湊。

後續主要研究工作是指導教授安排的論文重現；此專案作為備用研究原型保留。沒有正式大型 benchmark、研究問題已證明或 SOTA 的宣稱。

[架構](docs/PROJECT_ARCHITECTURE.md) · [接口合約](docs/PROJECT_INTERFACE_CONTRACTS.md) · [已知限制](docs/PROJECT_KNOWN_LIMITATIONS.md) · [恢復指南](docs/PROJECT_RECOVERY_GUIDE.md) · [目前交接](SESSION_HANDOFF.md)
