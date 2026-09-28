"""Bounded pinned InternVL static inspection/acquisition. No model imports or execution."""

import argparse
import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "bounded_fetch", Path(__file__).with_name("phase2_acquire.py")
)
assert spec and spec.loader
fetcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(fetcher)
ROOT = Path(__file__).resolve().parents[1] / "artifacts/internvl3-20260928"
fetcher.ROOT = ROOT
REPOS = {"hf": "OpenGVLab/InternVL3-2B-hf", "instruct": "OpenGVLab/InternVL3-2B-Instruct"}


def inspect() -> None:
    for name, repo in REPOS.items():
        path = ROOT / "evidence" / f"{name}_metadata.json"
        # Resolve main ONCE for discovery; every actual artifact URL uses returned full SHA.
        if not path.exists():
            fetcher.fetch(f"https://huggingface.co/api/models/{repo}?blobs=true", path, 2_000_000)
        meta = json.loads(path.read_text(encoding="utf8"))
        revision = meta["sha"]
        allow = []
        for item in meta["siblings"]:
            filename = item["rfilename"]
            if filename.endswith(
                (".py", ".json", ".jinja", ".txt", ".md", ".safetensors")
            ) or filename in {"LICENSE", "NOTICE"}:
                allow.append(
                    {
                        "filename": filename,
                        "repository": repo,
                        "revision": revision,
                        "source": f"https://huggingface.co/{repo}/resolve/{revision}/{filename}",
                        "expected_size": item["size"],
                        "sha256": item.get("lfs", {}).get("sha256"),
                        "purpose": "weights"
                        if filename.endswith(".safetensors")
                        else "static review / pinned runtime assets",
                    }
                )
        fetcher.save(ROOT / f"{name}_allowlist.json", allow)
        print(name, revision, json.dumps([(i["filename"], i["expected_size"]) for i in allow]))
        for item in allow:
            # Compare small configs/licenses/code first; defer tokenizers and weights.
            if item["expected_size"] > 1_000_000 or item["filename"].endswith(".safetensors"):
                continue
            fetcher.fetch(
                item["source"],
                ROOT / "upstream" / name / item["filename"],
                item["expected_size"],
                item["sha256"],
            )


def acquire(name: str, weights: bool) -> None:
    allow = json.loads((ROOT / f"{name}_allowlist.json").read_text())
    for item in allow:
        if item["filename"].endswith(".safetensors") != weights:
            continue
        dest = ROOT / "upstream" / name / item["filename"]
        if dest.exists():
            receipt = dest.with_name(dest.name + ".receipt.json")
            if not receipt.exists() or dest.stat().st_size != item["expected_size"]:
                raise RuntimeError("Incomplete existing artifact; no implicit retry")
            continue
        fetcher.fetch(item["source"], dest, item["expected_size"], item["sha256"])
        if dest.stat().st_size != item["expected_size"]:
            raise RuntimeError("ARTIFACT_SIZE_MISMATCH")
        print("verified", item["filename"], flush=True)


def rights() -> None:
    for name, repo in (("qwen15", "Qwen/Qwen2.5-1.5B"), ("qwen72", "Qwen/Qwen2.5-72B-Instruct")):
        path = ROOT / "evidence" / f"{name}_metadata.json"
        if not path.exists():
            fetcher.fetch(f"https://huggingface.co/api/models/{repo}?blobs=true", path, 2_000_000)
        meta = json.loads(path.read_text(encoding="utf8"))
        item = next(i for i in meta["siblings"] if i["rfilename"] == "LICENSE")
        url = f"https://huggingface.co/{repo}/resolve/{meta['sha']}/LICENSE"
        fetcher.save(
            ROOT / "evidence" / f"{name}_license_plan.json",
            {
                "source": url,
                "revision": meta["sha"],
                "expected_size": item["size"],
                "purpose": "local-use/redistribution rights review",
            },
        )
        if not (ROOT / "evidence" / f"{name}_LICENSE").exists():
            fetcher.fetch(url, ROOT / "evidence" / f"{name}_LICENSE", item["size"])
    for name, repo in (("internvl", "OpenGVLab/InternVL"), ("fastchat", "lm-sys/FastChat")):
        path = ROOT / "evidence" / f"{name}_github_commit.json"
        if not path.exists():
            fetcher.fetch(f"https://api.github.com/repos/{repo}/commits/main", path, 2_000_000)
        sha = json.loads(path.read_text(encoding="utf8"))["sha"]
        url = f"https://raw.githubusercontent.com/{repo}/{sha}/LICENSE"
        fetcher.save(
            ROOT / "evidence" / f"{name}_license_plan.json",
            {
                "source": url,
                "revision": sha,
                "size_upper_bound": 100_000,
                "purpose": "attribution/license review",
            },
        )
        if not (ROOT / "evidence" / f"{name}_LICENSE").exists():
            fetcher.fetch(url, ROOT / "evidence" / f"{name}_LICENSE", 100_000)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=("inspect", "assets", "weights", "rights"))
    parser.add_argument("--selected", choices=tuple(REPOS), default="instruct")
    args = parser.parse_args()
    if args.action == "inspect":
        inspect()
    elif args.action == "rights":
        rights()
    else:
        acquire(args.selected, args.action == "weights")
