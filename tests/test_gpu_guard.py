from __future__ import annotations

import subprocess
import unittest
from unittest.mock import patch

from local_vision_agent.gpu_guard import (
    GpuGuard,
    GpuPolicy,
    GpuSafetyError,
    GpuSnapshot,
    ModelMemorySpec,
    OffloadForbiddenError,
    assert_no_offload_options,
    query_gpu_snapshot,
)


class GpuGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        self.guard = GpuGuard(
            GpuPolicy(max_process_reserved_mib=6400, min_free_before_load_mib=1536)
        )
        self.snapshot = GpuSnapshot(
            name="RTX 3070 Ti",
            total_mib=8192,
            used_mib=512,
            free_mib=7680,
        )

    def test_accepts_model_inside_budget(self) -> None:
        model = ModelMemorySpec("clip", 1800)
        result = self.guard.preflight(model, snapshot=self.snapshot, load_options={"device_map": 0})
        self.assertEqual(result, self.snapshot)

    def test_rejects_model_above_process_ceiling(self) -> None:
        model = ModelMemorySpec("oversized", 7000)
        with self.assertRaises(GpuSafetyError):
            self.guard.preflight(model, snapshot=self.snapshot)

    def test_rejects_model_when_free_memory_is_insufficient(self) -> None:
        model = ModelMemorySpec("vlm", 6200)
        with self.assertRaises(GpuSafetyError):
            self.guard.preflight(model, snapshot=self.snapshot)

    def test_rejects_auto_device_map(self) -> None:
        with self.assertRaises(OffloadForbiddenError):
            assert_no_offload_options({"device_map": "auto"})

    def test_rejects_cpu_in_device_map(self) -> None:
        with self.assertRaises(OffloadForbiddenError):
            assert_no_offload_options({"device_map": {"encoder": 0, "decoder": "cpu"}})

    def test_rejects_offload_folder(self) -> None:
        with self.assertRaises(OffloadForbiddenError):
            assert_no_offload_options({"device_map": 0, "offload_folder": "cache"})

    def test_rejects_cpu_max_memory(self) -> None:
        with self.assertRaises(OffloadForbiddenError):
            assert_no_offload_options({"max_memory": {0: "6GiB", "cpu": "24GiB"}})

    def test_runtime_ceiling_is_enforced(self) -> None:
        with self.assertRaises(GpuSafetyError):
            self.guard.assert_runtime_reserved(6401)

    def test_only_explicit_cuda_maps_are_accepted(self) -> None:
        for value in ("balanced", "balanced_low_0", "sequential", None, {}, True, -1, "cuda"):
            with self.subTest(value=value), self.assertRaises(OffloadForbiddenError):
                assert_no_offload_options({"device_map": value})
        for value in (0, "cuda:0", {"": "cuda:0"}):
            assert_no_offload_options({"device_map": value})

    def test_offload_buffers_are_rejected(self) -> None:
        with self.assertRaises(OffloadForbiddenError):
            assert_no_offload_options({"offload_buffers": True})

    def test_invalid_memory_numbers_fail_closed(self) -> None:
        for value in (True, float("nan"), float("inf"), -1, 1.5, "100"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    ModelMemorySpec("model", value)
                with self.assertRaises(ValueError):
                    GpuPolicy(value)
                with self.assertRaises(ValueError):
                    self.guard.assert_runtime_reserved(value)
                with self.assertRaises(ValueError):
                    GpuSnapshot("gpu", 8192, 0, value)
        self.guard.assert_runtime_reserved(0)

    def test_inconsistent_snapshot_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            GpuSnapshot("gpu", 8192, 100, 8192)

    def test_device_must_match_snapshot_and_loader(self) -> None:
        with self.assertRaises(OffloadForbiddenError):
            self.guard.preflight(
                ModelMemorySpec("model", 100),
                snapshot=self.snapshot,
                load_options={"device_map": 1},
            )
        with self.assertRaises(GpuSafetyError):
            GpuGuard(gpu_index=1).preflight(
                ModelMemorySpec("model", 100),
                snapshot=self.snapshot,
            )

    def test_nested_and_opaque_offload_are_rejected(self) -> None:
        for config in (
            {"llm_int8_enable_fp32_cpu_offload": True},
            {"device_map": "auto"},
            {"quantization_config": {}},
            object(),
        ):
            with self.subTest(config=config), self.assertRaises(OffloadForbiddenError):
                assert_no_offload_options({"quantization_config": config})
        assert_no_offload_options({"quantization_config": {"load_in_4bit": True}})

    def test_bad_smi_output_is_a_safety_error(self) -> None:
        for output in ("", "gpu, N/A, 0, 0", "gpu, 8192, 0, 8192\ngpu, 8192, 0, 8192"):
            with (
                patch(
                    "local_vision_agent.gpu_guard.subprocess.run",
                    return_value=subprocess.CompletedProcess([], 0, stdout=output),
                ),
                self.assertRaises(GpuSafetyError),
            ):
                query_gpu_snapshot()

    def test_smi_failure_is_a_safety_error(self) -> None:
        for error in (FileNotFoundError(), subprocess.TimeoutExpired("nvidia-smi", 10)):
            with (
                patch(
                    "local_vision_agent.gpu_guard.subprocess.run",
                    side_effect=error,
                ),
                self.assertRaises(GpuSafetyError),
            ):
                query_gpu_snapshot()

    def test_smi_preserves_gpu_identity(self) -> None:
        with patch(
            "local_vision_agent.gpu_guard.subprocess.run",
            return_value=subprocess.CompletedProcess([], 0, stdout="gpu, 8192, 512, 7680"),
        ) as run:
            self.assertEqual(query_gpu_snapshot(1).gpu_index, 1)
            self.assertIn("--id=1", run.call_args.args[0])


if __name__ == "__main__":
    unittest.main()
