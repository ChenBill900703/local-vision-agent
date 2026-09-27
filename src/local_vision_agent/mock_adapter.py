"""Explicit synthetic fixture responses, NOT recognition or thesis evidence."""

import time
from dataclasses import dataclass, field

from .contracts import AgentError, Answer, ImageInfo, Request


@dataclass(frozen=True)
class MockAdapter:
    answers: dict[str, Answer] = field(default_factory=dict)
    failures: tuple[str, ...] = ()
    delays_s: dict[str, float] = field(default_factory=dict)
    capabilities: tuple[str, ...] = ("caption", "query")
    model_id: str = field(default="mock-scripted", init=False)
    revision: str = field(default="fixture-v1", init=False)
    is_mock: bool = field(default=True, init=False)

    def invoke(self, request: Request, image: ImageInfo) -> Answer:
        if request.tool not in self.capabilities:
            raise AgentError("UNSUPPORTED_TOOL")
        time.sleep(self.delays_s.get(request.prompt_id, 0))
        if request.prompt_id in self.failures:
            raise AgentError("TOOL_FAILURE")
        if request.prompt_id in self.answers:
            return self.answers[request.prompt_id]
        if request.prompt_id == "caption":
            return Answer(
                "模擬：桌上有一個杯子。", ("桌上有杯子",), True, ("object",), output_tokens=16
            )
        if request.prompt_id == "scene":
            return Answer("模擬場景：室內。", ("場景為室內",), output_tokens=12)
        if request.prompt_id == "object":
            return Answer(
                "模擬：杯子的細節不明。", uncertain=True, missing=("detail",), output_tokens=16
            )
        if request.prompt_id == "detail":
            return Answer("模擬：無法判定杯子的顏色。", uncertain=True, output_tokens=18)
        if request.prompt_id == "verify":
            return Answer("模擬：缺乏獨立證據，仍未確定。", verdict="unresolved", output_tokens=20)
        raise AgentError("UNKNOWN_PROMPT")
