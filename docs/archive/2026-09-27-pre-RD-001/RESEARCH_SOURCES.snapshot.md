# SUPERSEDED snapshot — 2026-09-27 before RD-001

Historical record only; not active instructions, requirements or execution authorization.
Original path: `docs/RESEARCH_SOURCES.md`. Original text follows unchanged (line endings may be normalized).
Active direction: [RD-001](../../RESEARCH_DIRECTION.md).

---

# 資料與文獻索引

核對日期：2026-09-06。以下已核對官方頁面/摘要；不代表已下載資料或已全文讀完論文。

## 影像資料

| 資料集 | 規模 | 本研究用途 | 官方來源與使用注意 |
| --- | --- | --- | --- |
| Oxford-IIIT Pet | 37類，每類約200張；官方下載約800MB | 必做，細粒度分類 | https://www.robots.ox.ac.uk/~vgg/data/pets/ ；頁面列CC BY-SA 4.0，圖片原作者保有著作權 |
| DTD | 47類、5640張；官方下載約625MB | 必做，紋理分類 | https://www.robots.ox.ac.uk/~vgg/data/dtd/ ；供研究用途，保留原始說明，勿推定任意再散布權 |
| EuroSAT | 10類、27000張，選RGB版本 | 第三資料集，領域差異 | https://github.com/phelber/EuroSAT ；作者引導至Zenodo下載，舊主機已標deprecated；MIT及Sentinel條款見原頁 |

約四萬張是整體資料規模，不等於測試樣本數。兩個必做資料集先完整跑通；
不用為湊數再加入大型影像集。原圖保留本機，不上傳GitHub。

## 起始閱讀清單

1. CLIP, Learning Transferable Visual Models From Natural Language Supervision (2021): https://arxiv.org/abs/2103.00020 — 零樣本分類基準。
2. DINOv2: Learning Robust Visual Features without Supervision (2023): https://arxiv.org/abs/2304.07193 — 凍結特徵及線性頭。
3. On Calibration of Modern Neural Networks (ICML 2017): https://proceedings.mlr.press/v70/guo17a.html — 校準與temperature scaling。
4. HuggingGPT (2023): https://arxiv.org/abs/2303.17580 — 規劃、選模、工具執行與總結；作為Agent定位參考。
5. Cats and Dogs (CVPR 2012): Pet官方頁面列出的資料集論文，見上述來源。
6. Describing Textures in the Wild (CVPR 2014): DTD官方頁面提供論文、引用與切分。
7. EuroSAT: A Novel Dataset and Deep Learning Benchmark for Land Use and Land Cover Classification (2019): 作者repository提供引用。

後續依這些工作補上選擇性分類、模型級聯、工具Agent的近年直接相關文獻，
建議先精讀10至15篇，再擴展到約25至40篇與題目直接相關的引用；数量為工作目標，非學校最低要求。
逐篇記錄研究問題、方法、資料集、比較基準、限制與本研究差異。不宣稱單純串接已有模型為新方法。
