# SUPERSEDED snapshot — 2026-09-27 before RD-001

Historical record only; not active instructions, requirements or execution authorization.
Original path: `docs/DELIVERY_PLAN.md`. Original text follows unchanged (line endings may be normalized).
Active direction: [RD-001](../../RESEARCH_DIRECTION.md).

---

# 論文交付計畫 v1.1

更新日期：2026-09-22。只記錄目標，不授權實作／下載／CUDA工作。
最新需求見 [REQUIREMENTS.md](REQUIREMENTS.md)；舊版時程與LLM必要性提案已被取代。

## 必要交付

1. Pet品種分類、DTD紋理分類、簡短繁體中文圖片描述；單張與資料夾逐張輸入。
2. DINOv2-Small分類頭與ResNet18基準；描述模型需另選且通過8GB安全驗收。
3. 資料來源／權利、完整manifest、固定切分與類別表、重複檢查。
4. 校準、拒答、離散AURC、其他分類指標與獨立描述驗收。
5. 中文報告、論文圖表及數值表；每項有實驗證據與重建指令。
6. 固定環境、清楚程式與測試、GPU失敗安全及完整錯誤紀錄。
7. 可公開GitHub材料；推送另取得授權。

CLIP、EuroSAT、雙模型驗證及LLM控制器不列必要交付。
圖片描述是必要功能，不能因時程緊迫自動移除。
上述大部分仍未實作；只有環境與部分安全／路由／評估骨架。

## 目標里程碑（須後續取得實作及GPU授權）

| 日期 | 目標 |
| --- | --- |
| 9月底 | 需求／方法審閱、描述模型選型與資源試驗方案；資料／模型權利檢查 |
| 10/1–10/10 | 資料契約、安全生命週期、分類與描述最小介接 |
| 10/11–10/20 | 校準、拒答、AURC、批量輸入與逐圖紀錄 |
| 10/21–10/31 | 中文報告與圖表、整合／失敗測試、必要功能驗收及凍結 |
| 11月 | 按已凍結協定正式實驗、完整性核對、必要重跑與分析 |
| 12月 | 寫作與老師修改；12/31論文初稿 |

10月底完成程式不代表正式實驗、研討會錄取或口試資格已完成。
新增描述會增加選型與驗收負擔；上述日期是目標，不是未驗證的保證。
如果資源／中文品質／時程有問題，要列出未滿足需求交由使用者決定。
正式測試前確認學校年度規章、老師意見與研討會規則。

## 驗收要求

以REQUIREMENTS.md R1–R9逐項追蹤「未做／已實作／CPU驗證／GPU驗證」，
不要把文件齊全或測試成功當成模型效果提升。
分類科學假設與描述工程品質分開；不捏造改善、引用或核准。
