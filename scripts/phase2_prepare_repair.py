"""Create a separate, reviewable query-suffix comparison package; CPU only."""

import difflib
import json
import shutil
from pathlib import Path

from local_vision_agent.pilot_policy import hash_file, validate_assets


def patch_query(source: str) -> str:
    old = '            prompt_tokens[0] += self.config.tokenizer.templates["query"]["suffix"]'
    if source.count(old) != 1:
        raise ValueError("UPSTREAM_QUERY_CHANGED")
    return source.replace(
        old, '            if getattr(self, "_pilot_duplicate_query_suffix", True):\n    ' + old
    )


def main() -> None:
    root = Path(__file__).resolve().parents[1] / "artifacts/phase2-20260927"
    original = validate_assets(root)
    src = root / "controlled/md2_fixed"
    dest = root / "controlled-repair1/md2_fixed"
    dest.mkdir(parents=True, exist_ok=False)
    for name in original["files"]:
        shutil.copyfile(src / name, dest / name)
    before = (src / "moondream.py").read_text(encoding="utf8")
    after = patch_query(before)
    (dest / "moondream.py").write_text(after, encoding="utf8")
    diff = "".join(
        difflib.unified_diff(
            before.splitlines(True),
            after.splitlines(True),
            fromfile="controlled/moondream.py",
            tofile="controlled-repair1/moondream.py",
        )
    )
    patch = root / "evidence/controlled-repair1.patch"
    patch.write_text(diff, encoding="utf8")
    manifest = {
        **original,
        "parent_patch_sha256": original["patch_sha256"],
        "patch_sha256": hash_file(patch),
        "files": {name: hash_file(dest / name) for name in original["files"]},
        "amendment": "repair1: same model, original double suffix vs single suffix",
    }
    (root / "evidence/controlled_repair1_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf8"
    )
    print(diff)
    print("patch_sha256:", manifest["patch_sha256"])


if __name__ == "__main__":
    main()
