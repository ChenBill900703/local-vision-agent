"""Frozen InternVL development pilot contracts; imports no model or CUDA code."""

import json
import re
from pathlib import Path
from typing import Any

from .pilot_policy import PilotRefusal, hash_file

RUN_ID = "INTERNVL3_INITIAL_GPU_PILOT"
REVISION = "f6c7b60375759170fd49f5e9e298e2178485c5ba"
WEIGHT_HASH = "b69fcfb5cd97b91b52022642d88da91201487aa73750fa8b14a0e6591a5a9e2d"
CORE = (
    ("A_english", "What shapes are in the image, and what color is each shape?"),
    ("B_direct_zh", "圖片中有哪些形狀？它們分別是什麼顏色？請只使用繁體中文回答。"),
    ("C_caption_zh", "請使用繁體中文簡潔描述這張圖片的主要內容。"),
    (
        "D_instruction_zh",
        "Answer in Traditional Chinese only. Describe the main visible contents of this image.",
    ),
)
PROBES = (
    ("scene", "這張圖片主要是什麼場景？"),
    ("objects", "請列出畫面中明顯可見的主要物件。"),
    ("detail", "背景中還有哪些明顯且可以確認的物件？"),
    (
        "verification",
        "敘述：圖片中有紅色正方形。請重新檢查圖片，這個敘述是否能由圖片直接支持？若不能確定，請明確說無法確定。",
    ),
)


def probe_gate(answers: dict[str, str]) -> bool:
    """Conservative fixture-only lexical gate, never a thesis quality metric.

    Refuse uncertain phrasing, unsupported characters, simplified characters,
    conflicting color pairs and echoes. The verification claim must occur in C.
    """
    if set(answers) != {name for name, _ in CORE}:
        return False
    english = answers["A_english"].lower()
    if not re.search(r"red\s+square", english) or not re.search(r"blue\s+circle", english):
        return False
    if any(x in english for x in ("not", "maybe", "blue square", "red circle", "?")):
        return False
    allowed_english = {
        "the",
        "image",
        "contains",
        "shows",
        "has",
        "two",
        "shapes",
        "a",
        "red",
        "square",
        "and",
        "blue",
        "circle",
        "on",
        "white",
        "background",
        "there",
        "are",
        "in",
        "one",
        "of",
        "is",
        "color",
        "colored",
        "colours",
        "colors",
        "following",
        "visible",
    }
    if not set(re.findall(r"[a-z]+", english)) <= allowed_english:
        return False
    # Only common fixture-description words are admitted; unfamiliar content skips probes.
    allowed = set(
        "圖片中有一個兩種形狀紅色的正方形和與及藍色圓形白背景在左邊右上下分別是為呈現顯示看到可以我們這張主要內容簡單幾何組成於佈置空間中心中央由各自並且、，。：「」；（） \n\t1234567890.-*："
    )
    for name, prompt in CORE[1:]:
        value = answers[name]
        if prompt in value or not set(value) <= allowed:
            return False
        if not re.search(r"紅色的?正方形", value) or not re.search(r"藍色的?圓形", value):
            return False
        if any(x in value for x in ("藍色正方形", "紅色圓形", "藍色的正方形", "紅色的圓形")):
            return False
    return True


def validate_assets(root: Path, project: Path) -> dict[str, Any]:
    manifest: dict[str, Any] = json.loads(
        (root / "evidence/runtime_manifest.json").read_text(encoding="utf8")
    )
    if manifest.get("revision") != REVISION:
        raise PilotRefusal("INTERNVL_REVISION")
    files = manifest.get("files", {})
    required = {
        "upstream/instruct/model.safetensors",
        "upstream/instruct/config.json",
        "upstream/instruct/tokenizer.json",
        "controlled/iv3_fixed/modeling_internvl_chat.py",
        "controlled/iv3_fixed/modeling_intern_vit.py",
        "controlled/iv3_fixed/conversation.py",
    }
    if not required <= files.keys() or files["upstream/instruct/model.safetensors"] != WEIGHT_HASH:
        raise PilotRefusal("INTERNVL_REQUIRED_ASSETS")
    for name, expected in files.items():
        path = (root / name).resolve()
        if not path.is_relative_to(root.resolve()) or hash_file(path) != expected:
            raise PilotRefusal("INTERNVL_ASSET_HASH_OR_PATH:" + name)
    if hash_file(root / "evidence/controlled.patch") != manifest["patch_sha256"]:
        raise PilotRefusal("INTERNVL_PATCH_HASH")
    library = project / ".venv/Lib/site-packages/transformers"
    for name, expected in manifest["transformers_code"].items():
        path = (library / name).resolve()
        if not path.is_relative_to(library.resolve()) or hash_file(path) != expected:
            raise PilotRefusal("TRANSFORMERS_CODE_HASH")
    return manifest
