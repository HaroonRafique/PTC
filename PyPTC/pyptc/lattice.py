"""Lattice metadata helpers for the standalone PyPTC wrapper."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class PyPTCFeatureNotExposed(NotImplementedError):
    pass


def not_exposed(feature: str) -> PyPTCFeatureNotExposed:
    return PyPTCFeatureNotExposed(
        f"{feature} is present in PTC internals but is not exposed by the PyPTC C ABI yet."
    )


FIBRE_MARK = "@@@@@@@@@@@@@@@@@@@@ FIBRE"
FIBRE_END_MARK = "@@@@@@@@@@@@@@@@@@@@  END"
ELEMENT_MARK = "$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$ ELEMENT"


@dataclass(frozen=True)
class FibreRecord:
    """Flat-file fibre metadata needed by the first PyPTC edit shims."""

    index: int
    name: str
    start_line: int
    end_line: int


def _find_fibre_blocks(lines: list[str]) -> list[tuple[int, int]]:
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


def _block_element_name(lines: list[str], start: int, end: int) -> str | None:
    element_header = next((index for index in range(start, end + 1) if ELEMENT_MARK in lines[index]), None)
    if element_header is None or element_header + 1 > end:
        return None
    parts = lines[element_header + 1].split()
    return parts[1] if len(parts) >= 2 else None


def read_flatfile_fibres(flat_file: str | Path) -> list[FibreRecord]:
    """Return one-based PTC fibre records parsed from a PTC flat file."""

    path = Path(flat_file)
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    records: list[FibreRecord] = []
    for index, (start, end) in enumerate(_find_fibre_blocks(lines), start=1):
        name = _block_element_name(lines, start, end)
        if name is None:
            continue
        records.append(FibreRecord(index=index, name=name, start_line=start + 1, end_line=end + 1))
    return records


def resolve_fibre_index(flat_file: str | Path, name: str, occurrence: int = 1) -> int:
    """Resolve an element name and occurrence to a one-based PTC fibre index."""

    wanted = name.upper()
    seen = 0
    for record in read_flatfile_fibres(flat_file):
        if record.name.upper() != wanted:
            continue
        seen += 1
        if seen == occurrence:
            return record.index
    raise ValueError(f"Element {name!r} occurrence {occurrence} not found in {Path(flat_file)}")
