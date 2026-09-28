"""Non-model Traditional Chinese report formatting; no invented observations."""

import html
import json
from dataclasses import asdict

from .contracts import Report


def to_json(report: Report) -> str:
    return json.dumps(asdict(report), ensure_ascii=False, indent=2, allow_nan=False)


def to_markdown(report: Report) -> str:
    def literal(text: str) -> str:
        # Model text remains inert text, including HTML, links and Markdown delimiters.
        return "<pre>" + html.escape(text) + "</pre>"

    labels = {
        "model-proposed": "模型提出（未驗證）",
        "supported": "同模型觀察支持",
        "contradicted": "同模型觀察反駁",
        "unresolved": "未確定",
    }
    mocked = report.evidence_kind == "MOCK_NOT_RESEARCH_EVIDENCE"
    lines = [
        "# 影像理解報告（MOCK 模擬，非研究證據）"
        if mocked
        else "# 影像理解報告（本地模型開發驗證，非正式論文結果）",
        "",
        f"執行 ID：{report.run_id}",
        "輸入 ID：" + literal(report.input_id),
        f"比較組別：{report.method.value}；狀態：{report.status}",
        f"停止原因：{report.stop_reason}；調查停止：{report.investigation_stop}",
        "",
        "## 簡述、場景與細節",
    ]
    for observation in report.observations:
        if observation.answer and observation.request.prompt_id != "verify":
            lines.extend(
                [f"{observation.state} [{observation.call_id}]", literal(observation.answer.text)]
            )
    lines.extend(["", "## 敘述與驗證紀錄"])
    for claim in report.claims:
        lines.extend(
            [
                literal(claim.text),
                (
                    f"狀態：{labels[claim.status]}；"
                    f"來源：{', '.join(claim.observation_ids)}；"
                    f"驗證：{claim.verification_id or '未執行'}"
                ),
            ]
        )
    lines.extend(["", "## 未確定、衝突與限制"])
    for observation in report.observations:
        if observation.error:
            lines.append(f"{observation.call_id}：{observation.error}")
        elif observation.answer and (observation.answer.uncertain or observation.answer.missing):
            lines.append(f"{observation.call_id}：有未確定內容或待查細節。")
    lines.extend(
        [
            "所有影像語意均來自 mock 腳本，不是圖片辨識。"
            if mocked
            else "以下為模型觀察；候選敘述不等於客觀真值，未明確驗證者維持未確定。",
            "同模型驗證不是獨立真值；未驗證敘述及反駁內容不得視為事實。",
            "",
            "## 資源摘要",
            f"工具嘗試次數：{len(report.observations)}",
            "真實模型延遲／峰值顯存：未量測；未載入模型。"
            if mocked
            else f"模型查詢總延遲（秒）：{report.model_latency_s}；峰值保留顯存（MiB）：{report.peak_vram_mib}；缺失值表示未量測。",
        ]
    )
    return "\n\n".join(lines) + "\n"
