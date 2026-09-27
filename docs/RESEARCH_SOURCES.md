# Research Sources — RD-001

整理／查核日期：2026-09-27。方向依 [RD-001](RESEARCH_DIRECTION.md)；此為文獻／官方來源索引，不是 feasibility 結果或完整 systematic review。
本次核對官方 model card／API 文件、論文原始摘要頁與書目。未下載權重／資料、未跑範例；尚未逐篇完成全文方法／程式複現。
「來源說明」與「本專案採用條件／推論」分開記錄，不把他人結果當自己的測量。

## 1. Moondream2、small/local VLM 與工具介面

| 來源 | 核對到的內容 | 本專案用途與界線 |
|---|---|---|
| [Moondream2 官方 model card](https://huggingface.co/vikhyatk/moondream2) | 頁面列 2B、Apache-2.0 標示，並提供 caption/query/detect/point 範例；可見 2025-06-21 revision 範例 | 主要候選的來源。該日期是 source-observed tag，不等於本專案已選定 immutable commit。確切權重、程式、依賴及授權適用仍須核查 |
| [Moondream 官方 Transformers 文件](https://docs.moondream.ai/transformers/) | 列本地 Transformers 使用及 caption/query/detect/point、影像 encoding reuse；頁面涵蓋不同模型版本 | adapter 能力表的查證入口。泛用文件不能證明固定 Moondream2 revision 在 Windows 可用，更不能證明 3070 Ti 實測 fit |

官方範例出現 remote-code 載入，未來需固定 revision 並審核程式；範例不是執行授權。不得複製任何 device_map="auto" 或 offload 路徑。
Moondream2 目前維持 candidate / proposed / pending hardware validation；繁中能力、真實峰值、延遲及離線可重現性均 UNKNOWN。
Moondream3／3.1 只作 related/future work 或另行批准的比較，不引入第二條主模型競賽。

## 2. Captioning／視覺問答／資料與評估

| 原始來源 | 來源說明 | 本專案關聯（設計推論／限制） |
|---|---|---|
| [Microsoft COCO: Common Objects in Context — Lin et al., 2014](https://arxiv.org/abs/1405.0312) | 常見物件在複雜日常場景的資料與標註研究 | 物件／場景評估的背景；實際 caption/annotation release、split、權利與 counts 要另核，尚未選定 dataset |
| [VQA: Visual Question Answering — 2015](https://arxiv.org/abs/1505.00468) | 給圖片與自然語言問題、回答視覺資訊的任務 | visual query/VQA 工具的方法背景；本專案不因此承諾完整 VQA benchmark 或聊天系統 |
| [CIDEr: Consensus-based Image Description Evaluation — Vedantam, Zitnick & Parikh, CVPR 2015](https://arxiv.org/abs/1411.5726) | 以人類描述共識評估生成描述 | 只有適當 reference captions、語言／tokenization 才考慮；不是必做指標，也不是 hallucination 證明 |
| [CLIPScore — Hessel et al., EMNLP 2021](https://aclanthology.org/2021.emnlp-main.595/) | 可不依賴參照描述的 image–text 相容性評分；另有 reference-augmented 版本 | 屬條件式次要評估；中文能力、域適用及額外模型成本須核查，不能取代物件／claim 正確性 |

BLEU 目前只是待評估名稱，未定採用或實作；若正式選用須另核原論文、語言與 reference 條件。
完整性不等於文字長度；最終 salient 規則與獨立標註要在 test 前定義，不從輸出倒推。

## 3. Hallucination、CHAIR 與驗證

| 原始來源 | 來源說明 | 本專案關聯（設計推論／限制） |
|---|---|---|
| [Object Hallucination in Image Captioning — Rohrbach et al., EMNLP 2018](https://aclanthology.org/D18-1437/) | 針對生成描述的物件幻覺提出影像相關性評估，研究 MSCOCO 上句子指標與幻覺的落差；CHAIR 來源 | 不是一般 caption 分數即可證明低幻覺。正式使用須讀全文／固定評分器，核對物件標註、詞表、同義詞及繁中映射；不擴稱可驗證所有屬性／關係 |
| [Evaluating Object Hallucination in Large Vision-Language Models — Li et al., EMNLP 2023](https://arxiv.org/abs/2305.10355) | 提出 POPE，以物件問答方式評估 object hallucination | 幫助設計 object verification 的評估對照；問答分數不是自由報告的完整品質，不能拿方法自己的 query 答案當真值 |
| [Woodpecker: Hallucination Correction for Multimodal Large Language Models — Yin et al., 2023 preprint / SCIS 2024](https://arxiv.org/abs/2310.16045) | 分階段概念抽取、問題形成、視覺驗證、claim 與幻覺修正的 training-free 方法 | verification／多階段修正的 prior work，必須比較差異，不能宣稱本專案首次想到驗證；其成績與模型堆疊不保證能在本 8GB 環境重現 |

獨立 annotation／人工 rubric 才是外部評估依據。相同 VLM 的自我驗證可能共犯同一錯誤，故本專案須實驗檢驗而非宣稱必有效。
同時報完整性、錯誤、輸出長度及成本，避免靠不說任何事達成表面零幻覺。

## 4. Visual agents、agentic vision 與 grounding

| 原始來源 | 來源說明 | 本專案關聯（設計推論／限制） |
|---|---|---|
| [Visual Programming: Compositional visual reasoning without training — Gupta & Kembhavi, 2022 preprint](https://arxiv.org/abs/2211.11559) | VISPROG 以 LLM 產生模組化程式，調用視覺工具並保留中間結果 | 視覺工具調度／可解釋流程的相關工作；本專案改採有界有限狀態，不執行模型生成程式，不要求雲端或另一 LLM controller |
| [Modeling Context in Referring Expressions — Yu et al., ECCV 2016](https://arxiv.org/abs/1608.00272) | 視覺上下文與 referring-expression 生成／理解，包含 RefCOCO 系列評估 | grounding 概念與評估背景；不因此增加必要資料集，detect/point 仍須 revision 支援與硬體驗證 |

本專案候選貢獻是固定 consumer GPU 上的本地 bounded workflow、公平同模型對照、逐圖驗證紀錄與品質／資源分析；新穎性需完整 prior-work 對照與教授確認，不能僅因稱為 Agent 就宣稱創新。

## 5. Historical / secondary literature

舊 CLIP／DINOv2／ResNet18／calibration／Pet／DTD／EuroSAT 與舊 agent 路由文獻保留在
[校正前 RESEARCH_SOURCES](archive/2026-09-27-pre-RD-001/RESEARCH_SOURCES.snapshot.md)。
它們屬 SUPERSEDED thesis-core design，不主導目前 literature review；若未來另批 secondary experiment，再查版本、權利與引用。
此處保留歷史不等於批准新一輪模型／題目選擇。

## 6. 後續查證紀律

- 模型與第三方 code/license 需按選定 revision 留 immutable reference；model-card 標籤不足以涵蓋所有再散布物。
- Dataset 最終版本、下載範圍、影像及 annotation 使用權、institution review 尚 UNKNOWN；論文引用不等於下載／發布許可。
- 投稿使用的公式、評分器、BibTeX／DOI 須再對原文全文查核，不以 AI 生成書目替代。
- 網頁會變動；保存查核日期及未來實際使用版本，不把今日動態頁面當不變的 reproducibility pin。
- 本文件只提供已核對來源的適用範圍，不證明新穎性、接受機率、中文效能或本機 VRAM。
