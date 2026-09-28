"""Create reviewed local custom code and record exact patches without importing it."""

import ast
import difflib
import importlib.metadata
import json
import shutil
from pathlib import Path

from local_vision_agent.pilot_policy import hash_file


def main() -> None:
    project = Path(__file__).resolve().parents[1]
    root = project / "artifacts/internvl3-20260928"
    upstream = root / "upstream/instruct"
    package = root / "controlled/iv3_fixed"
    package.mkdir(parents=True, exist_ok=False)
    diffs = []
    for source in upstream.glob("*.py"):
        before = source.read_text(encoding="utf8")
        after = before
        if source.name == "modeling_intern_vit.py":
            after = after.replace("from einops import rearrange\n", "")
            after = after.replace("from timm.layers import DropPath\n", "")
            start = after.index("try:\n    from flash_attn")
            end = after.index("class InternRMSNorm")
            after = (
                after[:start]
                + """# Controlled pilot: only reviewed eager attention; no optional kernel imports.
has_flash_attn = False
logger = logging.get_logger(__name__)


def rearrange(*args, **kwargs):
    raise RuntimeError("FLASH_ATTENTION_DISABLED")


class DropPath(nn.Module):
    def __init__(self, *args, **kwargs):
        raise RuntimeError("NONZERO_DROP_PATH_FORBIDDEN")


"""
                + after[end:]
            )
            start = after.index("try:\n    from apex.normalization")
            end = after.index("NORM2FN =")
            after = after[:start] + "# Optional apex kernel substitution disabled.\n" + after[end:]
        ast.parse(after)
        (package / source.name).write_text(after, encoding="utf8")
        diffs.extend(
            difflib.unified_diff(
                before.splitlines(True),
                after.splitlines(True),
                fromfile=f"upstream/{source.name}",
                tofile=f"controlled/{source.name}",
            )
        )
    (package / "__init__.py").write_text("", encoding="utf8")
    patch = root / "evidence/controlled.patch"
    patch.write_text("".join(diffs), encoding="utf8")
    files = {
        str(p.relative_to(root)).replace("\\", "/"): hash_file(p)
        for base in (upstream, package)
        for p in base.iterdir()
        if p.is_file() and not p.name.endswith(".receipt.json")
    }
    installed = [
        "models/qwen2/modeling_qwen2.py",
        "models/qwen2/configuration_qwen2.py",
        "generation/utils.py",
        "cache_utils.py",
        "modeling_utils.py",
        "integrations/hub_kernels.py",
    ]
    library = project / ".venv/Lib/site-packages/transformers"
    code_hashes = {name: hash_file(library / name) for name in installed}
    manifest = {
        "repository": "OpenGVLab/InternVL3-2B-Instruct",
        "revision": "f6c7b60375759170fd49f5e9e298e2178485c5ba",
        "files": files,
        "patch_sha256": hash_file(patch),
        "transformers_code": code_hashes,
    }
    (root / "evidence/runtime_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf8"
    )
    versions = {}
    for name in (
        "torch",
        "torchvision",
        "transformers",
        "numpy",
        "Pillow",
        "safetensors",
        "tokenizers",
        "packaging",
        "einops",
        "timm",
        "accelerate",
        "kernels",
    ):
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = "NOT INSTALLED"
    (root / "evidence/dependencies.json").write_text(
        json.dumps(versions, indent=2), encoding="utf8"
    )
    shutil.copyfile(
        project / "artifacts/phase2-20260927/evidence/development_manifest.json",
        root / "evidence/development_manifest.json",
    )
    print(
        json.dumps({"patch_sha256": manifest["patch_sha256"], "dependencies": versions}, indent=2)
    )


if __name__ == "__main__":
    main()
