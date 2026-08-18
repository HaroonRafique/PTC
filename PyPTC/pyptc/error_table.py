"""MAD-X error-table parsing helpers for PyPTC misalignment workflows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


MISALIGNMENT_COLUMNS = ("dx", "dy", "ds", "dtheta", "dphi", "dpsi")
MADX_ERROR_COLUMNS = ("NAME", "DX", "DY", "DS", "DPHI", "DTHETA", "DPSI")
LATEST_SURVEY_REFERENCE_ERROR_TABLE = (
    Path(__file__).resolve().parents[1] / "madx" / "reference_errors" / "jan26_survey_corrected.tfs"
)


@dataclass(frozen=True)
class MadxErrorRecord:
    """One MAD-X EFIELD/EALIGN table row in MAD-X units: metres and radians."""

    name: str
    dx: float = 0.0
    dy: float = 0.0
    ds: float = 0.0
    dtheta: float = 0.0
    dphi: float = 0.0
    dpsi: float = 0.0

    def has_misalignment(self, atol: float = 0.0) -> bool:
        return any(abs(float(getattr(self, column))) > atol for column in MISALIGNMENT_COLUMNS)

    def as_kwargs(self) -> dict[str, float]:
        return {column: float(getattr(self, column)) for column in MISALIGNMENT_COLUMNS}


@dataclass(frozen=True)
class AppliedErrorRecord:
    """A MAD-X error-table row resolved to a PTC fibre index."""

    name: str
    occurrence: int
    fibre_index: int
    dx: float
    dy: float
    ds: float
    dtheta: float
    dphi: float
    dpsi: float


def _parse_float(token: str) -> float:
    return float(token.replace("D", "E").replace("d", "e"))


def _clean_name(token: str) -> str:
    return token.strip().strip('"').split(":")[0]


def read_madx_error_table(path: str | Path, nonzero: bool = True, atol: float = 0.0) -> list[MadxErrorRecord]:
    """Read a MAD-X `ESAVE`/`EFIELD` TFS table.

    The returned records retain only the standard EALIGN columns used by the
    PyPTC misalignment API. Units are the MAD-X table units: metres for
    `DX/DY/DS` and radians for `DPHI/DTHETA/DPSI`.
    """

    table_path = Path(path)
    lines = table_path.read_text(encoding="utf-8").splitlines()

    columns: list[str] | None = None
    data_start: int | None = None
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("*"):
            columns = stripped.lstrip("*").split()
        elif stripped.startswith("$") and columns is not None:
            data_start = index + 1
            break

    if columns is None or data_start is None:
        raise ValueError(f"Could not parse MAD-X TFS error table header: {table_path}")

    missing = [column for column in MADX_ERROR_COLUMNS if column not in columns]
    if missing:
        raise ValueError(f"MAD-X error table {table_path} is missing columns: {missing}")

    column_index = {name: columns.index(name) for name in MADX_ERROR_COLUMNS}
    records: list[MadxErrorRecord] = []
    for line in lines[data_start:]:
        stripped = line.strip()
        if not stripped or stripped.startswith(("@", "*", "$", "!")):
            continue
        parts = stripped.split()
        if len(parts) < len(columns):
            raise ValueError(f"Malformed MAD-X error-table row in {table_path}: {stripped}")
        record = MadxErrorRecord(
            name=_clean_name(parts[column_index["NAME"]]),
            dx=_parse_float(parts[column_index["DX"]]),
            dy=_parse_float(parts[column_index["DY"]]),
            ds=_parse_float(parts[column_index["DS"]]),
            dtheta=_parse_float(parts[column_index["DTHETA"]]),
            dphi=_parse_float(parts[column_index["DPHI"]]),
            dpsi=_parse_float(parts[column_index["DPSI"]]),
        )
        if not nonzero or record.has_misalignment(atol=atol):
            records.append(record)

    return records
