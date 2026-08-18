"""Create modified PTC flat files with deterministic MAD-X-style misalignments."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

from pyptc.error_table import MadxErrorRecord, read_madx_error_table
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
    dtheta: float = 0.0
    dphi: float = 0.0
    dpsi: float = 0.0


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


def _matching_blocks(lines: list[str], element: str) -> list[tuple[int, int, str]]:
    wanted = element.upper()
    blocks: list[tuple[int, int, str]] = []
    sliced_dipoles: list[tuple[int, int, str]] = []
    for start, end in _find_blocks(lines):
        name = _block_element_name(lines, start, end)
        if name is None:
            continue
        upper_name = name.upper()
        if upper_name == wanted:
            blocks.append((start, end, name))
            continue
        suffix = upper_name[len(wanted) :]
        if wanted.endswith("_DIP") and upper_name.startswith(wanted) and suffix.isdigit():
            sliced_dipoles.append((start, end, name))
    return blocks or sliced_dipoles


def _set_mis_flag(lines: list[str], start: int, end: int) -> None:
    name_line = _element_name_line(lines, start, end)
    if name_line is None or name_line + 1 > end:
        raise ValueError("Could not locate L,PERMFRINGE,MIS line")
    parts = lines[name_line + 1].split()
    if len(parts) < 3:
        raise ValueError(f"Malformed L,PERMFRINGE,MIS line: {lines[name_line + 1].rstrip()}")
    lines[name_line + 1] = f"  {parts[0]} {parts[1]} T  L,PERMFRINGE,MIS\n"


def _set_chart_offset(
    lines: list[str],
    start: int,
    end: int,
    dx: float,
    dy: float,
    ds: float,
    dtheta: float,
    dphi: float,
    dpsi: float,
) -> None:
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
    values = [dx, dy, ds, dtheta, dphi, dpsi]
    lines[frame_end + 1] = _format_six(values, "D_IN,ANG_IN")
    lines[frame_end + 2] = _format_six([-value for value in values], "D_OUT,ANG_OUT")


def _apply_to_lines(
    lines: list[str],
    element: str,
    dx: float = 0.0,
    dy: float = 0.0,
    ds: float = 0.0,
    dtheta: float = 0.0,
    dphi: float = 0.0,
    dpsi: float = 0.0,
    occurrence: int = 1,
) -> AppliedMisalignment:
    matches = _matching_blocks(lines, element)
    if occurrence < 1 or occurrence > len(matches):
        raise ValueError(f"Element {element!r} occurrence {occurrence} not found")

    seen = 0
    for start, end, name in matches:
        seen += 1
        if seen == occurrence:
            _set_mis_flag(lines, start, end)
            _set_chart_offset(lines, start, end, dx, dy, ds, dtheta, dphi, dpsi)
            return AppliedMisalignment(
                element=name,
                occurrence=occurrence,
                dx=dx,
                dy=dy,
                ds=ds,
                dtheta=dtheta,
                dphi=dphi,
                dpsi=dpsi,
            )

    raise ValueError(f"Element {element!r} occurrence {occurrence} not found")


def _apply_all_matching_to_lines(
    lines: list[str],
    record: MadxErrorRecord,
) -> list[AppliedMisalignment]:
    matches = _matching_blocks(lines, record.name)
    if not matches:
        raise ValueError(f"Element {record.name!r} not found")
    applied: list[AppliedMisalignment] = []
    for occurrence, (start, end, name) in enumerate(matches, start=1):
        _set_mis_flag(lines, start, end)
        _set_chart_offset(lines, start, end, **record.as_kwargs())
        applied.append(AppliedMisalignment(
            element=name,
            occurrence=occurrence,
            **record.as_kwargs(),
        ))
    return applied


def apply_single_misalignment(
    input_file: str | Path,
    output_file: str | Path,
    element: str,
    dx: float = 0.0,
    dy: float = 0.0,
    ds: float = 0.0,
    dtheta: float = 0.0,
    dphi: float = 0.0,
    dpsi: float = 0.0,
    occurrence: int = 1,
) -> AppliedMisalignment:
    input_path = Path(input_file)
    output_path = Path(output_file)
    lines = input_path.read_text(encoding="utf-8").splitlines(keepends=True)
    try:
        applied = _apply_to_lines(lines, element, dx, dy, ds, dtheta, dphi, dpsi, occurrence)
    except ValueError as exc:
        raise ValueError(f"{exc} in {input_path}") from exc
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("".join(lines), encoding="utf-8")
    return applied


def apply_misalignments(
    input_file: str | Path,
    output_file: str | Path,
    records: list[MadxErrorRecord],
) -> list[AppliedMisalignment]:
    """Apply multiple MAD-X-style misalignments to one copied PTC flat file."""

    input_path = Path(input_file)
    output_path = Path(output_file)
    lines = input_path.read_text(encoding="utf-8").splitlines(keepends=True)
    occurrences: dict[str, int] = {}
    applied: list[AppliedMisalignment] = []

    for record in records:
        try:
            if record.name.upper() in occurrences:
                occurrence = occurrences[record.name.upper()] + 1
                occurrences[record.name.upper()] = occurrence
                applied.append(_apply_to_lines(lines, record.name, occurrence=occurrence, **record.as_kwargs()))
            else:
                occurrences[record.name.upper()] = 1
                applied.extend(_apply_all_matching_to_lines(lines, record))
        except ValueError as exc:
            raise ValueError(f"{exc} in {input_path}") from exc

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("".join(lines), encoding="utf-8")
    return applied


def apply_madx_error_table(
    input_file: str | Path,
    output_file: str | Path,
    error_table: str | Path,
    nonzero: bool = True,
    atol: float = 0.0,
) -> list[AppliedMisalignment]:
    """Apply a MAD-X `ESAVE`/`EFIELD` TFS table to a copied PTC flat file."""

    records = read_madx_error_table(error_table, nonzero=nonzero, atol=atol)
    return apply_misalignments(input_file, output_file, records)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_LATTICE)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--element", default="SP0_QF")
    parser.add_argument("--occurrence", type=int, default=1)
    parser.add_argument("--dx", type=float, default=0.003)
    parser.add_argument("--dy", type=float, default=0.0)
    parser.add_argument("--ds", type=float, default=0.0)
    parser.add_argument("--dtheta", type=float, default=0.0)
    parser.add_argument("--dphi", type=float, default=0.0)
    parser.add_argument("--dpsi", type=float, default=0.0)
    parser.add_argument("--madx-error-table", type=Path)
    args = parser.parse_args()

    if args.madx_error_table:
        applied = apply_madx_error_table(args.input, args.output, args.madx_error_table)
    else:
        applied = apply_single_misalignment(
            args.input,
            args.output,
            args.element,
            dx=args.dx,
            dy=args.dy,
            ds=args.ds,
            dtheta=args.dtheta,
            dphi=args.dphi,
            dpsi=args.dpsi,
            occurrence=args.occurrence,
        )
    print(applied)


if __name__ == "__main__":
    main()
