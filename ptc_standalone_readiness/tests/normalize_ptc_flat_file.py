#!/usr/bin/env python3
"""Create a compatibility-normalized copy of a PTC flat file.

The supplied flat file can encode PERMFRINGE as 0/1 on lines labelled
L,PERMFRINGE,MIS. The local PTC reader declares that field as logical and
expects F/T. This script rewrites only those labelled lines into a generated
copy so the original input remains untouched.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PERMFRINGE_RE = re.compile(r"^(\s*\S+)(\s+)([01])(\s+)([TF])(\s+L,PERMFRINGE,MIS.*)$")


def normalize_line(line: str) -> tuple[str, bool]:
    match = PERMFRINGE_RE.match(line.rstrip("\n"))
    if not match:
        return line, False
    logical = "T" if match.group(3) == "1" else "F"
    rewritten = f"{match.group(1)}{match.group(2)}{logical}{match.group(4)}{match.group(5)}{match.group(6)}\n"
    return rewritten, True


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()

    changed = 0
    total = 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.input.open("r", encoding="utf-8", errors="replace") as src, args.output.open("w", encoding="utf-8") as dst:
        for line in src:
            total += 1
            normalized, did_change = normalize_line(line)
            changed += int(did_change)
            dst.write(normalized)

    report = {
        "input": str(args.input),
        "output": str(args.output),
        "lines_read": total,
        "permfringe_lines_rewritten": changed,
        "rule": "Only labelled L,PERMFRINGE,MIS lines with 0/1 PERMFRINGE are rewritten to F/T.",
    }
    if args.report:
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
