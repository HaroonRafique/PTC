"""MAD-X error-table parsing helpers for PyPTC misalignment workflows."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


MISALIGNMENT_COLUMNS = ("dx", "dy", "ds", "dtheta", "dphi", "dpsi")
MULTIPOLE_ORDERS = 21
MADX_MULTIPOLE_COLUMNS = tuple(
    column
    for order in range(MULTIPOLE_ORDERS)
    for column in (f"K{order}L", f"K{order}SL")
)
MADX_ERROR_COLUMNS = ("NAME", "DX", "DY", "DS", "DPHI", "DTHETA", "DPSI")
LATEST_SURVEY_REFERENCE_ERROR_TABLE = (
    Path(__file__).resolve().parents[1] / "workflows" / "madx" / "reference_errors" / "apr_2026_survey_corrected.tfs"
)


@dataclass(frozen=True)
class MadxErrorRecord:
    """One MAD-X EFIELD row with alignment and integrated magnetic errors."""

    name: str
    dx: float = 0.0
    dy: float = 0.0
    ds: float = 0.0
    dtheta: float = 0.0
    dphi: float = 0.0
    dpsi: float = 0.0
    knl: tuple[float, ...] = (0.0,) * MULTIPOLE_ORDERS
    ksl: tuple[float, ...] = (0.0,) * MULTIPOLE_ORDERS
    unsupported: tuple[tuple[str, float], ...] = ()

    def has_misalignment(self, atol: float = 0.0) -> bool:
        return any(abs(float(getattr(self, column))) > atol for column in MISALIGNMENT_COLUMNS)

    def has_multipole_error(self, atol: float = 0.0) -> bool:
        return any(abs(value) > atol for value in (*self.knl, *self.ksl))

    def has_error(self, atol: float = 0.0) -> bool:
        return self.has_misalignment(atol) or self.has_multipole_error(atol) or any(
            abs(value) > atol for _, value in self.unsupported
        )

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
    knl: tuple[float, ...] = (0.0,) * MULTIPOLE_ORDERS
    ksl: tuple[float, ...] = (0.0,) * MULTIPOLE_ORDERS


def _parse_float(token: str) -> float:
    return float(token.replace("D", "E").replace("d", "e"))


def _clean_name(token: str) -> str:
    return token.strip().strip('"').split(":")[0]


def read_madx_error_table(path: str | Path, nonzero: bool = True, atol: float = 0.0) -> list[MadxErrorRecord]:
    """Read a MAD-X `ESAVE`/`EFIELD` TFS table.

    Alignment values use MAD-X units (metres and radians). Magnetic `K<n>L`
    and `K<n>SL` values are retained as integrated strengths. Other numeric
    fields are retained for explicit unsupported-field checks by the caller.
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
    multipole_index = {
        name: columns.index(name)
        for name in MADX_MULTIPOLE_COLUMNS
        if name in columns
    }
    supported_columns = set(MADX_ERROR_COLUMNS) | set(MADX_MULTIPOLE_COLUMNS)
    unsupported_indices = {
        name: index for index, name in enumerate(columns) if name not in supported_columns
    }
    records: list[MadxErrorRecord] = []
    for line in lines[data_start:]:
        stripped = line.strip()
        if not stripped or stripped.startswith(("@", "*", "$", "!")):
            continue
        parts = stripped.split()
        if len(parts) < len(columns):
            raise ValueError(f"Malformed MAD-X error-table row in {table_path}: {stripped}")
        values = {
            name: _parse_float(parts[index])
            for index, name in enumerate(columns)
            if name != "NAME"
        }
        knl = tuple(
            _parse_float(parts[multipole_index[f"K{order}L"]])
            if f"K{order}L" in multipole_index else 0.0
            for order in range(MULTIPOLE_ORDERS)
        )
        ksl = tuple(
            _parse_float(parts[multipole_index[f"K{order}SL"]])
            if f"K{order}SL" in multipole_index else 0.0
            for order in range(MULTIPOLE_ORDERS)
        )
        record = MadxErrorRecord(
            name=_clean_name(parts[column_index["NAME"]]),
            dx=_parse_float(parts[column_index["DX"]]),
            dy=_parse_float(parts[column_index["DY"]]),
            ds=_parse_float(parts[column_index["DS"]]),
            dtheta=_parse_float(parts[column_index["DTHETA"]]),
            dphi=_parse_float(parts[column_index["DPHI"]]),
            dpsi=_parse_float(parts[column_index["DPSI"]]),
            knl=knl,
            ksl=ksl,
            unsupported=tuple(
                (name, values[name])
                for name, index in unsupported_indices.items()
                if values[name] != 0.0
            ),
        )
        if not nonzero or record.has_error(atol=atol):
            records.append(record)

    return records
