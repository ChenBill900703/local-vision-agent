"""Fail-closed GPU memory checks for an 8 GiB local workstation.

This module intentionally has no PyTorch dependency. It can reject unsafe model
loading options before a heavyweight framework or model allocates memory.
"""

from __future__ import annotations

import json
import re
import subprocess
from collections.abc import Mapping
from dataclasses import asdict, dataclass
from typing import Any


class GpuSafetyError(RuntimeError):
    """Raised when a requested workload violates the GPU safety policy."""


class OffloadForbiddenError(GpuSafetyError):
    """Raised when configuration could move model state to CPU or disk."""


def _integer(value: object, name: str, minimum: int = 0) -> None:
    """Reject bool, NaN, infinity and non-integral memory/device values."""
    if type(value) is not int or value < minimum:
        raise ValueError(f"{name} must be an integer >= {minimum}")


@dataclass(frozen=True, slots=True)
class GpuPolicy:
    """Budget thresholds; not an allocator or driver-level memory limit."""

    max_process_reserved_mib: int = 6400
    min_free_before_load_mib: int = 1536

    def __post_init__(self) -> None:
        _integer(self.max_process_reserved_mib, "max_process_reserved_mib", 1)
        _integer(self.min_free_before_load_mib, "min_free_before_load_mib", 1)


@dataclass(frozen=True, slots=True)
class ModelMemorySpec:
    """Conservative peak-memory estimate for one model execution path."""

    name: str
    estimated_peak_vram_mib: int

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("model name must not be empty")
        _integer(self.estimated_peak_vram_mib, "estimated_peak_vram_mib", 1)


@dataclass(frozen=True, slots=True)
class GpuSnapshot:
    """One `nvidia-smi` memory observation."""

    name: str
    total_mib: int
    used_mib: int
    free_mib: int
    gpu_index: int = 0

    def __post_init__(self) -> None:
        _integer(self.gpu_index, "gpu_index")
        _integer(self.total_mib, "total_mib", 1)
        _integer(self.used_mib, "used_mib")
        _integer(self.free_mib, "free_mib")
        if not isinstance(self.name, str) or not self.name.strip():
            raise ValueError("GPU name must be nonempty")
        if self.used_mib + self.free_mib > self.total_mib:
            raise ValueError("GPU used + free memory exceeds total")


def _is_explicit_cuda(device: Any) -> bool:
    return (type(device) is int and device >= 0) or (
        isinstance(device, str) and re.fullmatch(r"cuda:[0-9]+", device) is not None
    )


def assert_no_offload_options(options: Mapping[str, Any], gpu_index: int = 0) -> None:
    """Reject Transformers-style options that enable CPU or disk fallback."""

    _integer(gpu_index, "gpu_index")
    if not isinstance(options, Mapping):
        raise OffloadForbiddenError("load options must be a mapping")
    quantization = options.get("quantization_config")
    if quantization is not None:
        if not isinstance(quantization, Mapping):
            raise OffloadForbiddenError("opaque quantization configuration is not supported")
        if "quantization_config" in quantization:
            raise OffloadForbiddenError("nested quantization configuration is not supported")
        assert_no_offload_options(quantization, gpu_index)
    # No map is permitted for adapters which explicitly move their model to CUDA.
    # The future loader must still validate actual placement after loading.
    if "device_map" in options:
        device_map = options["device_map"]
        values = tuple(device_map.values()) if isinstance(device_map, Mapping) else (device_map,)
        if not values or not all(_is_explicit_cuda(value) for value in values):
            raise OffloadForbiddenError("device_map must specify explicit CUDA indices only")
        if any(value not in (gpu_index, f"cuda:{gpu_index}") for value in values):
            raise OffloadForbiddenError("device_map does not match the checked GPU")

    for key in (
        "offload_folder",
        "offload_dir",
        "offload_state_dict",
        "offload_buffers",
        "llm_int8_enable_fp32_cpu_offload",
    ):
        value = options.get(key)
        if value not in (None, False, ""):
            raise OffloadForbiddenError(f"{key} is forbidden by the no-offload policy")

    max_memory = options.get("max_memory")
    if max_memory is not None and (
        not isinstance(max_memory, Mapping)
        or not max_memory
        or not all(
            _is_explicit_cuda(device) and device in (gpu_index, f"cuda:{gpu_index}")
            for device in max_memory
        )
    ):
        raise OffloadForbiddenError("max_memory must specify explicit CUDA indices only")
    if isinstance(max_memory, Mapping):
        non_gpu_targets = {
            str(device).lower()
            for device, limit in max_memory.items()
            if limit not in (None, 0, "0", "0MiB", "0GiB")
            and str(device).lower() in {"cpu", "disk"}
        }
        if non_gpu_targets:
            raise OffloadForbiddenError(
                f"max_memory enables forbidden targets: {sorted(non_gpu_targets)}"
            )


