# SUPERSEDED snapshot — 2026-09-27 before RD-001

Historical record only; not active instructions, requirements or execution authorization.
Original path: `docs/EXPERIMENT_PROTOCOL.md`. Original text follows unchanged (line endings may be normalized).
Active direction: [RD-001](../../RESEARCH_DIRECTION.md).

---

# 實驗協定 v0.2（設計提案，尚未凍結）

更新日期：2026-09-22。v0.1的CLIP必做、EuroSAT及LLM控制器提案不再列必要範圍。
本次只修改文件，不執行實驗。完整契約以 [需求規格v1.1](REQUIREMENTS.md) 為準。
本版本不是事後宣稱的預註冊協定，也不是教授核准；尚未取得正式測試結果。

## 分開評估兩種任務

分類研究：Pet與DTD固定詞彙，DINOv2-Small及ResNet18基準，
檢驗校準、拒答與可靠性。圖片描述為必要功能，但獨立作工程驗收，
不將生成文字當分類真值、不用分類AURC證明描述品質。

## 正式實驗前須凍結

依需求規格R4至R7，凍結：
- 官方資料版本、權利、類別表、split manifest/hash、每類精確張數、
  重複／相關樣本處理；Pet官方test與DTD split1。
- 分層split seed 42；訓練seed 17/42/73；凍結骨幹與線性頭規格。
- 每模型輸入前處理、訓練epochs、optimizer、學習率搜尋範圍、
  搜尋次數／時間預算、checkpoint選擇、失敗／停止／重跑條件。
- 正溫度temperature scaling、擬合方法、決策驗證門檻與平手規則。
- R6離散AURC公式與平手期望、ECE bin定義、失敗分母及bootstrap方案。
- 描述模型revision／來源、輸入及輸出token上限、固定提示與解碼參數；
  R7描述驗收來源、品質門檻與人工評分程序。

上列尚未確定的數值不能由實作預設靜默代填。
探索性試驗與正式test分開，任何下載或GPU試跑須另外授權。

## 不可違反的分析界線

完整test清單需在每方法核對；缺分數的失敗run不產生完整主AURC。
拒答前的預測與分數保留，AURC不可只計成功回答的子集。
所有樣本的accuracy與回答子集的accuracy清楚區分。
只在calibration擬合校準，只在decision-validation選門檻／超參數。
若temperature scaling沒有改變排序，AURC不變是有效結果。
不得以強骨幹優於弱骨幹就宣稱Agent有額外貢獻。

正式量測需包含模型載入、切換與釋放條件；離線重播不是實測時間／VRAM。
紀錄每種子、每資料集、失敗數及負面結果；不只報最好的結果。

## 產物與證據

現有evaluation.py只處理簡易sample_id/split/target/prediction表，尚非完整協定實作。
後續格式至少符合R2與R8，含raw預測、分數、接受／拒答／失敗、
run設定、模型與split版本、依賴及程式狀態。
資料、權重及完整run不放Git，另備份；公開中文圖表須有權利與重建指令。
GPU預算與OOM保護以R9為準，尚不能宣稱已通過真機驗收。
