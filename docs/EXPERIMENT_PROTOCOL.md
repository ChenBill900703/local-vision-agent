# Agent Evaluation Protocol v0.3 — PROPOSAL

日期：2026-09-27。依 [RD-001](RESEARCH_DIRECTION.md)；取代舊分類 protocol v0.2。
**研究方向 FROZEN，但本實驗方案仍 PROPOSAL／NOT FROZEN，未執行、未獲正式 test 授權。**
禁止以事後補寫稱作事前註冊。方向凍結回合未下載資料、未測試、未使用 CUDA。

2026-09-27 Phase 1 增補：使用者另已批准 CPU/mock 工程測試，實作見
[工程契約 v1](ENGINEERING_CONTRACT.md)。這不授權任何正式評估或 GPU 作業。
Mock fixtures 不屬研究樣本；A–D 介面測試不是四組效果實驗，也不會凍結 prompts、正式資料／指標或採用 mock 的 budgets 作科學門檻。
原文保留於 [快照](archive/2026-09-27-before-phase1/EXPERIMENT_PROTOCOL.md)。

## 1. 問題、假設與判定邊界

| RQ | 固定研究問題 | 計畫觀察（非既定結論） |
|---|---|---|
| RQ1 | 小型 VLM 能否在指定 8GB 環境作本地核心？ | offline completion、峰值顯存、failure、工具能力／中文輸出 |
| RQ2 | 多階段比 single-pass 是否較完整？ | 預先定義 salient information 的 recall／completeness |
| RQ3 | Verification 是否減少可觀察錯誤？ | 錯誤物件／claim 數量與率，並檢查完整性是否犧牲 |
| RQ4 | 品質與成本如何取捨？ | latency、peak VRAM、calls、iterations、failure 與品質一起報告 |

主要系統比較固定 A vs D，verification 比較為 B vs D，自適應查詢比較為 C vs D。
Primary metric、各比較的主要 endpoint、success/tradeoff threshold、最小有意義差異、樣本數、重複數、信賴區間及多重比較處理均 UNKNOWN。
選擇必須有資料／標註與研究理由，在正式 test 前由研究者及適當確認者鎖定；不能挑測後最好看的數字。
Negative/null 結果照樣保留；工程可運行不等於科學改善成立。

## 2. 固定 A–D 設計與對照

同一 Moondream2 revision／weights／precision／image preprocessing；若依 RD-001 批准換核心，四組一起使用替換後同一模型。
禁止只拿不同尺寸模型比較卻省略 A。

| 組別 | 流程 | Verification | Query policy |
|---|---|---|---|
| A | Single-pass caption／single response | 無 | 無追加 query |
| B | Multi-stage Agent without verification | 無 | 與 D 相同 bounded adaptive 規劃規則 |
| C | Fixed-query Agent | 與 D 相同驗證策略 | 問題／順序事前固定，不依答案調整 |
| D | Full local Agent | 有 | Adaptive bounded query |

- **A vs D**：整體 agent workflow 效果，包含多次推論的額外成本；不能宣稱與計算量無關。
- **B vs D**：只移除 verification 模組及其專用呼叫。為主要機制比較提案，D 的驗證置於調查完成後，不回饋重開無限調查；B/D 的初始觀察、調查模板、觸發與終止條件保持一致。若非決定性使中間軌跡不同需記錄，不偽稱完全相同。
- **C vs D**：同一 verification 方法、輸出結構及最大預算，只改固定／自適應查詢；實際 calls 可能不同，必須同時報告。
- 四組共用輸入影像清單、輸出語言／呈現規格、失敗政策、解碼設定、量測方法及 image-embedding cache policy。
- A 僅一次視覺模型回應，後續非模型格式化可用；不可暗加第二次語言模型潤飾。若繁中轉換需額外模型，須另列呼叫、所有組別一致並重新確認 baseline 名稱／契約。
- 最大長度與實際長度一起報告。不能強迫 A 用極短答案、卻讓 D 無限輸出，再把長度差誤當完整性改善。
- 共用測試排程／冷暖啟動控制；模型重載與 batch 政策一致。可在時間許可及事前批准時加 budget-matched 敏感度分析，不是必要新功能。
- 每一新增消融都須回答已固定 RQ；不為增加篇幅堆模型／功能。

## 3. Dataset 與 split（待定）

Final dataset／version／subset／counts／license：**UNKNOWN**。優先選能支援真實物件／caption/claims 評估的公開資料；COCO 僅是可查證的相關資料與 CHAIR 方法背景，非本次選定的必下載資料。
Pet/DTD 是 SUPERSEDED 歷史分類方案，附加使用須重新確認。

正式 freeze 前記錄：

1. 圖片及標註版本、來源、使用／再散布權利、敏感資料處理、可引用內容。
2. 每階段樣本量、預先抽樣規則、image IDs／hash；development/pilot、validation、test 互斥，跨 split 的 exact/near duplicates 與關聯影像檢查。
3. Salient 的定義、標註覆蓋範圍、物件類別／同義詞與 claim matching。標註缺少物件不一定代表物件不存在，不得一律算 hallucination。
4. Test manifest 不看結果後換圖；不得只留成功樣本；基礎模型預訓練重疊若未知如實聲明。
5. 無需為形式而加入訓練；若日後批准任何學習／tuning，僅可用 development/validation，不接觸 test。
6. Pilot 僅探索可行性與設計；其結果不能不揭露地混入 confirmatory test。已看過的圖不得假裝未看過。

## 4. 指標候選與適用條件

