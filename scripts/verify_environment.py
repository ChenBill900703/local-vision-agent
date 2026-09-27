"""CPU-only installation smoke check; never downloads weights or initializes CUDA."""

from __future__ import annotations

import importlib.metadata
import io
import json
import sys


def main() -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import scipy
    import sklearn
    import torch
    import torchvision
    from PIL import Image
    from transformers import Dinov2Config, Dinov2Model

    # Import classes only: no from_pretrained, no model instantiation, no CUDA calls.
    assert Dinov2Config is not None and Dinov2Model is not None
    assert scipy.__version__ and sklearn.__version__
    assert torch.version.cuda == "12.6", "Expected pinned CUDA 12.6 wheel"
    assert not torch.cuda.is_initialized()
    assert (torch.ones(2, device="cpu") + 1).tolist() == [2, 2]
    boxes = torch.tensor([[0.0, 0.0, 1.0, 1.0]], device="cpu")
    assert torchvision.ops.nms(boxes, torch.tensor([0.9]), 0.5).tolist() == [0]
    assert torchvision.transforms.ToTensor()(Image.new("RGB", (8, 8))).shape == (3, 8, 8)
    assert pd.DataFrame({"value": np.array([1, 2])})["value"].sum() == 3
    figure, axis = plt.subplots()
    axis.plot([0, 1], [0, 1])
    buffer = io.BytesIO()
    figure.savefig(buffer, format="png")
    plt.close(figure)
    assert buffer.getbuffer().nbytes > 0
    assert not torch.cuda.is_initialized()
    packages = (
        "torch",
        "torchvision",
        "transformers",
        "numpy",
        "scipy",
        "scikit-learn",
        "pandas",
        "Pillow",
        "matplotlib",
    )
    print(
        json.dumps(
            {
                "kind": "cpu_installation_smoke_check_not_research_evidence",
                "python": sys.version.split()[0],
                "cuda_initialized": False,
                "versions": {name: importlib.metadata.version(name) for name in packages},
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
