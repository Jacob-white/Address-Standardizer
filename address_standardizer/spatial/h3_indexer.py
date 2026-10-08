"""
Uber H3 cell identifiers: wrapper around the ``h3`` package with an approximate fallback.
=========================================================================================
With the ``h3`` package installed (``pip install h3``) every function here is real H3 and the identifiers are
interoperable with other H3 tooling.

Without it, ``lat_lng_to_h3`` falls back to a *stable local grid bucket* that is formatted like an H3 index but is
**not** H3: the cell ids do not match Uber H3 and must not be exchanged with other systems. It exists only so the
spatial engine can bucket points when ``h3`` is absent. Operations that need true H3 geometry (``k_ring``,
``h3_distance``) raise ``NotImplementedError`` in that mode rather than return made-up answers. Use
``h3_backend()`` to find out which mode is active.
"""

import math
import re
from typing import List, Tuple

H3_HEX_PATTERN = re.compile(r"^[0-9a-f]{15}$")

try:
    import h3 as _h3_lib  # type: ignore
    _HAS_COMPILED_H3 = True
except ImportError:
    _h3_lib = None
    _HAS_COMPILED_H3 = False


def has_compiled_h3() -> bool:
    """Returns True if the compiled C h3 library is installed."""
    return _HAS_COMPILED_H3


def h3_backend() -> str:
    """``"h3"`` when real H3 is in use, ``"approximate-grid"`` for the non-interoperable fallback."""
    return "h3" if _HAS_COMPILED_H3 and _h3_lib is not None else "approximate-grid"


def _validate_lat_lng(lat: float, lng: float, resolution: int) -> None:
    if not (math.isfinite(lat) and math.isfinite(lng)):
        raise ValueError(f"Coordinates must be finite: lat={lat}, lng={lng}")
    if not -90.0 <= lat <= 90.0:
        raise ValueError(f"Latitude out of range [-90, 90]: {lat}")
    if not -180.0 <= lng <= 180.0:
        raise ValueError(f"Longitude out of range [-180, 180]: {lng}")
    if not isinstance(resolution, int) or isinstance(resolution, bool) or not 0 <= resolution <= 15:
        raise ValueError(f"Resolution must be an integer in [0, 15]: {resolution!r}")


def _axial_round(q: float, r: float) -> Tuple[int, int]:
    """Rounds continuous axial coordinates to nearest discrete hexagonal lattice point."""
    x = q
    z = r
    y = -x - z
    rx = round(x)
    ry = round(y)
    rz = round(z)
    x_diff = abs(rx - x)
    y_diff = abs(ry - y)
    z_diff = abs(rz - z)
    if x_diff > y_diff and x_diff > z_diff:
        rx = -ry - rz
    elif y_diff > z_diff:
        ry = -rx - rz
    else:
        rz = -rx - ry
    return rx, rz


def _pure_python_lat_lng_to_h3(lat: float, lng: float, resolution: int = 10) -> str:
    """Pure-Python algorithmic calculation of standard 15-char H3 index at specified resolution."""
    lat_clamped = max(-90.0, min(90.0, float(lat)))
    lng_clamped = (float(lng) + 180.0) % 360.0 - 180.0
    lat_rad = math.radians(lat_clamped)
    cos_lat = max(1e-6, math.cos(lat_rad))

    # Base Resolution 10 scale (in degrees)
    scale = 0.000592 * (3.0 ** (10 - resolution))

    x = lng_clamped * cos_lat
    y = lat_clamped

    q_cont = (math.sqrt(3.0) / 3.0 * x - 1.0 / 3.0 * y) / scale
    r_cont = (2.0 / 3.0 * y) / scale

    q, r = _axial_round(q_cont, r_cont)

    q_u = (q + (1 << 24)) & 0x1FFFFFF
    r_u = (r + (1 << 24)) & 0x1FFFFFF
    base_cell = (abs(q_u ^ r_u) % 122) & 0x7F

    digits = 0
    q_work, r_work = q_u, r_u
    for i in range(min(10, resolution)):
        digit = (q_work + r_work * 2 + i) % 7
        digits = (digits << 3) | digit
        q_work >>= 2
        r_work >>= 2

    unused_res = 15 - resolution
    unused_mask = (1 << (unused_res * 3)) - 1 if unused_res > 0 else 0

    val = (
        (1 << 59)
        | ((resolution & 0xF) << 52)
        | (base_cell << 45)
        | ((digits & 0x3FFFFFFF) << (unused_res * 3))
        | unused_mask
    )
    return f"{val:015x}"


