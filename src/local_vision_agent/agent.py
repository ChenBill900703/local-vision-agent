"""Finite same-adapter A-D controller with explicit mock or supervised real executor."""

import time
from collections.abc import Callable
from dataclasses import replace
from uuid import uuid4

from .contracts import (
    AgentError,
    Answer,
    Claim,
    Executor,
    ImageInput,
    Limits,
    Method,
    Observation,
    Report,
    Request,
    VisionAdapter,
)
from .image_input import inspect_image
from .internvl_adapter import InternVLAdapter
from .mock_adapter import MockAdapter
from .tool_executor import MockProcessExecutor

# Versioned finite prompt library; model text never becomes executable tool instructions.
PROMPTS = {
    "caption": "以繁體中文描述圖片的場景、重要物件與可見細節；不確定時明示。",
    "scene": "以繁體中文描述可見場景，不推測不可見的背景。",
    "object": "以繁體中文檢查重要物件；看不清楚的物件請標示未確定。",
    "detail": "以繁體中文描述可見細節；不要推測看不見的屬性。",
    "verify": "檢查候選敘述，回報 supported、contradicted 或 unresolved；非獨立真值：",
}


def validate_answer(answer: Answer, limits: Limits, remaining_tokens: int) -> None:
    """Reject malformed or oversized responses before inserting into memory."""
    if (
        not isinstance(answer, Answer)
        or not isinstance(answer.text, str)
        or not answer.text.strip()
        or type(answer.uncertain) is not bool
        or type(answer.claims) is not tuple
        or type(answer.missing) is not tuple
        or any(not isinstance(c, str) or not c.strip() for c in answer.claims)
        or any(m not in ("object", "detail") for m in answer.missing)
        or answer.verdict not in ("supported", "contradicted", "unresolved")
        or type(answer.output_tokens) is not int
        or answer.output_tokens <= 0
    ):
        raise AgentError("INVALID_TOOL_RESULT")
    if len(answer.claims) > limits.max_memory_entries:
        raise AgentError("MEMORY_LIMIT")
    if len(answer.text) + sum(map(len, answer.claims)) > limits.max_response_chars:
        raise AgentError("OUTPUT_LIMIT")
    if answer.output_tokens > min(limits.max_output_tokens, remaining_tokens):
        raise AgentError("OUTPUT_LIMIT")