| 候選 | 前提／必報界線 |
|---|---|
| Salient object recall | 獨立定義 salient ground truth 及匹配規則；不等同一般資料集所有物件 recall |
| Object precision | 標註足夠；以有依據的提及數為分子／輸出提及數為分母；去重與單位先鎖定 |
| Hallucination count/rate | 錯誤物件與屬性／關係 claim 分開；指定 claim 或 image 分母；unsupported 與 contradicted 不混為一類 |
| CHAIR | 僅在 annotation／類別與語言映射合理時使用；先查原文及評分實作，不能直接套到任意繁中段落 |
| Caption completeness/correctness | 獨立 rubric、圖片證據、盲化標註與一致性處理，不能由 Agent 自稱 |
| Human evaluation | 人評規則、評審數／資格、盲化順序、協議／分歧處理、適用倫理／同意程序先確認 |
| Latency / peak VRAM | 指定量測邊界、單位、冷暖啟動、背景負載與取樣方式 |
| Calls / failure / iterations | 包含所有工具及模型呼叫、額外報告／轉換、失敗及重試，不能只計成功路徑 |
| CLIPScore / CIDEr / BLEU | 僅在語言、參照資料及方法適用時考慮；CLIPScore 不要求 reference，CIDEr/BLEU 需適用 reference；均不能取代獨立 hallucination 檢查 |

CHAIR 對物件的評估不能證明所有屬性、數量、關係或其他 claim 正確。中文輸出／翻譯造成的 matching error 應另評估；英文原始回應與繁中報告不可混算。
上述來源與方法限制見 [RESEARCH_SOURCES](RESEARCH_SOURCES.md)。

空輸出、無物件提及與工具失敗的分母處理必須事前指定，不能以零除為零錯誤率。
同時列 all-attempted 與 successful-output 統計、未定義指標數量、完整性、長度及 failure；不把失敗排除後的分數當全體成績。
圖例／成功圖片只能按預先規則抽取，保留失敗案例，不 cherry-pick。

## 5. Verification 與人工真值

- 模型對自己再次提問可能重複同一錯誤；supported 只是內部一致／觀察支持，不是獨立正確性證明。
- 檢測不到不等於不存在；錯誤／unsupported／矛盾分開記錄。
- 評估須使用與方法輸出獨立的標註／人工判定，不能把 verifier 回答拿來當測試真值。
- 人評先固定選樣、rubric、匿名化方法標籤、評閱順序、評審數、缺失評分／分歧仲裁及一致性分析；數值尚 UNKNOWN。
- Human evaluation 如涉及受試者／招募／可識別資訊，須先確認學校審查、同意及匿名化要求；不得自行宣告豁免。
- 非必要不引入額外 judge 模型；不得以雲端 GPT judge 冒充本地系統，也不以 AI 分數代替未做的人評。

## 6. Resource protocol（必須實測，不可預先宣稱）

主環境 RTX 3070 Ti 8GB／i7-11700K／32GB／Windows／Python 3.11。
6400 MiB process planning ceiling ＋ estimated-use 後 1536 MiB free reserve；計入既有桌面使用。
單一 heavyweight GPU model、batch1、明確 image/token/call/iteration/timeout bounds。
禁止 CPU/disk/shared GPU memory fallback，禁止 device_map="auto"；OOM safe fail。

記錄 driver、PyTorch/Transformers、模型與 remote-code revision、precision、allocation/reserved 峰值、裝置層顯存及 Windows shared-memory 的可觀測性。
若監測無法證明未使用 shared memory，須報限制，不能聲稱已證明「零 spill」。

端到端 latency 包含預處理、影像編碼、所有模型／工具調度、verification、中文呈現與結果整合；另分項記錄，避免只報核心 forward。
冷啟動含載入成本，暖啟動另報；GPU 計時同步方法與取樣 overhead 在授權後選定，不能拿 cached replay 當推論耗時。
記錄 calls、image encodes、輸入／輸出 tokens、停止 iterations，作計算成本 proxy；沒量電力／FLOPs 就不能宣稱已量到。
額外 GPU 任務存在時不得混為正式可比較資源結果。所有組別背景條件一致；方法執行順序與配對設計事前固定。

## 7. 分析、追溯與正式 freeze checklist

- [ ] 模型 exact revision／weights/code hash、授權、remote-code 審核與相容性證據。
- [ ] 8GB 及離線 feasibility、中文呈現、各工具能力與安全失敗證據。
- [ ] Dataset／標註／權利、完整 manifests、split／近重複、獨立真值。
- [ ] A–D prompts/templates、adaptive triggers、verification、limits、stop/retry/failure policy。
- [ ] Primary metric／contrast／tradeoff 門檻／樣本數與選樣理據。
- [ ] Repetitions、seed（適用）、同圖配對分析、uncertainty／CI 方法、多重比較及 exclusions。
- [ ] 人評與機構／教授要求有適用證據；新穎性與投稿要求確認。
- [ ] 版本、日期、確認者與正式實驗授權；完整測試前凍結，不靠測試結果反推。

每個結果保留 run ID、commit（無則明記）與 dirty state、依賴、dataset/model revision、hash、input ID、prompt/template revision、agent config、stop policy、seed、逐圖 claims、tool traces、修正／失敗、latency/VRAM。
報表從 artifacts 產生，含分母、缺失、error bars 定義與重製命令；原始證據 Git 外備份。
任何 post-hoc 改動都新增 dated amendment 並標 EXPLORATORY；保留原方案及 negative/null 結果。
此 checklist 未完成前不得把 v0.3 稱為正式凍結實驗。
