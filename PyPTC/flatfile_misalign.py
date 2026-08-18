"""Create modified PTC flat files with one deterministic magnet offset."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from ptc import DEFAULT_LATTICE


FIBRE_MARK = "@@@@@@@@@@@@@@@@@@@@ FIBRE"
FIBRE_END_MARK = "@@@@@@@@@@@@@@@@@@@@  END"
ELEMENT_MARK = "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ ELEMENT"
CHART_MARK = "THIS IS A CHART"
END_MAGNET_FRAME_MARK = "END MAGNET FRAME"
END_CHART_MARK = "END OF A CHART"


@dataclass(frozen=True)
class AppliedMisalignment:
    element: str
    occurrence: int
    dx: float
    dy: float
    ds: float


def _format_six(values: list[float], label: str) -> str:
    return "  " + "  ".join(f"{value:.16E}" for value in values) + f" {label}\n"


def _find_blocks(lines: list[str]) -> list[tuple[int, int]]:
    starts = [index for index, line in enumerate(lines) if FIBRE_MARK in line]
    blocks: list[tuple[int, int]] = []
    for start in starts:
        end = next(
            (index for index in range(start + 1, len(lines)) if FIBRE_END_MARK in lines[index]),
            None,
        )
        if end is None:
            raise ValueError(f"Could not find end of fibre block starting at line {start + 1}")
        blocks.append((start, end))
    return blocks


def _element_name_line(lines: list[str], start: int, end: int) -> int | None:
    element_header = next((index for index in range(start, end + 1) if ELEMENT_MARK in lines[index]), None)
    if element_header is None or element_header + 1 > end:
        return None
    return element_header + 1


def _block_element_name(lines: list[str], start: int, end: int) -> str | None:
    name_line = _element_name_line(lines, start, end)
    if name_line is None:
        return None
    parts = lines[name_line].split()
    return parts[1] if len(parts) >= 2 else None


def _set_mis_flag(lines: list[str], start: int, end: int) -> None:
    name_line = _element_name_line(lines, start, end)
    if name_line is None or name_line + 1 > end:
        raise ValueError("Could not locate L,PERMFRINGE,MIS line")
    parts = lines[name_line + 1].split()
    if len(parts) < 3:
        raise ValueError(f"Malformed L,PERMFRINGE,MIS line: {lines[name_line + 1].rstrip()}")
    lines[name_line + 1] = f"  {parts[0]} {parts[1]} T  L,PERMFRINGE,MIS\n"


def _set_chart_offset(lines: list[str], start: int, end: int, dx: float, dy: float, ds: float) -> None:
    chart = next((index for index in range(start, end + 1) if CHART_MARK in lines[index]), None)
    if chart is None:
        raise ValueError("Target fibre has no chart; cannot encode deterministic misalignment")
    frame_end = next(
        (index for index in range(chart + 1, end + 1) if END_MAGNET_FRAME_MARK in lines[index]),
        None,
    )
    if frame_end is None or frame_end + 2 > end:
        raise ValueError("Target fibre chart has no D_IN/D_OUT lines")
    chart_end = next(
        (index for index in range(frame_end + 1, end + 1) if END_CHART_MARK in lines[index]),
        None,
    )
    if chart_end is None or frame_end + 2 >= chart_end:
        raise ValueError("Target fibre chart layout is not recognized")

    # These lines are read by PTC as D_IN,ANG_IN and D_OUT,ANG_OUT.
    lines[frame_end + 1] = _format_six([dx, dy, ds, 0.0, 0.0, 0.0], "D_IN,ANG_IN")
    lines[frame_end + 2] = _format_six([-dx, -dy, -ds, 0.0, 0.0, 0.0], "D_OUT,ANG_OUT")


def apply_single_misalignment(
    input_file: str | Path,
    output_file: str | Path,
    element: str,
    dx: float = 0.0,
    dy: float = 0.0,
    ds: float = 0.0,
    occurrence: int = 1,
) -> AppliedMisalignment:
    input_path = Path(input_file)
    output_path = Path(output_file)
    lines = input_path.read_text(encoding="utf-8").splitlines(keepends=True)
    wanted = element.upper()
    seen = 0

    for start, end in _find_blocks(lines):
        name = _block_element_name(lines, start, end)
        if name is None or name.upper() != wanted:
            continue
        seen += 1
        if seen != occurrence:
            continue
        _set_mis_flag(lines, start, end)
        _set_chart_offset(lines, start, end, dx, dy, ds)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("".join(lines), encoding="utf-8")
        return AppliedMisalignment(element=name, occurrence=occurrence, dx=dx, dy=dy, ds=ds)

    raise ValueError(f"Element {element!r} occurrence {occurrence} not found in {input_path}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_LATTICE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--element", default="SP0_QF")
    parser.add_argument("--occurrence", type=int, default=1)
    parser.add_argument("--dx", type=float, default=0.003)
    parser.add_argument("--dy", type=float, default=0.0)
    parser.add_argument("--ds", type=float, default=0.0)
    args = parser.parse_args()

    applied = apply_single_misalignment(
        args.input,
        args.output,
        args.element,
        dx=args.dx,
        dy=args.dy,
        ds=args.ds,
        occurrence=args.occurrence,
    )
    print(applied)


if __name__ == "__main__":
    main()
