#!/usr/bin/env python3
"""Run the newest numbered ISIS RCS admission skill iteration."""
from __future__ import annotations

import importlib.util
import re
import sys
from pathlib import Path

STEP_DIR = Path(__file__).resolve().parent
ITERATION_PATTERN = re.compile(r"iteration-(\d{4})\Z")


def discover_harness() -> tuple[int, Path]:
    candidates: list[tuple[int, Path]] = []
    for directory in STEP_DIR.iterdir():
        match = ITERATION_PATTERN.fullmatch(directory.name)
        harness = directory / "admission_harness.py"
        if match and directory.is_dir() and harness.is_file():
            candidates.append((int(match.group(1)), harness))
    if not candidates:
        raise FileNotFoundError(
            f"No iteration-NNNN/admission_harness.py found under {STEP_DIR}"
        )
    return max(candidates, key=lambda item: item[0])


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if arguments:
        print("run_admission.py takes no arguments; it selects the newest skill iteration.",
              file=sys.stderr)
        return 2

    try:
        iteration, harness_path = discover_harness()
    except OSError as exc:
        print(f"Cannot select admission skill iteration: {exc}", file=sys.stderr)
        return 2

    spec = importlib.util.spec_from_file_location(
        f"admission_iteration_{iteration}", harness_path
    )
    if spec is None or spec.loader is None:
        print(f"Cannot load admission harness: {harness_path}", file=sys.stderr)
        return 2
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    print(f"Selected admission skill iteration: {iteration:04d}")
    return int(module.cli([]))


if __name__ == "__main__":
    raise SystemExit(main())
