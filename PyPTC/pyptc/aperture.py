"""Aperture and loss convenience functions for PyPTC."""

from __future__ import annotations

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from .lattice import not_exposed


RECTANGULAR_APERTURE_KIND = 2
_APERTURE_ASSIGNMENT_RE = re.compile(
    r"^\s*(?P<name>[^,!]+)\s*,\s*APERTYPE\s*=\s*RECTANGLE\s*,\s*APERTURE\s*=\s*"
    r"\{\s*(?P<x>[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?)\s*,\s*"
    r"(?P<y>[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[Ee][+-]?\d+)?)\s*\}",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class RectangularApertureRecord:
    """Rectangular half aperture for one MAD-X/PTC element."""

    name: str
    half_x: float
    half_y: float
    s: float | None = None


@dataclass(frozen=True)
class AppliedApertureRecord(RectangularApertureRecord):
    """Rectangular aperture record after resolving it to a PTC fibre."""

    fibre_index: int = 0


def normalize_aperture_name(name: str) -> str:
    return name.strip().strip('"').strip("'").split(":")[0].upper()


def read_madx_aperture_file(path: str | Path) -> list[RectangularApertureRecord]:
    """Read MAD-X `APERTYPE=RECTANGLE, APERTURE={half_x, half_y}` assignments."""

    records: list[RectangularApertureRecord] = []
    for line in Path(path).read_text(encoding="utf-8").splitlines():
        match = _APERTURE_ASSIGNMENT_RE.match(line)
        if not match:
            continue
        records.append(
            RectangularApertureRecord(
                name=normalize_aperture_name(match.group("name")),
                half_x=float(match.group("x")),
                half_y=float(match.group("y")),
            )
        )
    return records


def read_madx_aperture_tfs(path: str | Path) -> list[RectangularApertureRecord]:
    """Read MAD-X APERTURE TFS output using `APER_1`, `APER_2`, and `S`."""

    columns: list[str] | None = None
    records: list[RectangularApertureRecord] = []
    for line in Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("@") or stripped.startswith("$"):
            continue
        if stripped.startswith("*"):
            columns = stripped.split()[1:]
            continue
        if columns is None:
            continue
        values = stripped.split()
        if len(values) < len(columns):
            continue
        row = dict(zip(columns, values))
        if "NAME" not in row or "APER_1" not in row or "APER_2" not in row:
            continue
        try:
            records.append(
                RectangularApertureRecord(
                    name=normalize_aperture_name(row["NAME"]),
                    half_x=float(row["APER_1"]),
                    half_y=float(row["APER_2"]),
                    s=float(row.get("S", "nan")),
                )
            )
        except ValueError:
            continue
    return records


def read_jvt_design_aperture(path: str | Path) -> list[RectangularApertureRecord]:
    """Read the ISIS JVT aperture CSV; `Semi_Ap_*` columns are in millimetres."""

    records: list[RectangularApertureRecord] = []
    with Path(path).open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            try:
                records.append(
                    RectangularApertureRecord(
                        name=normalize_aperture_name(row["Element"]),
                        half_x=float(row["Semi_Ap_H"]) / 1000.0,
                        half_y=float(row["Semi_Ap_V"]) / 1000.0,
                        s=float(row["Dist_Datum_D"]),
                    )
                )
            except (KeyError, TypeError, ValueError):
                continue
    return records


def set_aperture(ptc, *args, **kwargs):
    return ptc.set_aperture(*args, **kwargs)


def get_aperture(ptc, *args, **kwargs):
    return ptc.get_aperture(*args, **kwargs)


def apply_madx_aperture_file(ptc, *args, **kwargs):
    return ptc.apply_madx_aperture_file(*args, **kwargs)


def disable_aperture(ptc, *args, **kwargs):
    return ptc.disable_aperture(*args, **kwargs)


def absolute_aperture(ptc):
    return ptc.absolute_aperture()


def set_absolute_aperture(ptc, value):
    return ptc.set_absolute_aperture(value)


def track_bunch_with_losses(ptc, *args, **kwargs):
    return ptc.track_bunch_with_losses(*args, **kwargs)


def normalized_aperture_scan(*_args, **_kwargs):
    raise not_exposed("Normalized aperture scan")


def tune_smear_tracking(*_args, **_kwargs):
    raise not_exposed("PTC tune-smear tracking")
