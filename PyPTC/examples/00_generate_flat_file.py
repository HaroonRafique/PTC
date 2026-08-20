#!/usr/bin/env python3
"""Generate the default simplified ISIS RCS PTC flat file."""

from __future__ import annotations

from common import generate_flat_file, output_dir


def main() -> None:
    out = output_dir("00_generate_flat_file")
    summary = generate_flat_file(out)
    print(summary)


if __name__ == "__main__":
    main()
