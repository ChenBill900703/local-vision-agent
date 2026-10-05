# GitHub 私人備份說明

作者明確要求將專案與過程上傳 GitHub，並設為私人儲存庫。此授權涵蓋私人遠端建立、程式與文件提交、main 與原凍結 tag 推送；不解凍功能開發，也不授權新增硬體測試。

私人儲存庫：`ChenBill900703/local-vision-agent`，建立時即為 private，先確認私有再推送。實際遠端可見性與提交一致性由推送後查詢核對，本機回執保存在 ignored artifacts/github-private-upload/。

## GitHub 保存的範圍

- 所有 Git 追蹤的專案程式、設定、測試與文件。
- 完整 main 提交歷史及原註解 tag `local-vision-agent-v1.0-frozen`。
- 白話繁中 README、開發過程、所有既有結果與失敗說明。
- 最終純文字 CPU 測試／Ruff／Mypy／pip check 輸出及其雜湊。

## 留在本機的範圍

模型權重、未確認再散布權利的第三方 controlled code、私人 development 圖片、Webcam captures、虛擬環境、cache、raw runs、憑證與含私人資料的證據備份，都不會強制加入 Git。私人儲存庫仍是外部服務，不等於可以忽略先前的照片不得上傳限制。

因此這是完整的**程式與開發紀錄備份**，不是包含所有 ignored 大型／私密資料的磁碟映像。要在另一台電腦恢復真實模型執行，仍須依 runbook 取得經授權且符合原雜湊的本地模型／環境。

## 版本與凍結規則

原凍結 commit：`7c0485ff9a83706b72ebc020c151191b0a79c9e7`。原 tag 不移動，原 freeze manifest 不改寫。main 新增的 GitHub 說明文件提交不是重新硬體驗證，也不修改程式。

舊文件中「尚無 remote／push 未授權」描述當時凍結情境；本次作者的私人備份指示僅取代這項發布限制。功能開發凍結、既有負面證據與硬體 blocker 均維持。若需核對 freeze manifest 的 README／handoff 雜湊，請對照原 tag；目前 main 的說明文件可能較新。
