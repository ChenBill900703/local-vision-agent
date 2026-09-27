# Moondream2 feasibility 準備 v1 — PROPOSAL，未執行

查核日期：2026-09-27。只閱官方網頁／原始碼文字，沒有下載權重／模型資產、執行 remote code 或查詢 GPU。
這是下一階段可審閱的授權範圍提案，不是當前執行許可；RD-001、RTX 3070 Ti 8GB 與 RQ1–4 不變。

## 確切候選與來源

主候選 `vikhyatk/moondream2`，release tag `2025-06-21`，完整 commit：
`9a7d4024050840e001defacec2b00727e89149e6`。
官方 [release commit](https://huggingface.co/vikhyatk/moondream2/commit/9a7d4024050840e001defacec2b00727e89149e6)
與 [tag tree](https://huggingface.co/vikhyatk/moondream2/tree/2025-06-21) 對應。
不使用會移動的 main 作載入版本；模型與程式使用同一完整 SHA，檔案下載後另記 SHA256。
不因 Moondream3 存在而更換主線；本階段不建立第二模型候選。

[固定 SHA 模型卡](https://huggingface.co/vikhyatk/moondream2/blob/9a7d4024050840e001defacec2b00727e89149e6/README.md)
metadata 標 `apache-2.0`，示範 caption/query/detect/point，要求 `trust_remote_code=True`。
這是上游聲明，不等於本專案已完成全部資產、第三方依賴或公開再散布權利審核。取得資產前保留 license／NOTICE／attribution，缺漏需釐清；本專案 code license 仍待使用者決定。

檔案樹列 `model.safetensors` 約 3.85 GB，整個 repository 約 7.61 GB，還含 GGUF。
提案只下載 safetensors、必要 config/tokenizer/remote-code 及授權檔，**不下載 GGUF 或整個 repo**；核准下載 ceiling 5 GB、暫存與快取磁碟 ceiling 12 GB，達上限停止。
這是下載規劃，不是實測大小／顯存；權重 bytes 不代表推論 VRAM。

## 相容性與 remote-code 審閱發現

1. [config.json](https://huggingface.co/vikhyatk/moondream2/blob/2025-06-21/config.json) 的 auto_map 指向 `hf_moondream.HfConfig` / `HfMoondream`，dtype 標 bfloat16、記錄 Transformers 4.52.4。這不是本機 4.57.6 的相容保證。
2. [hf_moondream.py](https://huggingface.co/vikhyatk/moondream2/blob/2025-06-21/hf_moondream.py) 載入本地相對模組，caption/query 等屬性会建立 caches。未來 preflight 必須早於 heavyweight imports／allocation，不能只在第一次 forward 前檢查。
3. [moondream.py 固定 SHA](https://huggingface.co/vikhyatk/moondream2/blob/9a7d4024050840e001defacec2b00727e89149e6/moondream.py) 建構子呼叫 `Tokenizer.from_pretrained("moondream/starmie-v1")`，沒有 pin tokenizer revision。**只 pin 主模型並不足以確保完全固定／離線**。需要獨立固定 tokenizer commit/hash，审查其權利，改成受控本地資產或驗證封存快取解析；網路封鎖下缺資產必須失敗，不能隱式下載。
4. [starmie-v1 官方檔案樹](https://huggingface.co/moondream/starmie-v1/tree/main) 約 3.7 MB，tokenizer.json 約 3.69 MB；查到候選 [commit 35192e10a54e36eabe0a7cc57a2c1aab371cafc5](https://huggingface.co/moondream/starmie-v1/commit/35192e10a54e36eabe0a7cc57a2c1aab371cafc5)。目前 README 沒有提供 license metadata；精確資產清單、hash、與主模型搭配及權利證據在 acquisition gate 再確認，不把缺 license 當已授權。
5. [固定版 requirements](https://huggingface.co/vikhyatk/moondream2/blob/2025-06-21/requirements.txt) 列 einops、pyvips-binary==8.16.0、pyvips==2.2.3。
   [image_crops.py](https://huggingface.co/vikhyatk/moondream2/blob/9a7d4024050840e001defacec2b00727e89149e6/image_crops.py) 有 pyvips 不可用時的 Pillow 路徑；此是 CPU 圖片處理，不是模型 offload。是否採用需固定並驗證 A–D 一致，不默默混用預處理。
6. [現行官方 Transformers 教學](https://docs.moondream.ai/transformers/) 列 transformers>=4.51.1、torch>=2.7.0、accelerate>=1.10.0、Pillow>=11.0.0，列生成 token 控制。現行教學可能涵蓋不同版本，固定 revision 的實際行為須逐項核對，不能直接照貼執行。

本機 metadata 查核：Python 3.11.9、torch 2.7.1+cu126、transformers 4.57.6、Pillow 12.3.0；accelerate/einops/pyvips/pyvips-binary 不存在。未安裝，未 import torch。
先確認固定 revision 實際 imports、Pillow 路徑、Windows wheel／授權；任何必要安裝列確切版本與 hashes、額外取得許可，不升級既有 torch/transformers 作為第一反應。

目前只是局部靜態審閱，不宣称 remote code 已安全。完整 gate 尚需：完整 import closure、網路／外部資產、subprocess／檔案寫入、反序列化、device placement／caches／精度、generation termination、crop 上限、資源釋放及所有依賴 license。HF 頁面 Safe 標籤不取代審閱。

## 下一階段分開批准的具體範圍

| Gate | 提案與停止條件 |
|---|---|
| 資產取得 | 僅上述完整 SHA 的 Moondream2 必要檔案；tokenizer 完成 pin／權利查核後取得，總下載不超過 5 GB、磁碟 12 GB；不下載資料集。先列 allowlist/size/hash，保留來源與 license。未解決 tokenizer 權利或 pin 則停止 |
| 依賴 | 本次不授權安裝。後續如需要，另列缺套件的確切版本、wheel/hash、license、Windows 相容性及用途，再請使用者批准；不連帶更新整個 lock |
| 程式審閱 | 固定程式完整審核，不執行；核准後才可啟用已審閱的 remote-code 或本地封存版本。任何本地修補留原 SHA、patch/hash 與理由 |
| 本機 GPU feasibility | 明確允許 GPU 查詢、CUDA 初始化、該單一模型載入與有限推論；只在 RTX 3070 Ti 8GB、Windows、既有 Python 3.11，不作訓練／正式 benchmark |
| 輸入資料 | 使用者提供並確認權利的至多 3 張非敏感 development 圖；固定 manifest/hash，不屬 formal test；無資料集下載、人像蒐集或 user study |
| 輸出與保存 | 只產生探索性 raw traces、錯誤、preflight、顯存與延遲、繁中／離線相容性紀錄，Git 外保存與備份；不作 RQ2/3 改善結論，不公開 |

建議第一輪 GPU limits（PROPOSAL，尚未批准且不是 mock 值）：batch=1、最多一個模型；每圖 512 px 最長邊、262144 pixels、10 MiB；caption/query 每次至多 128 output tokens、1024 input tokens；每圖至多 8 calls/iterations、1024 total output tokens；每 call 60 秒、每圖 300 秒；載入最多 180 秒，cleanup 最多 10 秒；最多 3 圖、24 calls、1 次載入嘗試、整個 session 30 分鐘。
caption/query 優先；detect/point/reasoning/compile 預設關閉，後續需功能支援＋額外硬體檢核才啟用。無自動重試或額外圖；若載入失敗或 OOM 即停止，後續修復需帶修訂紀錄與新授權。

載入估計尚未量測，必須涵蓋 weights/encoder/activations/KV/workspace/framework；沒有合理保守估計就 fail closed。
`GpuGuard.preflight` 必須在 heavyweight import/allocate 前通過：estimated peak <=6400 MiB 且 current free >= estimated peak+1536 MiB，另外計入桌面佔用；這不是 allocator cap。
需在真實 adapter 實作單一持久 worker、固定 `cuda:0` placement、inference mode、參數/buffers/KV 裝置核對、OOM/timeout 中止與資源釋放、driver/allocator/shared-memory 監測後，才可作 pilot。禁止 device_map="auto" 或 CPU/disk/shared-memory fallback。
量測 allocated/reserved/裝置層顯存、冷載入／暖推論時間与 failure；監測無法辨識 Windows shared memory 時明示限制，不宣稱零 spill。

斷網驗證須在資產齊全且 acquisition 已停止後做；任何隱式請求或漏資產均失敗。繁中需求需測試同一模型能否在 bounded single response 保留足夠內容；不能以 mock 中文成功代替。若需要另一模型／翻譯流程，回報 blocker，不擅加。
以上 gate 未完成前，不授權 formal evaluation，不變更 RD-001，也不保證 8GB fit 或研究改善。