def query_gpu_snapshot(gpu_index: int = 0) -> GpuSnapshot:
    """Read one GPU snapshot from NVIDIA SMI."""

    _integer(gpu_index, "gpu_index")
    command = [
        "nvidia-smi",
        f"--id={gpu_index}",
        "--query-gpu=name,memory.total,memory.used,memory.free",
        "--format=csv,noheader,nounits",
    ]
    try:
        completed = subprocess.run(
            command,
            check=True,
            capture_output=True,
            text=True,
            timeout=10,
        )
        lines = completed.stdout.strip().splitlines()
        if len(lines) != 1:
            raise ValueError("expected exactly one GPU row")
        name, total, used, free = (part.strip() for part in lines[0].split(",", maxsplit=3))
        return GpuSnapshot(
            name=name,
            total_mib=int(total),
            used_mib=int(used),
            free_mib=int(free),
            gpu_index=gpu_index,
        )
    except (OSError, subprocess.SubprocessError, ValueError) as error:
        raise GpuSafetyError(f"Cannot verify GPU {gpu_index}: {error}") from error


class GpuGuard:
    """Checks estimates and supplied measurements; does not reserve GPU memory.

    Real adapters still need allocator limits, placement checks, bounded inputs,
    OOM handling and process isolation. Snapshots cannot prevent concurrent GPU use.
    """

    def __init__(self, policy: GpuPolicy | None = None, gpu_index: int = 0) -> None:
        _integer(gpu_index, "gpu_index")
        self.policy = policy or GpuPolicy()
        self.gpu_index = gpu_index

    def preflight(
        self,
        model: ModelMemorySpec,
        snapshot: GpuSnapshot | None = None,
        load_options: Mapping[str, Any] | None = None,
    ) -> GpuSnapshot:
        """Fail before loading when the estimate or current free VRAM is unsafe."""

        assert_no_offload_options({} if load_options is None else load_options, self.gpu_index)
        current = snapshot or query_gpu_snapshot(self.gpu_index)
        if current.gpu_index != self.gpu_index:
            raise GpuSafetyError("snapshot does not match the checked GPU")

        if model.estimated_peak_vram_mib > self.policy.max_process_reserved_mib:
            raise GpuSafetyError(
                f"{model.name} estimates {model.estimated_peak_vram_mib} MiB, above the "
                f"{self.policy.max_process_reserved_mib} MiB process ceiling"
            )

        required_free = model.estimated_peak_vram_mib + self.policy.min_free_before_load_mib
        if current.free_mib < required_free:
            raise GpuSafetyError(
                f"{model.name} requires at least {required_free} MiB free by policy, "
                f"but GPU {current.name} has {current.free_mib} MiB free"
            )
        return current

    def assert_runtime_reserved(self, reserved_mib: int) -> None:
        """Check a supplied measurement; callers must obtain it from the allocator."""

        _integer(reserved_mib, "reserved_mib")
        if reserved_mib > self.policy.max_process_reserved_mib:
            raise GpuSafetyError(
                f"runtime reserved VRAM {reserved_mib} MiB exceeds the "
                f"{self.policy.max_process_reserved_mib} MiB ceiling"
            )


def main() -> None:
    snapshot = query_gpu_snapshot()
    print(json.dumps(asdict(snapshot), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
