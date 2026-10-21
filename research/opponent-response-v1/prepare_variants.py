#!/usr/bin/env python3
"""Materialize isolated local bench arms. Never submits or runs a platform match."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "bots/chatgpt-opp-response-v1/src"
ARMS = {"off": 0, "shadow": 1, "learned": 2, "fixed": 3}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", type=Path, default=ROOT)
    args = parser.parse_args()
    manifest = json.loads((Path(__file__).parent / "SOURCE_MANIFEST.json").read_text())
    baseline = ROOT / "bots/v23v/src"
    for name, expected in manifest["baseline_sha256"].items():
        actual = hashlib.sha256((baseline / name).read_bytes()).hexdigest()
        if actual != expected:
            raise SystemExit(f"Pinned v23v source changed: {name}; review/rebase before testing")
    destinations = [args.project / "bots" / f"chatgpt-opp-{name}" for name in ARMS]
    if any(p.exists() for p in destinations):
        raise SystemExit("A generated arm already exists; use a fresh project or remove only your old generated arms")
    for (name, mode), destination in zip(ARMS.items(), destinations):
        shutil.copytree(SOURCE, destination / "src")
        (destination / "src/opponent_config.h").write_text(
            f"#pragma once\n#define POLARIS_OPP_MODEL {mode}\n")
        print(f"{name}: {destination}")


if __name__ == "__main__":
    main()
