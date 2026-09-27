"""Version-checked PyTorch workspace cleanup, invoked only after model release."""

from typing import Any


def clear_workspaces(torch: Any) -> dict[str, Any]:
    torch.cuda.synchronize(0)
    before = torch.cuda.memory_allocated(0)
    clear = getattr(torch._C, "_cuda_clearCublasWorkspaces", None)
    if not callable(clear):
        raise RuntimeError("CUBLAS_CLEANUP_API_UNAVAILABLE")  # noqa: TRY004 -- missing runtime capability
    clear()
    torch.cuda.empty_cache()
    torch.cuda.synchronize(0)
    return {
        "api": "torch._C._cuda_clearCublasWorkspaces",
        "torch_version": torch.__version__,
        "before_allocated_bytes": before,
        "after_allocated_bytes": torch.cuda.memory_allocated(0),
    }
