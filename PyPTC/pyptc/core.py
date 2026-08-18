"""Core ctypes wrapper for the standalone PyPTC shared library."""

from __future__ import annotations

import ctypes
from pathlib import Path
from typing import Iterable

import numpy as np

from .error_table import AppliedErrorRecord, read_madx_error_table
from .lattice import resolve_fibre_index, resolve_fibre_indices


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_LIBRARY = ROOT / "PyPTC" / "artifacts" / "build-pyptc" / "libpyptc.so"
DEFAULT_LATTICE = ROOT / "ptc_standalone_readiness" / "inputs" / "PTC-PyORBIT_flat_file.madx.flt"
C_DOUBLE_P = ctypes.POINTER(ctypes.c_double)
C_INT_P = ctypes.POINTER(ctypes.c_int)


class PTC:
    """Python-level handle to one loaded standalone PTC shared library."""

    def __init__(self, library: str | Path = DEFAULT_LIBRARY):
        self.library = Path(library)
        self.lattice: Path | None = None
        if not self.library.exists():
            raise FileNotFoundError(f"PTC shared library not found: {self.library}")
        self.lib = ctypes.CDLL(str(self.library))
        self._configure()

    def _configure(self) -> None:
        self.lib.ptc_init_.argtypes = [ctypes.c_char_p, ctypes.c_int]
        self.lib.ptc_init_.restype = None
        self.lib.ptc_script_.argtypes = [ctypes.c_char_p, ctypes.c_int]
        self.lib.ptc_script_.restype = None
        self.lib.ptc_read_accel_table_.argtypes = [ctypes.c_char_p, ctypes.c_int]
        self.lib.ptc_read_accel_table_.restype = None
        self.lib.ptc_get_ini_params_.argtypes = [C_INT_P, C_INT_P, C_DOUBLE_P, C_DOUBLE_P]
        self.lib.ptc_get_ini_params_.restype = None
        self.lib.ptc_get_syncpart_.argtypes = [C_DOUBLE_P, C_INT_P, C_DOUBLE_P]
        self.lib.ptc_get_syncpart_.restype = None
        self.lib.ptc_get_twiss_init_.argtypes = [C_DOUBLE_P] * 12
        self.lib.ptc_get_twiss_init_.restype = None
        self.lib.ptc_get_twiss_for_node_.argtypes = [C_INT_P] + [C_DOUBLE_P] * 13
        self.lib.ptc_get_twiss_for_node_.restype = None
        self.lib.ptc_get_task_type_.argtypes = [C_INT_P, C_INT_P]
        self.lib.ptc_get_task_type_.restype = None
        self.lib.ptc_get_omega_.argtypes = [C_DOUBLE_P]
        self.lib.ptc_get_omega_.restype = None
        self.lib.ptc_get_p0c_.argtypes = [C_DOUBLE_P]
        self.lib.ptc_get_p0c_.restype = None
        self.lib.ptc_get_beta0_.argtypes = [C_DOUBLE_P]
        self.lib.ptc_get_beta0_.restype = None
        self.lib.ptc_get_kinetic_.argtypes = [C_DOUBLE_P]
        self.lib.ptc_get_kinetic_.restype = None
        self.lib.ptc_synchronous_set_.argtypes = [C_INT_P]
        self.lib.ptc_synchronous_set_.restype = None
        self.lib.ptc_synchronous_after_.argtypes = [C_INT_P]
        self.lib.ptc_synchronous_after_.restype = None
        self.lib.ptc_track_particle_.argtypes = [C_INT_P] + [C_DOUBLE_P] * 6
        self.lib.ptc_track_particle_.restype = None
        self.lib.ptc_update_twiss_.argtypes = []
        self.lib.ptc_update_twiss_.restype = None

        if hasattr(self.lib, "pyptc_get_api_level"):
            self.lib.pyptc_get_api_level.argtypes = [C_INT_P]
            self.lib.pyptc_get_api_level.restype = None
            self.lib.pyptc_get_tunes.argtypes = [C_DOUBLE_P, C_DOUBLE_P, C_DOUBLE_P, C_INT_P]
            self.lib.pyptc_get_tunes.restype = None
            self.lib.pyptc_get_chromaticities.argtypes = [C_DOUBLE_P, C_DOUBLE_P, C_INT_P]
            self.lib.pyptc_get_chromaticities.restype = None
            self.lib.pyptc_set_misalignment.argtypes = [ctypes.c_int, C_DOUBLE_P, C_INT_P]
            self.lib.pyptc_set_misalignment.restype = None
            self.lib.pyptc_set_madx_misalignment.argtypes = [ctypes.c_int, C_DOUBLE_P, C_INT_P]
            self.lib.pyptc_set_madx_misalignment.restype = None
            self.lib.pyptc_set_one_aperture.argtypes = [
                ctypes.c_int,
                ctypes.c_int,
                C_DOUBLE_P,
                ctypes.c_double,
                ctypes.c_double,
                ctypes.c_double,
                ctypes.c_double,
                C_INT_P,
            ]
            self.lib.pyptc_set_one_aperture.restype = None
            self.lib.pyptc_turn_off_one_aperture.argtypes = [ctypes.c_int, C_INT_P]
            self.lib.pyptc_turn_off_one_aperture.restype = None
            self.lib.pyptc_set_absolute_aperture.argtypes = [ctypes.c_double, C_INT_P]
            self.lib.pyptc_set_absolute_aperture.restype = None
            self.lib.pyptc_get_absolute_aperture.argtypes = [C_DOUBLE_P]
            self.lib.pyptc_get_absolute_aperture.restype = None
            self.lib.pyptc_track_particle_ring_loss.argtypes = [
                C_DOUBLE_P,
                ctypes.c_int,
                C_INT_P,
                C_INT_P,
                C_INT_P,
                C_INT_P,
            ]
            self.lib.pyptc_track_particle_ring_loss.restype = None
            for name in (
                "pyptc_set_acceleration",
                "pyptc_set_ramping",
                "pyptc_set_modulation",
                "pyptc_set_cavity",
                "pyptc_cavity_totalpath",
            ):
                getattr(self.lib, name).argtypes = [ctypes.c_int, C_INT_P]
                getattr(self.lib, name).restype = None
            for name in ("pyptc_store_orbit_state", "pyptc_use_orbit_state", "pyptc_set_all_ramp", "pyptc_close_cavity_ring"):
                getattr(self.lib, name).argtypes = [C_INT_P]
                getattr(self.lib, name).restype = None
            self.lib.pyptc_energize_lattice.argtypes = [ctypes.c_double, ctypes.c_int, C_INT_P]
            self.lib.pyptc_energize_lattice.restype = None
            self.lib.pyptc_set_orbit_time.argtypes = [ctypes.c_double, C_INT_P]
            self.lib.pyptc_set_orbit_time.restype = None
            self.lib.pyptc_initialize_cavity.argtypes = [ctypes.c_int, ctypes.c_char_p, C_INT_P]
            self.lib.pyptc_initialize_cavity.restype = None
            self.lib.pyptc_power_cavity.argtypes = [
                ctypes.c_int,
                ctypes.c_double,
                ctypes.c_double,
                ctypes.c_double,
                C_INT_P,
            ]
            self.lib.pyptc_power_cavity.restype = None
            self.lib.pyptc_configure_ac_magnet.argtypes = [
                ctypes.c_int,
                ctypes.c_double,
                ctypes.c_double,
                ctypes.c_double,
                ctypes.c_double,
                ctypes.c_int,
                C_DOUBLE_P,
                C_DOUBLE_P,
                C_INT_P,
            ]
            self.lib.pyptc_configure_ac_magnet.restype = None
            self.lib.pyptc_configure_ramp_magnet.argtypes = [
                ctypes.c_int,
                ctypes.c_char_p,
                ctypes.c_double,
                C_INT_P,
            ]
            self.lib.pyptc_configure_ramp_magnet.restype = None

    def _check_status(self, operation: str, status: ctypes.c_int) -> None:
        if status.value != 0:
            raise RuntimeError(f"{operation} failed with PyPTC status {status.value}")

    def _resolve(self, name: str, occurrence: int = 1, lattice: str | Path | None = None) -> int:
        lattice_path = Path(lattice) if lattice is not None else self.lattice
        if lattice_path is None:
            raise ValueError("Name-based fibre lookup requires init_lattice(...) first or an explicit lattice path.")
        return resolve_fibre_index(lattice_path, name, occurrence)

    def api_level(self) -> int:
        value = ctypes.c_int()
        self.lib.pyptc_get_api_level(ctypes.byref(value))
        return value.value

    def init_lattice(self, lattice: str | Path) -> None:
        self.lattice = Path(lattice).resolve()
        encoded = str(self.lattice).encode()
        self.lib.ptc_init_(encoded, len(encoded))

    def run_script(self, script: str | Path) -> None:
        encoded = str(Path(script).resolve()).encode()
        self.lib.ptc_script_(encoded, len(encoded))

    def read_accel_table(self, table: str | Path) -> None:
        encoded = str(Path(table).resolve()).encode()
        self.lib.ptc_read_accel_table_(encoded, len(encoded))

    def update_twiss(self) -> None:
        self.lib.ptc_update_twiss_()

    def tunes(self) -> dict[str, float]:
        qx = ctypes.c_double()
        qy = ctypes.c_double()
        qs = ctypes.c_double()
        status = ctypes.c_int()
        self.lib.pyptc_get_tunes(ctypes.byref(qx), ctypes.byref(qy), ctypes.byref(qs), ctypes.byref(status))
        self._check_status("pyptc_get_tunes", status)
        return {"qx": qx.value, "qy": qy.value, "qs": qs.value}

    def chromaticities(self) -> dict[str, float]:
        chromx = ctypes.c_double()
        chromy = ctypes.c_double()
        status = ctypes.c_int()
        self.lib.pyptc_get_chromaticities(ctypes.byref(chromx), ctypes.byref(chromy), ctypes.byref(status))
        self._check_status("pyptc_get_chromaticities", status)
        return {"chromx": chromx.value, "chromy": chromy.value}

    def set_misalignment(
        self,
        fibre_index: int,
        dx: float = 0.0,
        dy: float = 0.0,
        ds: float = 0.0,
        dtheta: float = 0.0,
        dphi: float = 0.0,
        dpsi: float = 0.0,
    ) -> None:
        mis = np.ascontiguousarray([dx, dy, ds, dtheta, dphi, dpsi], dtype=np.float64)
        status = ctypes.c_int()
        self.lib.pyptc_set_misalignment(int(fibre_index), mis.ctypes.data_as(C_DOUBLE_P), ctypes.byref(status))
        self._check_status("pyptc_set_misalignment", status)

    def set_madx_misalignment(
        self,
        fibre_index: int,
        dx: float = 0.0,
        dy: float = 0.0,
        ds: float = 0.0,
        dtheta: float = 0.0,
        dphi: float = 0.0,
        dpsi: float = 0.0,
    ) -> None:
        # PTC's MAD_MISALIGN_FIBRE expects MAD-X angular inputs as
        # dphi, dtheta, dpsi. Keep set_misalignment(...) in raw PTC order.
        mis = np.ascontiguousarray([dx, dy, ds, dphi, dtheta, dpsi], dtype=np.float64)
        status = ctypes.c_int()
        self.lib.pyptc_set_madx_misalignment(int(fibre_index), mis.ctypes.data_as(C_DOUBLE_P), ctypes.byref(status))
        self._check_status("pyptc_set_madx_misalignment", status)

    def set_misalignment_by_name(self, name: str, occurrence: int = 1, **kwargs: float) -> int:
        fibre_index = self._resolve(name, occurrence)
        self.set_misalignment(fibre_index, **kwargs)
        return fibre_index

    def set_madx_misalignment_by_name(self, name: str, occurrence: int = 1, **kwargs: float) -> int:
        fibre_index = self._resolve(name, occurrence)
        self.set_madx_misalignment(fibre_index, **kwargs)
        return fibre_index

    def apply_misalignments(
        self,
        records: Iterable[dict[str, float | int | str] | object],
        madx_convention: bool = False,
    ) -> list[AppliedErrorRecord]:
        """Apply name-based misalignment records to the active PTC lattice.

        Repeated element names are mapped to occurrence 1, 2, ... in record
        order, matching how repeated rows in MAD-X tables are usually resolved.
        """

        occurrences: dict[str, int] = {}
        applied: list[AppliedErrorRecord] = []
        for record in records:
            if hasattr(record, "as_kwargs"):
                name = str(getattr(record, "name")).strip().strip('"').split(":")[0]
                occurrence_value = getattr(record, "occurrence", None)
                kwargs = getattr(record, "as_kwargs")()
            else:
                name = str(record["name"]).strip().strip('"').split(":")[0]
                occurrence_value = record.get("occurrence")
                kwargs = {
                    "dx": float(record.get("dx", 0.0)),
                    "dy": float(record.get("dy", 0.0)),
                    "ds": float(record.get("ds", 0.0)),
                    "dtheta": float(record.get("dtheta", 0.0)),
                    "dphi": float(record.get("dphi", 0.0)),
                    "dpsi": float(record.get("dpsi", 0.0)),
                }
            key = name.upper()
            if occurrence_value is not None:
                occurrence = int(occurrence_value)
                if madx_convention:
                    fibre_index = self.set_madx_misalignment_by_name(name, occurrence=occurrence, **kwargs)
                else:
                    fibre_index = self.set_misalignment_by_name(name, occurrence=occurrence, **kwargs)
                applied.append(AppliedErrorRecord(name=name, occurrence=occurrence, fibre_index=fibre_index, **kwargs))
                occurrences[key] = occurrence
                continue

            lattice_path = self.lattice
            if lattice_path is None:
                raise ValueError("Name-based fibre lookup requires init_lattice(...) first.")
            fibre_indices = resolve_fibre_indices(lattice_path, name)
            if len(fibre_indices) == 1:
                occurrence = occurrences.get(key, 0) + 1
                occurrences[key] = occurrence
                fibre_indices = [resolve_fibre_index(lattice_path, name, occurrence)]
            for local_occurrence, fibre_index in enumerate(fibre_indices, start=1):
                if madx_convention:
                    self.set_madx_misalignment(fibre_index, **kwargs)
                else:
                    self.set_misalignment(fibre_index, **kwargs)
                applied.append(
                    AppliedErrorRecord(
                        name=name,
                        occurrence=local_occurrence,
                        fibre_index=fibre_index,
                        **kwargs,
                    )
                )
        return applied

    def apply_madx_error_table(
        self,
        table: str | Path,
        nonzero: bool = True,
        atol: float = 0.0,
    ) -> list[AppliedErrorRecord]:
        """Read and apply a MAD-X `ESAVE`/`EFIELD` error table to PTC."""

        records = read_madx_error_table(table, nonzero=nonzero, atol=atol)
        return self.apply_misalignments(records, madx_convention=True)

    def set_aperture(
        self,
        fibre_index: int,
        kind: int,
        r1: float = 0.0,
        r2: float = 0.0,
        x: float = 0.0,
        y: float = 0.0,
        dx: float = 0.0,
        dy: float = 0.0,
    ) -> None:
        radii = np.ascontiguousarray([r1, r2], dtype=np.float64)
        status = ctypes.c_int()
        self.lib.pyptc_set_one_aperture(
            int(fibre_index),
            int(kind),
            radii.ctypes.data_as(C_DOUBLE_P),
            float(x),
            float(y),
            float(dx),
            float(dy),
            ctypes.byref(status),
        )
        self._check_status("pyptc_set_one_aperture", status)

    def set_aperture_by_name(self, name: str, occurrence: int = 1, **kwargs: float | int) -> int:
        fibre_index = self._resolve(name, occurrence)
        self.set_aperture(fibre_index, **kwargs)
        return fibre_index

    def disable_aperture(self, fibre_index: int) -> None:
        status = ctypes.c_int()
        self.lib.pyptc_turn_off_one_aperture(int(fibre_index), ctypes.byref(status))
        self._check_status("pyptc_turn_off_one_aperture", status)

    def disable_aperture_by_name(self, name: str, occurrence: int = 1) -> int:
        fibre_index = self._resolve(name, occurrence)
        self.disable_aperture(fibre_index)
        return fibre_index

    def absolute_aperture(self) -> float:
        value = ctypes.c_double()
        self.lib.pyptc_get_absolute_aperture(ctypes.byref(value))
        return value.value

    def set_absolute_aperture(self, value: float) -> None:
        status = ctypes.c_int()
        self.lib.pyptc_set_absolute_aperture(float(value), ctypes.byref(status))
        self._check_status("pyptc_set_absolute_aperture", status)

    def track_particle_ptc_with_loss(self, coords: Iterable[float], turns: int = 1) -> tuple[np.ndarray, dict[str, int | bool]]:
        values = np.ascontiguousarray(list(coords), dtype=np.float64)
        if values.shape != (6,):
            raise ValueError(f"Expected six PTC coordinates, got shape {values.shape}")
        lost = ctypes.c_int()
        lost_turn = ctypes.c_int()
        lost_pos = ctypes.c_int()
        status = ctypes.c_int()
        self.lib.pyptc_track_particle_ring_loss(
            values.ctypes.data_as(C_DOUBLE_P),
            int(turns),
            ctypes.byref(lost),
            ctypes.byref(lost_turn),
            ctypes.byref(lost_pos),
            ctypes.byref(status),
        )
        self._check_status("pyptc_track_particle_ring_loss", status)
        return values.copy(), {"lost": bool(lost.value), "lost_turn": lost_turn.value, "lost_pos": lost_pos.value}

    def track_bunch_with_losses(self, bunch: np.ndarray, turns: int = 1) -> tuple[np.ndarray, list[dict[str, int | bool]]]:
        rows = np.asarray(bunch, dtype=float).copy()
        if rows.ndim != 2 or rows.shape[1] != 6:
            raise ValueError(f"Expected an N x 6 bunch array, got {rows.shape}")
        p0c = self.scalar("ptc_get_p0c_")
        beta0 = self.scalar("ptc_get_beta0_")
        loss_info: list[dict[str, int | bool]] = []
        for particle_index in range(rows.shape[0]):
            x, xp, y, yp, z, d_e = rows[particle_index]
            ptc_coords = np.array([x, xp, y, yp, d_e / p0c, -z / beta0], dtype=float)
            tracked, info = self.track_particle_ptc_with_loss(ptc_coords, turns=turns)
            rows[particle_index] = [
                tracked[0],
                tracked[1],
                tracked[2],
                tracked[3],
                -tracked[5] * beta0,
                tracked[4] * p0c,
            ]
            loss_info.append({"particle": particle_index, **info})
        return rows, loss_info

    def set_acceleration(self, enabled: bool) -> None:
        self._set_flag("pyptc_set_acceleration", enabled)

    def set_ramping(self, enabled: bool) -> None:
        self._set_flag("pyptc_set_ramping", enabled)

    def set_modulation(self, enabled: bool) -> None:
        self._set_flag("pyptc_set_modulation", enabled)

    def set_cavity(self, enabled: bool) -> None:
        self._set_flag("pyptc_set_cavity", enabled)

    def _set_flag(self, symbol: str, enabled: bool) -> None:
        status = ctypes.c_int()
        getattr(self.lib, symbol)(1 if enabled else 0, ctypes.byref(status))
        self._check_status(symbol, status)

    def store_orbit_state(self) -> None:
        self._call_status_only("pyptc_store_orbit_state")

    def use_orbit_state(self) -> None:
        self._call_status_only("pyptc_use_orbit_state")

    def set_all_ramp(self) -> None:
        self._call_status_only("pyptc_set_all_ramp")

    def close_cavity_ring(self) -> None:
        self._call_status_only("pyptc_close_cavity_ring")

    def _call_status_only(self, symbol: str) -> None:
        status = ctypes.c_int()
        getattr(self.lib, symbol)(ctypes.byref(status))
        self._check_status(symbol, status)

    def energize_lattice(self, time_value: float | None = None) -> None:
        status = ctypes.c_int()
        use_t = 0 if time_value is None else 1
        self.lib.pyptc_energize_lattice(float(time_value or 0.0), use_t, ctypes.byref(status))
        self._check_status("pyptc_energize_lattice", status)

    def set_orbit_time(self, time_value: float) -> None:
        status = ctypes.c_int()
        self.lib.pyptc_set_orbit_time(float(time_value), ctypes.byref(status))
        self._check_status("pyptc_set_orbit_time", status)

    def initialize_cavity(self, fibre_index: int, table_file: str | Path) -> None:
        status = ctypes.c_int()
        encoded = str(Path(table_file).resolve()).encode()
        self.lib.pyptc_initialize_cavity(int(fibre_index), encoded, ctypes.byref(status))
        self._check_status("pyptc_initialize_cavity", status)

    def initialize_cavity_by_name(self, name: str, occurrence: int, table_file: str | Path) -> int:
        fibre_index = self._resolve(name, occurrence)
        self.initialize_cavity(fibre_index, table_file)
        return fibre_index

    def power_cavity(self, harmonic_number: int, volt: float, phase: float, epsf: float = 1.0e-8) -> None:
        status = ctypes.c_int()
        self.lib.pyptc_power_cavity(
            int(harmonic_number),
            float(volt),
            float(phase),
            float(epsf),
            ctypes.byref(status),
        )
        self._check_status("pyptc_power_cavity", status)

    def cavity_totalpath(self, enabled: bool) -> None:
        status = ctypes.c_int()
        self.lib.pyptc_cavity_totalpath(1 if enabled else 0, ctypes.byref(status))
        self._check_status("pyptc_cavity_totalpath", status)

    def configure_ac_magnet(
        self,
        fibre_index: int,
        dc: float,
        amplitude: float,
        phase_turns: float,
        d_ac: float,
        bn: Iterable[float] | None = None,
        an: Iterable[float] | None = None,
    ) -> None:
        bn_values = np.ascontiguousarray(list(bn or []), dtype=np.float64)
        an_values = np.ascontiguousarray(list(an or []), dtype=np.float64)
        n = max(len(bn_values), len(an_values))
        if len(bn_values) < n:
            bn_values = np.pad(bn_values, (0, n - len(bn_values)))
        if len(an_values) < n:
            an_values = np.pad(an_values, (0, n - len(an_values)))
        status = ctypes.c_int()
        self.lib.pyptc_configure_ac_magnet(
            int(fibre_index),
            float(dc),
            float(amplitude),
            float(phase_turns),
            float(d_ac),
            int(n),
            bn_values.ctypes.data_as(C_DOUBLE_P),
            an_values.ctypes.data_as(C_DOUBLE_P),
            ctypes.byref(status),
        )
        self._check_status("pyptc_configure_ac_magnet", status)

    def configure_ac_magnet_by_name(self, name: str, occurrence: int = 1, **kwargs) -> int:
        fibre_index = self._resolve(name, occurrence)
        self.configure_ac_magnet(fibre_index, **kwargs)
        return fibre_index

    def configure_ramp_magnet(self, fibre_index: int, table_file: str | Path, hgap: float) -> None:
        status = ctypes.c_int()
        encoded = str(Path(table_file).resolve()).encode()
        self.lib.pyptc_configure_ramp_magnet(int(fibre_index), encoded, float(hgap), ctypes.byref(status))
        self._check_status("pyptc_configure_ramp_magnet", status)

    def configure_ramp_magnet_by_name(self, name: str, occurrence: int, table_file: str | Path, hgap: float) -> int:
        fibre_index = self._resolve(name, occurrence)
        self.configure_ramp_magnet(fibre_index, table_file, hgap)
        return fibre_index

    def machine_summary(self) -> dict[str, float | int]:
        n_nodes = ctypes.c_int()
        n_harm = ctypes.c_int()
        l_ring = ctypes.c_double()
        gamma_t = ctypes.c_double()
        self.lib.ptc_get_ini_params_(
            ctypes.byref(n_nodes),
            ctypes.byref(n_harm),
            ctypes.byref(l_ring),
            ctypes.byref(gamma_t),
        )

        mass = ctypes.c_double()
        charge = ctypes.c_int()
        kinetic = ctypes.c_double()
        self.lib.ptc_get_syncpart_(ctypes.byref(mass), ctypes.byref(charge), ctypes.byref(kinetic))
        return {
            "n_nodes": n_nodes.value,
            "harmonic": n_harm.value,
            "circumference_m": l_ring.value,
            "gamma_t": gamma_t.value,
            "mass_gev": mass.value,
            "charge": charge.value,
            "kinetic_energy_gev": kinetic.value,
        }

    def scalar(self, name: str) -> float:
        value = ctypes.c_double()
        getattr(self.lib, name)(ctypes.byref(value))
        return value.value

    def node_twiss_orbit(self, node_index: int) -> dict[str, float | int]:
        idx = ctypes.c_int(int(node_index))
        values = [ctypes.c_double() for _ in range(13)]
        self.lib.ptc_get_twiss_for_node_(ctypes.byref(idx), *[ctypes.byref(value) for value in values])
        names = (
            "length",
            "betax",
            "betay",
            "alphax",
            "alphay",
            "etax",
            "etapx",
            "etay",
            "etapy",
            "orbitx",
            "orbitpx",
            "orbity",
            "orbitpy",
        )
        row: dict[str, float | int] = {"node_index": int(node_index)}
        row.update({name: value.value for name, value in zip(names, values)})
        return row

    def all_node_twiss_orbit(self) -> list[dict[str, float | int]]:
        return [self.node_twiss_orbit(index) for index in range(int(self.machine_summary()["n_nodes"]))]

    def task_type(self, node_index: int) -> int:
        idx = ctypes.c_int(int(node_index))
        task = ctypes.c_int()
        self.lib.ptc_get_task_type_(ctypes.byref(idx), ctypes.byref(task))
        return task.value

    def track_particle_ptc(self, node_index: int, coords: Iterable[float]) -> np.ndarray:
        idx = ctypes.c_int(int(node_index))
        values = [ctypes.c_double(float(value)) for value in coords]
        self.lib.ptc_track_particle_(ctypes.byref(idx), *[ctypes.byref(value) for value in values])
        return np.array([value.value for value in values], dtype=float)

    def track_bunch(self, bunch: np.ndarray, turns: int = 1, record_turns: bool = False) -> np.ndarray | list[np.ndarray]:
        rows = np.asarray(bunch, dtype=float).copy()
        if rows.ndim != 2 or rows.shape[1] != 6:
            raise ValueError(f"Expected an N x 6 bunch array, got {rows.shape}")

        snapshots: list[np.ndarray] = []
        n_nodes = int(self.machine_summary()["n_nodes"])
        for _turn in range(int(turns)):
            for node_index in range(n_nodes):
                idx = ctypes.c_int(node_index)
                self.lib.ptc_synchronous_set_(ctypes.byref(idx))
                p0c_enter = self.scalar("ptc_get_p0c_")
                beta_enter = self.scalar("ptc_get_beta0_")
                for particle_index in range(rows.shape[0]):
                    x, xp, y, yp, z, d_e = rows[particle_index]
                    ptc_coords = np.array([x, xp, y, yp, d_e / p0c_enter, -z / beta_enter], dtype=float)
                    tracked = self.track_particle_ptc(node_index, ptc_coords)
                    p0c_exit = self.scalar("ptc_get_p0c_")
                    beta_exit = self.scalar("ptc_get_beta0_")
                    rows[particle_index] = [
                        tracked[0],
                        tracked[1],
                        tracked[2],
                        tracked[3],
                        -tracked[5] * beta_exit,
                        tracked[4] * p0c_exit,
                    ]
                self.lib.ptc_synchronous_after_(ctypes.byref(idx))
            if record_turns:
                snapshots.append(rows.copy())
        return snapshots if record_turns else rows
