"""CPU-only safety/transport fixtures, not image-recognition evidence."""

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from dataclasses import asdict, replace
from pathlib import Path
from unittest.mock import patch

from local_vision_agent.capability_gate import (
    OPERATIONS,
    RUN_ID,
    CapabilityTransport,
    ExecutionReceipt,
    validate_receipt,
)
from local_vision_agent.gpu_guard import GpuSnapshot
from local_vision_agent.pilot_ipc import Deadlines
from local_vision_agent.pilot_policy import PilotBudget, PilotLimits, PilotRefusal
from local_vision_agent.pilot_supervisor_repair import run


def receipt(text: str = "模型輸出") -> ExecutionReceipt:
    return ExecutionReceipt(
        text, True, True, "completed", None, 320, 20, 20, 1, 1, 1, 1.0, 2.0, 30.0, 4700.0, 2300.0
    )


class CapabilityGateTests(unittest.TestCase):
    def test_wording_is_not_a_safety_decision(self) -> None:
        for raw in (
            "A red square on the left, blue circle on the right.",
            "這張圖片顯示了一個紅色正方形。",
            "完全不同的措辭",
            "答案不正確仍需人工評閱",
            "I am uncertain.",
            "可能無法確認",
            "blue square and red circle",
        ):
            validate_receipt(asdict(receipt(raw)), PilotLimits())

    def test_empty_and_malformed_output_stop(self) -> None:
        for raw in ("", " \n", "\ufffd", "\ud800", None, {}, 5):
            with self.subTest(raw=repr(raw)), self.assertRaises(PilotRefusal):
                replace(receipt(), response=raw).validate(PilotLimits())
        for value in (None, [], {}, {**asdict(receipt()), "extra": True}):
            with self.assertRaises(PilotRefusal):
                validate_receipt(value, PilotLimits())

    def test_exception_decode_and_unhealthy_transport_stop(self) -> None:
        for change in (
            {"error": "model exception"},
            {"worker_healthy": False},
            {"decoded": False},
            {"transport": "pending"},
            {"worker_healthy": 1},
        ):
            with self.assertRaises(PilotRefusal):
                replace(receipt(), **change).validate(PilotLimits())

    def test_timeout_and_memory_stop(self) -> None:
        for change in (
            {"elapsed_s": 61},
            {"image_elapsed_s": 301},
            {"session_elapsed_s": 1801},
            {"elapsed_s": float("nan")},
            {"reserved_mib": 5401},
            {"free_mib": 1535},
            {"free_mib": None},
        ):
            with self.assertRaises(PilotRefusal):
                replace(receipt(), **change).validate(PilotLimits())

    def test_token_call_image_overflow_stop(self) -> None:
        for change in (
            {"input_tokens": 1025},
            {"output_tokens": 129},
            {"image_output_tokens": 1025},
            {"calls": 25},
            {"image_calls": 9},
            {"images": 4},
            {"calls": True},
        ):
            with self.assertRaises(PilotRefusal):
                replace(receipt(), **change).validate(PilotLimits())
        budget = PilotBudget(PilotLimits())
        budget.start_image()
        for _ in range(8):
            budget.before_call(320, 128)
            budget.after_call(128)
        with self.assertRaises(PilotRefusal):
            budget.before_call(320, 128)

    def test_missing_limits_and_late_result_fail_closed(self) -> None:
        with self.assertRaises(PilotRefusal):
            receipt().validate(None)
        deadlines = Deadlines(0, PilotLimits(), loaded=True)
        deadlines.observe({"phase": "call_start", "monotonic": 1})
        with self.assertRaises(PilotRefusal):
            deadlines.check(62)

    def test_unexpected_transport_and_exception_stop(self) -> None:
        for event in (
            {"phase": "unknown"},
            {"phase": "call_done"},
            {"phase": "worker_done", "exit_code": 0},
        ):
            with self.assertRaises(PilotRefusal):
                CapabilityTransport(PilotLimits()).observe(event)
        state = CapabilityTransport(PilotLimits())
        state.observe({"phase": "failure"})
        with self.assertRaises(PilotRefusal):
            state.observe({"phase": "model_loaded"})

    @unittest.skipUnless(os.name == "nt", "Windows persistent process lifecycle")
    def test_real_cpu_worker_five_queries_one_load_and_timeout(self) -> None:
        real_popen = subprocess.Popen
        for hang in (False, True):
            with self.subTest(hang=hang), tempfile.TemporaryDirectory() as directory:
                source = (
                    "import os,sys,time,json\n"
                    "from dataclasses import asdict\n"
                    "from local_vision_agent.capability_gate import OPERATIONS,ExecutionReceipt\n"
                    "def emit(phase,**kw):\n"
                    " print(json.dumps(dict(phase=phase,pid=os.getpid(),monotonic=time.monotonic(),**kw)),flush=True)\n"
                    "emit('ready'); assert sys.stdin.readline().strip()=='GO'\n"
                    "emit('load_start'); emit('model_loaded'); emit('image_start'); emit('image_ready')\n"
                    "for i,(name,prompt) in enumerate(OPERATIONS):\n"
                    " emit('call_start',operation=name,prompt=prompt)\n"
                    + (" time.sleep(30)\n" if hang else "")
                    + " r=ExecutionReceipt('left right 了',True,True,'completed',None,320,20,(i+1)*20,i+1,i+1,1,0.01,0.1,0.1,4700.,2300.)\n"
                    " emit('call_done',operation=name,raw_response=r.response,execution_receipt=asdict(r))\n"
                    "emit('pilot_complete'); emit('cleanup_start')\n"
                    "emit('cleanup_done',allocator_empty=True,measurement={'allocated_bytes':0,'reserved_bytes':0})\n"
                    "emit('worker_done',exit_code=0)\n"
                )

                def launch(command, fixture=source, **kwargs):
                    if "local_vision_agent.internvl_worker" in command:
                        self.assertIn("--capability", command)
                        command = [sys.executable, "-B", "-c", fixture]
                    return real_popen(command, **kwargs)

                with (
                    patch(
                        "local_vision_agent.pilot_supervisor_repair.subprocess.Popen",
                        side_effect=launch,
                    ),
                    patch(
                        "local_vision_agent.pilot_supervisor_repair.query_gpu_snapshot",
                        return_value=GpuSnapshot("CPU fixture", 8192, 200, 7800),
                    ),
                    patch(
                        "local_vision_agent.pilot_supervisor_repair.windows_memory", return_value={}
                    ),
                    patch(
                        "local_vision_agent.pilot_supervisor_repair.PilotLimits",
                        return_value=replace(PilotLimits(), call_s=0.2, load_s=5, cleanup_s=2),
                    ),
                    patch("sys.stdout", io.StringIO()),
                ):
                    code = run(Path(directory), True, capability=True)
                root = Path(directory) / "runs" / RUN_ID
                result = json.loads((root / "supervisor_result.json").read_text())
                self.assertEqual(code, 1 if hang else 0)
                self.assertTrue(result["job_empty"])
                self.assertTrue(result["worker_exited"])
                if not hang:
                    events = [
                        json.loads(x)
                        for x in (root / "pipe_events.jsonl")
                        .read_text(encoding="utf8")
                        .splitlines()
                    ]
                    self.assertEqual(sum(e["phase"] == "model_loaded" for e in events), 1)
                    self.assertEqual(
                        [e["operation"] for e in events if e["phase"] == "call_done"],
                        [name for name, _ in OPERATIONS],
                    )


if __name__ == "__main__":
    unittest.main()
