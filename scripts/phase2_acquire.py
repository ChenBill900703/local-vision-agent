"""Explicit pinned artifact acquisition, resumptions refused; never imports model code."""

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "artifacts" / "phase2-20260927"
MODEL = "vikhyatk/moondream2"
REVISION = "9a7d4024050840e001defacec2b00727e89149e6"
TOKENIZER = "moondream/starmie-v1"
TOKEN_REVISION = "35192e10a54e36eabe0a7cc57a2c1aab371cafc5"
LABEL = "PILOT / EXPLORATORY / NOT FORMAL THESIS RESULT"
# Payload ceiling below the approved 5 GB to allow metadata/transport overhead.
NETWORK_CAP = 4_900_000_000
DISK_CAP = 12_000_000_000


def save(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf8")


def ledger() -> dict:
    path = ROOT / "network_ledger.json"
    return json.loads(path.read_text()) if path.exists() else {"label": LABEL, "payload_bytes": 0}


def fetch(url: str, destination: Path, expected: int, expected_sha: str | None = None) -> None:
    if destination.exists():
        raise RuntimeError("Refuse overwrite/retry: " + str(destination))
    budget = ledger()
    used_disk = sum(p.stat().st_size for p in ROOT.rglob("*") if p.is_file())
    if budget["payload_bytes"] + expected > NETWORK_CAP or used_disk + expected > DISK_CAP:
        raise RuntimeError("Acquisition ceiling")
    destination.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    digest = hashlib.sha256()
    try:
        with urllib.request.urlopen(url, timeout=45) as response, destination.open("xb") as out:
            while chunk := response.read(min(1024 * 1024, expected - count + 1)):
                count += len(chunk)
                budget["payload_bytes"] += len(chunk)
                if count > expected or budget["payload_bytes"] > NETWORK_CAP:
                    raise RuntimeError("Unexpected download size")
                out.write(chunk)
                digest.update(chunk)
                if count % (64 * 1024 * 1024) == 0:
                    save(ROOT / "network_ledger.json", budget)
                    print(f"{destination.name}: {count} bytes", flush=True)
    finally:
        save(ROOT / "network_ledger.json", budget)
    if expected_sha and digest.hexdigest() != expected_sha:
        raise RuntimeError("SHA256 mismatch")
    save(
        destination.with_name(destination.name + ".receipt.json"),
        {"label": LABEL, "source": url, "actual_size": count, "sha256": digest.hexdigest()},
    )


def plan() -> None:
    for repo, revision, name in (
        (MODEL, REVISION, "model"),
        (TOKENIZER, TOKEN_REVISION, "tokenizer"),
    ):
        path = ROOT / "evidence" / f"{name}_metadata.json"
        fetch(
            f"https://huggingface.co/api/models/{repo}/revision/{revision}?blobs=true",
            path,
            2_000_000,
        )
        metadata = json.loads(path.read_text(encoding="utf8"))
        if metadata["sha"] != revision:
            raise RuntimeError("Revision mismatch")
        allow = []
        for item in metadata["siblings"]:
            filename = item["rfilename"]
            if name == "model":
                wanted = filename in {
                    "config.json",
                    "README.md",
                    "requirements.txt",
                    "model.safetensors",
                    "config.py",
                    "hf_moondream.py",
                    "moondream.py",
                    "image_crops.py",
                    "vision.py",
                    "text.py",
                    "region.py",
                    "utils.py",
                    "layers.py",
                    "lora.py",
                    "rope.py",
                    "fourier_features.py",
                    "weights.py",
                    "LICENSE",
                    "NOTICE",
                }
            else:
                wanted = filename in {
                    "README.md",
                    "tokenizer.json",
                    "tokenizer_config.json",
                    "special_tokens_map.json",
                    "LICENSE",
                    "NOTICE",
                }
            if wanted:
                allow.append(
                    {
                        "filename": filename,
                        "repository": repo,
                        "revision": revision,
                        "source": f"https://huggingface.co/{repo}/resolve/{revision}/{filename}",
                        "expected_size": item["size"],
                        "sha256": item.get("lfs", {}).get("sha256"),
                        "purpose": "weights"
                        if filename.endswith("safetensors")
                        else "static review / local pinned runtime assets",
                    }
                )
        save(ROOT / f"{name}_allowlist.json", allow)
        print(json.dumps(allow, indent=2))


def acquire(weights: bool) -> None:
    for name in ("model", "tokenizer"):
        allow = json.loads((ROOT / f"{name}_allowlist.json").read_text())
        for item in allow:
            if item["filename"].endswith("safetensors") != weights:
                continue
            destination = ROOT / "upstream" / name / item["filename"]
            fetch(item["source"], destination, item["expected_size"], item["sha256"])
            if destination.stat().st_size != item["expected_size"]:
                raise RuntimeError("Size mismatch")
            print("Verified", item["filename"], flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["plan", "code", "weights"])
    args = parser.parse_args()
    if args.action == "plan":
        plan()
    else:
        acquire(args.action == "weights")
