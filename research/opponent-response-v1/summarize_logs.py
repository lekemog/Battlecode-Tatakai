#!/usr/bin/env python3
"""Summarize OPP lines in exported text logs. Pass one team's logs from ONE game."""
import argparse
import json
import re
from pathlib import Path


def summarize(paths):
    latest, samples, choices = {}, {}, set()
    errors = 0
    for path in paths:
        for line in path.read_text(errors="replace").splitlines():
            if "bot error:" in line:
                errors += 1
            match = re.search(r"\b(OPP_SAMPLE|OPP_CHOICE|OPP)\s+(.*)", line)
            if not match:
                continue
            kind, body = match.groups()
            d = dict(re.findall(r"([a-z]+)=([^\s]+)", body))
            if kind == "OPP":
                key = d["slot"]
                if key not in latest or int(d["r"]) > int(latest[key]["r"]):
                    latest[key] = d
            elif kind == "OPP_SAMPLE":
                samples[(d["slot"], d["enemy"], d["start"])] = d
            else:
                choices.add((d["r"], d["slot"], d["kind"], d["baseline"], d["model"]))
    scored = [s for s in samples.values() if s["label"] != "-1"]
    squared = [(float(s["prediction"]) - int(s["label"])) ** 2 for s in scored]
    return {
        "last_summary_per_slot": latest,
        "observed_choice_changes": len(choices),
        "samples": len(samples),
        "censored": sum(s["label"] == "-1" for s in samples.values()),
        "scored_samples": len(scored),
        "approaches": sum(s["label"] == "1" for s in scored),
        "brier_on_uncensored_samples_only": sum(squared) / len(squared) if squared else None,
        "bot_error_lines": errors,
        "warning": "Observational/censored sample, not a calibrated death probability or causal response estimate. "
                   "Counters may be incomplete if logs are truncated. Compare score and fuel in matched engine games.",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", type=Path, nargs="+")
    args = parser.parse_args()
    print(json.dumps(summarize(args.logs), indent=2))


if __name__ == "__main__":
    main()