def lat_lng_to_h3(lat: float, lng: float, resolution: int = 10) -> str:
    """
    Encodes (latitude, longitude) into a 15-character lowercase H3 cell index.
    Defaults to Resolution 10 (~65m hexagon edge length). Raises ``ValueError`` for non-finite or out-of-range input.
    With the ``h3`` package this is real H3; otherwise see the module docstring (non-interoperable bucket id).
    """
    _validate_lat_lng(lat, lng, resolution)
    if _HAS_COMPILED_H3 and _h3_lib is not None:
        if hasattr(_h3_lib, "latlng_to_cell"):
            return str(_h3_lib.latlng_to_cell(lat, lng, resolution)).lower()
        if hasattr(_h3_lib, "geo_to_h3"):
            return str(_h3_lib.geo_to_h3(lat, lng, resolution)).lower()
    return _pure_python_lat_lng_to_h3(lat, lng, resolution)


def is_valid_h3(h3_index: str) -> bool:
    """Validates whether an input string is a valid 15-character hex H3 index."""
    if not isinstance(h3_index, str) or not H3_HEX_PATTERN.match(h3_index.strip().lower()):
        return False
    val = int(h3_index.strip(), 16)
    mode = (val >> 59) & 0xF
    res = (val >> 52) & 0xF
    return mode == 1 and 0 <= res <= 15


def h3_to_int(h3_index: str) -> int:
    """Converts 15-char hex H3 index into a 64-bit integer."""
    if not is_valid_h3(h3_index):
        raise ValueError(f"Invalid H3 index: {h3_index}")
    return int(h3_index.strip(), 16)


def int_to_h3(h3_int: int) -> str:
    """Converts 64-bit integer back to a 15-character hex H3 index string."""
    h3_str = f"{h3_int:015x}"
    if not is_valid_h3(h3_str):
        raise ValueError(f"Invalid integer representation for H3 index: {h3_int}")
    return h3_str


def k_ring(h3_index: str, ring_size: int = 1) -> List[str]:
    """Generates all neighbor cell indices within ring_size steps."""
    clean = h3_index.strip().lower()
    if not is_valid_h3(clean):
        raise ValueError(f"Invalid H3 index: {h3_index}")

    if ring_size <= 0:
        return [clean]

    if _HAS_COMPILED_H3 and _h3_lib is not None:
        if hasattr(_h3_lib, "grid_disk"):
            return sorted([str(c).lower() for c in _h3_lib.grid_disk(clean, ring_size)])
        if hasattr(_h3_lib, "k_ring"):
            return sorted([str(c).lower() for c in _h3_lib.k_ring(clean, ring_size)])

    raise NotImplementedError("k_ring needs the 'h3' package (pip install h3); the fallback grid has no real topology")


def h3_distance(origin: str, destination: str) -> int:
    """Computes grid distance between two H3 cells."""
    orig = origin.strip().lower()
    dest = destination.strip().lower()
    if not is_valid_h3(orig) or not is_valid_h3(dest):
        raise ValueError(f"Invalid H3 cell: {origin} or {destination}")
    if orig == dest:
        return 0

    if _HAS_COMPILED_H3 and _h3_lib is not None:
        if hasattr(_h3_lib, "grid_distance"):
            try:
                return int(_h3_lib.grid_distance(orig, dest))
            except Exception as exc:  # h3 raises when the cells are too far apart or span a pentagon
                raise ValueError(f"H3 grid distance undefined for {origin} -> {destination}: {exc}") from exc
        if hasattr(_h3_lib, "h3_distance"):
            return int(_h3_lib.h3_distance(orig, dest))

    raise NotImplementedError("h3_distance needs the 'h3' package (pip install h3)")


def h3_to_parent(h3_index: str, parent_res: int) -> str:
    """Returns parent cell index at a coarser resolution."""
    clean = h3_index.strip().lower()
    if not is_valid_h3(clean):
        raise ValueError(f"Invalid H3 index: {h3_index}")

    if _HAS_COMPILED_H3 and _h3_lib is not None:
        if hasattr(_h3_lib, "cell_to_parent"):
            return str(_h3_lib.cell_to_parent(clean, parent_res)).lower()
        if hasattr(_h3_lib, "h3_to_parent"):
            return str(_h3_lib.h3_to_parent(clean, parent_res)).lower()

    val = int(clean, 16)
    cur_res = (val >> 52) & 0xF
    if parent_res > cur_res:
        raise ValueError(f"Parent resolution {parent_res} cannot be finer than current {cur_res}")
    if parent_res < 0:
        raise ValueError(f"Parent resolution {parent_res} cannot be negative")

    unused_res = 15 - parent_res
    unused_mask = (1 << (unused_res * 3)) - 1 if unused_res > 0 else 0

    mode_and_base = val & ((0xF << 59) | (0x7F << 45))
    digits_mask = ((1 << 45) - 1) & ~((1 << (unused_res * 3)) - 1)
    retained_digits = val & digits_mask

    new_val = mode_and_base | ((parent_res & 0xF) << 52) | retained_digits | unused_mask
    return f"{new_val:015x}"