class Agent:
    def __init__(
        self,
        limits: Limits,
        adapter: VisionAdapter,
        *,
        executor: Executor | None = None,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if type(limits) is not Limits:
            raise AgentError("MISSING_LIMITS")
        limits.__post_init__()
        if type(adapter) is MockAdapter:
            selected_executor: Executor = executor or MockProcessExecutor(
                adapter, limits.cleanup_timeout_s
            )
        elif type(adapter) is InternVLAdapter:
            if executor is not adapter or not adapter.loaded or adapter.config.limits != limits:
                raise AgentError("REAL_ADAPTER_REQUIRES_LOADED_SUPERVISED_EXECUTOR")
            selected_executor = adapter
        else:
            raise AgentError("REAL_ADAPTER_NOT_ENABLED")
        self.limits = limits
        self.adapter = adapter
        self.executor = selected_executor
        self.clock = clock

    def run(self, item: ImageInput, method: Method) -> Report:
        if not isinstance(method, Method):
            raise AgentError("INVALID_METHOD")
        limits = self.limits
        start = self.clock()
        observations: list[Observation] = []
        claims: list[Claim] = []
        states = ["START"]
        total_tokens = 0
        image = None
        investigation_stop = "NOT_STARTED"

        def call(state: str, prompt_id: str, claim: str | None = None) -> Answer:
            nonlocal total_tokens
            if not states or states[-1] != state:
                states.append(state)
            remaining_s = limits.per_image_timeout_s - (self.clock() - start)
            if remaining_s <= 0:
                raise AgentError("IMAGE_TIMEOUT")
            calls = len(observations)
            for maximum, code in (
                (limits.max_tool_calls, "TOOL_CALL_LIMIT"),
                (limits.max_model_calls, "MODEL_CALL_LIMIT"),
                (limits.max_iterations, "ITERATION_LIMIT"),
                (limits.max_memory_entries, "MEMORY_LIMIT"),
            ):
                if calls >= maximum:
                    raise AgentError(code)
            remaining_tokens = limits.max_total_output_tokens - total_tokens
            if remaining_tokens <= 0:
                raise AgentError("OUTPUT_LIMIT")
            prompt = PROMPTS[prompt_id] + (claim or "")
            # Mock has no tokenizer. UTF-8 bytes are a conservative engineering proxy,
            # not a claim about Moondream tokenization; real adapter must tokenize.
            if self.adapter.is_mock and len(prompt.encode("utf-8")) > limits.max_input_tokens:
                raise AgentError("INPUT_TOKEN_LIMIT")
            request = Request(
                "caption" if prompt_id == "caption" else "query",
                prompt_id,
                prompt,
                min(limits.max_output_tokens, remaining_tokens),
                claim,
            )
            call_id = f"call-{calls + 1}"
            answer = None
            try:
                if request.tool not in self.adapter.capabilities:
                    raise AgentError("UNSUPPORTED_TOOL")
                assert image is not None
                call_start = self.clock()
                answer = self.executor.invoke(
                    request, image, min(remaining_s, limits.per_call_timeout_s)
                )
                if self.clock() - start >= limits.per_image_timeout_s:
                    raise AgentError("IMAGE_TIMEOUT")
                if self.clock() - call_start >= limits.per_call_timeout_s:
                    raise AgentError("TOOL_TIMEOUT")
                validate_answer(answer, limits, remaining_tokens)
                total_tokens += answer.output_tokens
            except AgentError as exc:
                observations.append(Observation(call_id, state, request, None, exc.code))
                raise
            except Exception as exc:
                observations.append(Observation(call_id, state, request, None, "TOOL_FAILURE"))
                raise AgentError("TOOL_FAILURE") from exc
            observations.append(Observation(call_id, state, request, answer, None))
            if prompt_id != "verify":
                for text in answer.claims:
                    prior = next((i for i, c in enumerate(claims) if c.text == text), None)
                    if prior is not None:
                        claims[prior] = replace(
                            claims[prior],
                            observation_ids=claims[prior].observation_ids + (call_id,),
                        )
                    elif len(claims) >= limits.max_memory_entries:
                        raise AgentError("MEMORY_LIMIT")
                    else:
                        claims.append(
                            Claim(
                                text,
                                (call_id,),
                                status="model-proposed" if self.adapter.is_mock else "unresolved",
                            )
                        )
            return answer

        try:
            image = inspect_image(item, limits)
            initial = call("INITIAL_CAPTION", "caption")
            if method == Method.A:
                investigation_stop = "SINGLE_PASS"
            else:
                scene = call("SCENE_ANALYSIS", "scene")
                states.append("OBJECT_CHECK")
                needs_object = any(a.uncertain or "object" in a.missing for a in (initial, scene))
                obj = call("OBJECT_CHECK", "object") if method == Method.C or needs_object else None
                states.append("DETAIL_QUERY")
                needs_detail = any("detail" in a.missing for a in (initial, scene))
                needs_detail = needs_detail or (
                    obj is not None and (obj.uncertain or "detail" in obj.missing)
                )
                if method == Method.C or needs_detail:
                    before = len(claims)
                    call("DETAIL_QUERY", "detail")
                    investigation_stop = (
                        "NO_NEW_EVIDENCE" if len(claims) == before else "QUERY_SET_DONE"
                    )
                else:
                    investigation_stop = "NO_TRIGGER"
                if method in (Method.C, Method.D):
                    states.append("VERIFICATION")
                    # Verification never feeds back into the investigation; B/D contrast.
                    for index, candidate in enumerate(tuple(claims)):
                        answer = call("VERIFICATION", "verify", candidate.text)
                        claims[index] = replace(
                            candidate,
                            status=answer.verdict,
                            verification_id=observations[-1].call_id,
                        )
            reason = "COMPLETED"
            status = "complete"
        except AgentError as exc:
            reason = exc.code
            status = "partial" if any(o.answer is not None for o in observations) else "failed"
        states.extend(("REPORT", "STOP"))
        return Report(
            str(uuid4()),
            item.input_id,
            method,
            status,
            reason,
            investigation_stop,
            image,
            tuple(observations),
            tuple(claims),
            tuple(states),
            limits,
            model_id=self.adapter.model_id,
            model_revision=self.adapter.revision,
            evidence_kind="MOCK_NOT_RESEARCH_EVIDENCE"
            if self.adapter.is_mock
            else "REAL_LOCAL_DEVELOPMENT_NOT_FORMAL_THESIS_RESULT",
        )

    def run_batch(self, items: list[ImageInput], method: Method) -> tuple[Report, ...]:
        """Sequential, fresh memory per image. Stop batch on execution failures."""
        if not items or len(items) > self.limits.max_batch_images:
            raise AgentError("BATCH_LIMIT")
        if len({item.input_id for item in items}) != len(items):
            raise AgentError("DUPLICATE_INPUT_ID")
        reports: list[Report] = []
        halted = False
        for item in items:
            if halted:
                reports.append(
                    Report(
                        str(uuid4()),
                        item.input_id,
                        method,
                        "not_attempted",
                        "BATCH_HALTED",
                        "NOT_STARTED",
                        None,
                        (),
                        (),
                        ("START", "REPORT", "STOP"),
                        self.limits,
                    )
                )
                continue
            report = self.run(item, method)
            reports.append(report)
            halted = report.stop_reason in {
                "TOOL_TIMEOUT",
                "IMAGE_TIMEOUT",
                "CLEANUP_FAILED",
                "TOOL_FAILURE",
            }
        return tuple(reports)
