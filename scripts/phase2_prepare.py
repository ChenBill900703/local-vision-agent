"""Prepare an auditable local source copy and synthetic development fixture; no GPU."""

import ast
import difflib
import hashlib
import importlib.metadata
import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1] / "artifacts" / "phase2-20260927"
SOURCE = ROOT / "upstream" / "model"
DEST = ROOT / "controlled" / "md2_fixed"
LABEL = "PILOT / EXPLORATORY / NOT FORMAL THESIS RESULT"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def main() -> None:
    if DEST.exists():
        raise RuntimeError("Refuse overwrite of controlled code")
    DEST.mkdir(parents=True)
    changes = []
    manifest = {
        "label": LABEL,
        "upstream_revision": "9a7d4024050840e001defacec2b00727e89149e6",
        "files": {},
    }
    imports = {}
    for path in sorted(SOURCE.glob("*.py")):
        if path.name in {"hf_moondream.py", "weights.py", "fourier_features.py"}:
            continue
        original = path.read_bytes()
        receipt = json.loads(path.with_name(path.name + ".receipt.json").read_text())
        if sha(original) != receipt["sha256"]:
            raise RuntimeError("Upstream hash changed")
        code = original.decode("utf8")
        imports[path.name] = [
            ast.unparse(n)
            for n in ast.walk(ast.parse(code))
            if isinstance(n, (ast.Import, ast.ImportFrom))
        ]
        if path.name == "moondream.py":
            old = 'Tokenizer.from_pretrained("moondream/starmie-v1")'
            assert code.count(old) == 1
            code = "from pathlib import Path\n" + code.replace(
                old, 'Tokenizer.from_file(str(Path(__file__).with_name("tokenizer.json")))'
            )
            code = code.replace(
                "torch._dynamo.mark_dynamic(all_crops, 0)",
                "# Pilot: compilation disabled; no dynamo marking",
            )
            code = code.replace(
                "torch._dynamo.mark_dynamic(prompt_emb, 1)",
                "# Pilot: compilation disabled; no dynamo marking",
            )
            code = code.replace(
                "        def generator(next_token, pos):\n",
                "        def generator(next_token, pos):\n"
                "            self._pilot_generated_token_ids = []\n",
            )
            code = code.replace(
                "                token_cache.append(next_token_id)\n",
                "                token_cache.append(next_token_id)\n"
                "                self._pilot_generated_token_ids.append(next_token_id)\n",
            )
        elif path.name == "lora.py":
            code = (
                '"""Pilot: all variants disabled, no network or torch.load path."""\n'
                'def variant_state_dict(variant_id=None, device="cuda:0"):\n'
                "    if variant_id is not None:\n"
                '        raise RuntimeError("Variants are not authorized")\n'
                "    return None\n"
            )
        elif path.name == "image_crops.py":
            start, end = code.index("try:\n"), code.index("\ndef select_tiling")
            code = code[:start] + "from PIL import Image\nHAS_VIPS = False\n\n" + code[end:]
        elif path.name == "layers.py":
            start, end = code.index("try:\n"), code.index("\ndef gelu_approx")
            code = (
                code[:start]
                + (
                    "def quantize_(*args, **kwargs):\n"
                    '    raise RuntimeError("Quantization is not authorized")\n\n'
                    "def int4_weight_only(*args, **kwargs):\n"
                    '    raise RuntimeError("Quantization is not authorized")\n\n'
                )
                + code[end:]
            )
        elif path.name == "vision.py":
            start, end = (
                code.index("if torch.backends.mps.is_available():"),
                code.index("DeviceLike ="),
            )
            code = code[:start] + "adaptive_avg_pool2d = F.adaptive_avg_pool2d\n\n" + code[end:]
        ast.parse(code)
        (DEST / path.name).write_text(code, encoding="utf8", newline="\n")
        manifest["files"][path.name] = sha(code.encode())
        changes.extend(
            difflib.unified_diff(
                original.decode().splitlines(True),
                code.splitlines(True),
                fromfile="upstream/" + path.name,
                tofile="controlled/" + path.name,
            )
        )
    (DEST / "__init__.py").write_text("", encoding="utf8")
    manifest["files"]["__init__.py"] = sha(b"")
    tok = ROOT / "upstream" / "tokenizer" / "tokenizer.json"
    tokenizer_bytes = tok.read_bytes()
    assert (
        sha(tokenizer_bytes)
        == json.loads(tok.with_name(tok.name + ".receipt.json").read_text())["sha256"]
    )
    (DEST / "tokenizer.json").write_bytes(tokenizer_bytes)
    manifest["files"]["tokenizer.json"] = sha(tokenizer_bytes)
    patch_bytes = "".join(changes).encode()
    (ROOT / "evidence" / "controlled.patch").write_bytes(patch_bytes)
    manifest["patch_sha256"] = sha(patch_bytes)
    for filename, data in (
        ("controlled_manifest.json", manifest),
        ("upstream_imports.json", imports),
    ):
        (ROOT / "evidence" / filename).write_text(json.dumps(data, indent=2), encoding="utf8")
    packages = {}
    for package in (
        "torch",
        "transformers",
        "numpy",
        "Pillow",
        "tokenizers",
        "safetensors",
        "accelerate",
        "einops",
        "pyvips",
        "pyvips-binary",
        "torchao",
    ):
        try:
            packages[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            packages[package] = "NOT INSTALLED"
    (ROOT / "evidence" / "dependencies.json").write_text(json.dumps(packages, indent=2))
    images = ROOT / "development"
    images.mkdir()
    image = Image.new("RGB", (384, 256), "white")
    draw = ImageDraw.Draw(image)
    draw.rectangle((30, 60, 130, 160), fill="red")
    draw.ellipse((230, 60, 330, 160), fill="blue")
    path = images / "synthetic_shapes.png"
    image.save(path)
    image.close()
    (ROOT / "evidence" / "development_manifest.json").write_text(
        json.dumps(
            {
                "label": LABEL,
                "source": "Project-generated simple geometric CPU fixture; no external image",
                "rights": "Generated locally for this authorized technical pilot; no personal data",
                "split": "development-only; never untouched formal test",
                "images": [
                    {
                        "id": "synthetic-shapes-v1",
                        "path": str(path.resolve()),
                        "sha256": sha(path.read_bytes()),
                        "width": 384,
                        "height": 256,
                    }
                ],
            },
            indent=2,
        ),
        encoding="utf8",
    )
    print(json.dumps({"controlled_manifest": manifest, "dependencies": packages}, indent=2))


if __name__ == "__main__":
    main()
