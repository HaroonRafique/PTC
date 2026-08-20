"""Standalone Python interface for PTC."""

from .bunch import (
    DEFAULT_PYPARTICLEBUNCH_SRC,
    generate_matched_gaussian_4d,
    pyparticlebunch_source,
)
from .core import DEFAULT_LATTICE, DEFAULT_LIBRARY, DEFAULT_SIMPLIFIED_LATTICE, LEGACY_READINESS_LATTICE, PTC, ensure_default_lattice
from .aperture import (
    AppliedApertureRecord,
    RECTANGULAR_APERTURE_KIND,
    RectangularApertureRecord,
    normalize_aperture_name,
    read_jvt_design_aperture,
    read_madx_aperture_file,
    read_madx_aperture_tfs,
)
from .error_table import (
    LATEST_SURVEY_REFERENCE_ERROR_TABLE,
    AppliedErrorRecord,
    MadxErrorRecord,
    read_madx_error_table,
)
from .lattice import FibreRecord, read_flatfile_fibres, resolve_fibre_index, resolve_fibre_indices
from .plotting import (
    DIAGNOSTIC_COLUMNS,
    plot_diagnostic_dashboard,
    plot_tune_footprints,
    plot_tune_vs_action,
    tune_summary,
    write_diagnostic_csv,
    write_tune_csv,
)

__all__ = [
    "DEFAULT_LATTICE",
    "DEFAULT_LIBRARY",
    "DEFAULT_SIMPLIFIED_LATTICE",
    "DEFAULT_PYPARTICLEBUNCH_SRC",
    "LEGACY_READINESS_LATTICE",
    "LATEST_SURVEY_REFERENCE_ERROR_TABLE",
    "AppliedErrorRecord",
    "AppliedApertureRecord",
    "FibreRecord",
    "MadxErrorRecord",
    "PTC",
    "RECTANGULAR_APERTURE_KIND",
    "RectangularApertureRecord",
    "generate_matched_gaussian_4d",
    "ensure_default_lattice",
    "normalize_aperture_name",
    "pyparticlebunch_source",
    "read_jvt_design_aperture",
    "read_madx_aperture_file",
    "read_madx_aperture_tfs",
    "read_madx_error_table",
    "read_flatfile_fibres",
    "resolve_fibre_index",
    "resolve_fibre_indices",
    "DIAGNOSTIC_COLUMNS",
    "plot_diagnostic_dashboard",
    "plot_tune_footprints",
    "plot_tune_vs_action",
    "tune_summary",
    "write_diagnostic_csv",
    "write_tune_csv",
]
