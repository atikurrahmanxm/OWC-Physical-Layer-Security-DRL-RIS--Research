"""Finite planar optical Reconfigurable Intelligent Surface (RIS) model.

Implements a specular mirror-array optical RIS for Visible Light Communications
under the geometric-optics / DC approximation. Features:
- Exact finite receiver entrance aperture clipping (Sutherland-Hodgman)
- Symmetric triangle quadrature integration of virtual-source Lambertian irradiance
- Optical power conservation bounded by mirror-intercepted power (Gauss-Legendre)
- Shared physical mirror normals across all transmitters and receivers per codebook state
- Five scenario-specific oracle codebook configurations:
  0: 'off' (inactive/stowed reference state with exact zero gain)
  1: 'alice_to_bob' (all tiles aimed Alice -> Bob)
  2: 'jammers_to_eve' (tiles distributed deterministically across friendly jammers -> Eve)
  3: 'split_bob_eve' (mixed: half tiles Alice -> Bob, remainder jammers -> Eve)
  4: 'neutral' (un-tilted nominal wall normal +y)
"""

from dataclasses import dataclass, field
from typing import Tuple, List, Dict, Any, Optional
import math
import numpy as np
from .config import VLCConfig


@dataclass
class OpticalRISConfig:
    """Configuration for finite-area optical RIS panel."""
    enabled: bool = True
    panel_center: tuple = (2.5, 0.25, 2.6)
    panel_width_m: float = 1.0
    panel_height_m: float = 0.5
    rows: int = 2
    cols: int = 3
    reflectivity: float = 0.85
    max_tilt_deg: float = 85.0

    def __post_init__(self):
        if not isinstance(self.enabled, bool):
            raise TypeError("enabled must be a boolean")
        if not isinstance(self.rows, (int, np.integer)) or isinstance(self.rows, bool) or self.rows < 1:
            raise ValueError(f"rows must be a positive integer, got {self.rows}")
        if not isinstance(self.cols, (int, np.integer)) or isinstance(self.cols, bool) or self.cols < 1:
            raise ValueError(f"cols must be a positive integer, got {self.cols}")
        if not np.isfinite(self.panel_width_m) or self.panel_width_m < 0.0:
            raise ValueError(f"panel_width_m must be non-negative and finite, got {self.panel_width_m}")
        if not np.isfinite(self.panel_height_m) or self.panel_height_m < 0.0:
            raise ValueError(f"panel_height_m must be non-negative and finite, got {self.panel_height_m}")
        if not np.isfinite(self.reflectivity) or not (0.0 <= self.reflectivity <= 1.0):
            raise ValueError(f"reflectivity must be in [0, 1], got {self.reflectivity}")
        if not np.isfinite(self.max_tilt_deg) or not (0.0 <= self.max_tilt_deg <= 90.0):
            raise ValueError(f"max_tilt_deg must be in [0, 90], got {self.max_tilt_deg}")
        center = np.asarray(self.panel_center, dtype=np.float64)
        if center.shape != (3,) or not np.isfinite(center).all():
            raise ValueError(f"panel_center must be a 3D coordinate tuple/array, got {self.panel_center}")


def compute_tile_basis(normal: np.ndarray) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Computes orthonormal basis (u, v, normal) for a planar tile.

    u corresponds to horizontal width (+x un-tilted),
    v corresponds to vertical height (+z un-tilted),
    normal corresponds to front normal (+y un-tilted, facing into room).
    """
    n0 = np.array([0.0, 1.0, 0.0], dtype=np.float64)
    u0 = np.array([1.0, 0.0, 0.0], dtype=np.float64)
    v0 = np.array([0.0, 0.0, 1.0], dtype=np.float64)

    n = np.asarray(normal, dtype=np.float64)
    norm_n = np.linalg.norm(n)
    if norm_n < 1e-12:
        raise ValueError("Tile normal must be non-zero")
    n = n / norm_n

    k = np.cross(n0, n)
    sin_theta = np.linalg.norm(k)
    cos_theta = float(np.dot(n0, n))

    if sin_theta < 1e-12:
        if cos_theta > 0:
            return u0.copy(), v0.copy(), n
        else:
            return -u0.copy(), v0.copy(), n

    axis = k / sin_theta

    def rotate_vec(w: np.ndarray) -> np.ndarray:
        return (w * cos_theta +
                np.cross(axis, w) * sin_theta +
                axis * np.dot(axis, w) * (1.0 - cos_theta))

    u = rotate_vec(u0)
    v = rotate_vec(v0)

    # Gram-Schmidt to enforce exact numerical orthonormality
    u = u - np.dot(u, n) * n
    norm_u = np.linalg.norm(u)
    if norm_u < 1e-12:
        raise ValueError("Degenerate basis vector u")
    u = u / norm_u

    v = v - np.dot(v, n) * n - np.dot(v, u) * u
    norm_v = np.linalg.norm(v)
    if norm_v < 1e-12:
        raise ValueError("Degenerate basis vector v")
    v = v / norm_v

    return u, v, n


def aim_normal(
    source_pos: np.ndarray,
    mirror_center: np.ndarray,
    rx_pos: np.ndarray,
    max_tilt_deg: float = 85.0
) -> np.ndarray:
    """Computes unit normal aimed from source_pos through mirror_center to rx_pos.

    Constrains the angle between the aimed normal and the nominal wall normal +y
    to be at most max_tilt_deg.
    """
    S = np.asarray(source_pos, dtype=np.float64)
    M = np.asarray(mirror_center, dtype=np.float64)
    R = np.asarray(rx_pos, dtype=np.float64)

    v_S = S - M
    dist_S = np.linalg.norm(v_S)
    if dist_S < 1e-12:
        return np.array([0.0, 1.0, 0.0], dtype=np.float64)
    u_S = v_S / dist_S

    v_R = R - M
    dist_R = np.linalg.norm(v_R)
    if dist_R < 1e-12:
        return np.array([0.0, 1.0, 0.0], dtype=np.float64)
    u_R = v_R / dist_R

    v_sum = u_S + u_R
    norm_sum = np.linalg.norm(v_sum)
    if norm_sum < 1e-12:
        return np.array([0.0, 1.0, 0.0], dtype=np.float64)
    n_ideal = v_sum / norm_sum

    # Constrain to cone of semi-angle max_tilt_deg around +y
    n0 = np.array([0.0, 1.0, 0.0], dtype=np.float64)
    cos_theta = float(np.dot(n_ideal, n0))
    cos_theta = np.clip(cos_theta, -1.0, 1.0)
    theta = float(np.arccos(cos_theta))

    theta_max = math.radians(max_tilt_deg)
    if theta > theta_max:
        n_perp = n_ideal - cos_theta * n0
        norm_perp = np.linalg.norm(n_perp)
        if norm_perp > 1e-12:
            u_perp = n_perp / norm_perp
            n_constrained = math.cos(theta_max) * n0 + math.sin(theta_max) * u_perp
        else:
            n_constrained = n0.copy()
        n_constrained = n_constrained / np.linalg.norm(n_constrained)
        return n_constrained

    return n_ideal


def clip_polygon_to_box(
    poly_vertices: List[np.ndarray],
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float
) -> List[np.ndarray]:
    """Clips 2D polygon against axis-aligned box using Sutherland-Hodgman algorithm."""
    if len(poly_vertices) < 3:
        return []

    def clip_edge(points, inside_fn, intersect_fn):
        out = []
        if not points:
            return out
        prev = points[-1]
        prev_inside = inside_fn(prev)
        for curr in points:
            curr_inside = inside_fn(curr)
            if curr_inside:
                if not prev_inside:
                    out.append(intersect_fn(prev, curr))
                out.append(curr)
            elif prev_inside:
                out.append(intersect_fn(prev, curr))
            prev = curr
            prev_inside = curr_inside
        return out

    pts = [np.asarray(p, dtype=np.float64) for p in poly_vertices]

    # Edge 1: x >= x_min
    pts = clip_edge(
        pts,
        lambda p: p[0] >= x_min,
        lambda p1, p2: np.array([x_min, p1[1] + (x_min - p1[0]) * (p2[1] - p1[1]) / (p2[0] - p1[0])])
    )
    # Edge 2: x <= x_max
    pts = clip_edge(
        pts,
        lambda p: p[0] <= x_max,
        lambda p1, p2: np.array([x_max, p1[1] + (x_max - p1[0]) * (p2[1] - p1[1]) / (p2[0] - p1[0])])
    )
    # Edge 3: y >= y_min
    pts = clip_edge(
        pts,
        lambda p: p[1] >= y_min,
        lambda p1, p2: np.array([p1[0] + (y_min - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1]), y_min])
    )
    # Edge 4: y <= y_max
    pts = clip_edge(
        pts,
        lambda p: p[1] <= y_max,
        lambda p1, p2: np.array([p1[0] + (y_max - p1[1]) * (p2[0] - p1[0]) / (p2[1] - p1[1]), y_max])
    )
    return pts


def polygon_area(pts: List[np.ndarray]) -> float:
    """Computes area of a 2D polygon using the Shoelace formula."""
    if len(pts) < 3:
        return 0.0
    area = 0.0
    n = len(pts)
    for i in range(n):
        area += pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1]
    return 0.5 * abs(area)


def integrate_triangle_quadrature(tri_pts: List[np.ndarray], integrand_fn) -> float:
    """Integrates integrand_fn(x, y) over a triangle using symmetric 3-point order-2 quadrature."""
    t1, t2, t3 = tri_pts
    area = 0.5 * abs((t2[0] - t1[0]) * (t3[1] - t1[1]) - (t3[0] - t1[0]) * (t2[1] - t1[1]))
    if area < 1e-18:
        return 0.0
    p1 = 0.5 * (t1 + t2)
    p2 = 0.5 * (t2 + t3)
    p3 = 0.5 * (t3 + t1)
    val = (integrand_fn(p1[0], p1[1]) +
           integrand_fn(p2[0], p2[1]) +
           integrand_fn(p3[0], p3[1]))
    return (area / 3.0) * val


def compute_tile_intercepted_fraction(
    source_pos: np.ndarray,
    mirror_center: np.ndarray,
    tile_basis_u: np.ndarray,
    tile_basis_v: np.ndarray,
    normal: np.ndarray,
    tile_side: float,
    lambertian_m: float
) -> float:
    """Integrates source Lambertian irradiance over the tile to find fraction of source

    optical power intercepted by the finite tile surface using 3x3 Gauss-Legendre quadrature (order 5).
    """
    if tile_side <= 0.0:
        return 0.0

    # 3-point Gauss-Legendre quadrature on [-1, 1]
    nodes = np.array([-np.sqrt(3.0 / 5.0), 0.0, np.sqrt(3.0 / 5.0)], dtype=np.float64)
    weights = np.array([5.0 / 9.0, 8.0 / 9.0, 5.0 / 9.0], dtype=np.float64)

    half_s = 0.5 * tile_side
    u_pts = half_s * nodes
    w_u = half_s * weights
    v_pts = half_s * nodes
    w_v = half_s * weights

    S = np.asarray(source_pos, dtype=np.float64)
    M = np.asarray(mirror_center, dtype=np.float64)
    n = np.asarray(normal, dtype=np.float64)
    u_vec = np.asarray(tile_basis_u, dtype=np.float64)
    v_vec = np.asarray(tile_basis_v, dtype=np.float64)

    total_fraction = 0.0
    for iu, u in enumerate(u_pts):
        for iv, v in enumerate(v_pts):
            Q = M + u * u_vec + v * v_vec
            d_vec = Q - S
            d = np.linalg.norm(d_vec)
            if d < 1e-9:
                continue
            # Downward LED optical axis [0, 0, -1]
            cos_phi_src = (S[2] - Q[2]) / d
            if cos_phi_src <= 0.0:
                continue
            # Angle of incidence onto mirror front normal
            cos_theta_inc = np.dot(S - Q, n) / d
            if cos_theta_inc <= 0.0:
                continue
            integrand = ((lambertian_m + 1.0) / (2.0 * np.pi * (d ** 2)) *
                         (cos_phi_src ** lambertian_m) * cos_theta_inc)
            total_fraction += w_u[iu] * w_v[iv] * integrand

    return float(total_fraction)


def compute_single_tile_optical_gain(
    source_pos: np.ndarray,
    rx_pos: np.ndarray,
    mirror_center: np.ndarray,
    normal: np.ndarray,
    tile_side: float,
    config: VLCConfig,
    reflectivity: float
) -> float:
    """Computes optical channel gain G for a single specular tile between source_pos and rx_pos.

    Aggregates num_leds_per_fixture exactly once.
    Clips against the effective entrance aperture of the receiver.
    Enforces power conservation bounded by reflected intercepted optical power.
    """
    if reflectivity <= 0.0 or tile_side <= 0.0:
        return 0.0

    S = np.asarray(source_pos, dtype=np.float64)
    R = np.asarray(rx_pos, dtype=np.float64)
    M = np.asarray(mirror_center, dtype=np.float64)
    n = np.asarray(normal, dtype=np.float64)
    norm_n = np.linalg.norm(n)
    if norm_n < 1e-12:
        return 0.0
    n = n / norm_n

    # 1. Halfspace check: both source and receiver must reside in front of mirror
    dot_S = float(np.dot(S - M, n))
    dot_R = float(np.dot(R - M, n))
    if dot_S <= 1e-12 or dot_R <= 1e-12:
        return 0.0

    u, v, n = compute_tile_basis(n)

    # Lambertian order m
    phi_half = math.radians(config.phi_half_deg)
    lambertian_m = float(-math.log(2.0) / math.log(math.cos(phi_half)))

    # 2. Intercepted optical power fraction (power conservation bound)
    F_intercepted = compute_tile_intercepted_fraction(
        S, M, u, v, n, tile_side, lambertian_m
    )
    G_bound = float(reflectivity * config.num_leds_per_fixture * F_intercepted)
    if G_bound <= 1e-18:
        return 0.0

    # 3. Virtual source position and reflected optical axis
    S_prime = S - 2.0 * dot_S * n
    led_axis = np.array([0.0, 0.0, -1.0], dtype=np.float64)
    led_axis_prime = led_axis - 2.0 * np.dot(led_axis, n) * n
    norm_axis = np.linalg.norm(led_axis_prime)
    if norm_axis < 1e-12:
        return 0.0
    led_axis_prime = led_axis_prime / norm_axis

    # 4. Mirror corners in 3D
    half_s = 0.5 * tile_side
    corners = [
        M - half_s * u - half_s * v,
        M + half_s * u - half_s * v,
        M + half_s * u + half_s * v,
        M - half_s * u + half_s * v,
    ]

    # 5. Project mirror corners from S' onto horizontal receiver plane z = R[2]
    R_z = float(R[2])
    S_prime_z = float(S_prime[2])
    delta_z_total = R_z - S_prime_z

    proj_pts = []
    for V_k in corners:
        w_z = V_k[2] - S_prime_z
        if abs(w_z) < 1e-12:
            return 0.0  # Ray parallel to receiver plane
        lam = delta_z_total / w_z
        if lam <= 1.0 or not np.isfinite(lam):
            return 0.0  # Backward or horizon projection
        P_k = S_prime + lam * (V_k - S_prime)
        proj_pts.append(np.array([P_k[0], P_k[1]]))

    proj_area = polygon_area(proj_pts)
    if proj_area < 1e-16:
        return 0.0

    # 6. Effective entrance aperture of receiver
    # Area = detector_area * n0^2 / sin^2(fov)
    fov_rad = math.radians(config.fov_deg)
    sin_fov = math.sin(fov_rad)
    g_conc = (config.n0 ** 2) / (sin_fov ** 2)
    A_eff = config.detector_area * g_conc
    w_eff = math.sqrt(A_eff)
    half_w = 0.5 * w_eff

    x_min = R[0] - half_w
    x_max = R[0] + half_w
    y_min = R[1] - half_w
    y_max = R[1] + half_w

    # 7. Sutherland-Hodgman clipping
    clipped_pts = clip_polygon_to_box(proj_pts, x_min, x_max, y_min, y_max)
    if len(clipped_pts) < 3:
        return 0.0
    clipped_area = polygon_area(clipped_pts)
    if clipped_area < 1e-18:
        return 0.0

    # 8. Triangulate clipped polygon and integrate virtual-source Lambertian irradiance
    def integrand(x, y):
        P = np.array([x, y, R_z], dtype=np.float64)
        L_vec = P - S_prime
        L = np.linalg.norm(L_vec)
        if L < 1e-9:
            return 0.0
        r_hat = L_vec / L
        # Irradiance angle relative to virtual LED axis
        cos_phi = float(np.dot(r_hat, led_axis_prime))
        if cos_phi <= 0.0:
            return 0.0
        # Incidence angle on upward-facing photodiode [0, 0, 1]
        cos_psi = (S_prime_z - R_z) / L
        if cos_psi <= 0.0:
            return 0.0
        cos_psi = np.clip(cos_psi, -1.0, 1.0)
        psi = math.acos(cos_psi)
        if psi > fov_rad:
            return 0.0
        return float(((lambertian_m + 1.0) / (2.0 * math.pi * (L ** 2))) *
                     (cos_phi ** lambertian_m) * cos_psi)

    total_irradiance = 0.0
    c0 = clipped_pts[0]
    for j in range(len(clipped_pts) - 2):
        tri = [c0, clipped_pts[j + 1], clipped_pts[j + 2]]
        total_irradiance += integrate_triangle_quadrature(tri, integrand)

    G_geom = float(reflectivity * config.num_leds_per_fixture * total_irradiance)
    G_final = min(G_geom, G_bound)
    return float(G_final)


class OpticalRIS:
    """Finite planar specular optical RIS channel simulator.

    Computes reflected electrical channel gains (h_AB, h_AE, h_JB, h_JE) for
    Alice, friendly jammers, Bob, and Eve under stored codebook mirror normals.
    """

    def __init__(
        self,
        config: Optional[VLCConfig] = None,
        ris_config: Optional[OpticalRISConfig] = None,
        bob_pos: Optional[np.ndarray] = None,
        eve_pos: Optional[np.ndarray] = None
    ):
        self.config = config if config is not None else VLCConfig()
        self.ris_config = ris_config if ris_config is not None else OpticalRISConfig()

        self.bob_pos = np.asarray(
            bob_pos if bob_pos is not None else self.config.bob_pos,
            dtype=np.float64
        ).copy()
        self.eve_pos = np.asarray(
            eve_pos if eve_pos is not None else self.config.eve_pos,
            dtype=np.float64
        ).copy()

        self._init_geometry()
        self._init_codebook()
        self._gain_cache: Dict[int, Tuple[float, float, np.ndarray, np.ndarray]] = {}

    def _init_geometry(self):
        rc = self.ris_config
        self.panel_center = np.asarray(rc.panel_center, dtype=np.float64)
        self.rows = int(rc.rows)
        self.cols = int(rc.cols)
        self.num_tiles = self.rows * self.cols
        self.panel_width = float(rc.panel_width_m)
        self.panel_height = float(rc.panel_height_m)
        self.bounding_area = self.panel_width * self.panel_height

        if self.panel_width > 0.0 and self.panel_height > 0.0:
            self.pitch_x = self.panel_width / self.cols
            self.pitch_z = self.panel_height / self.rows
            min_pitch = min(self.pitch_x, self.pitch_z)
            self.clearance_diameter = 0.9 * min_pitch
            self.tile_side = self.clearance_diameter / math.sqrt(2.0)
            self.tile_area = self.tile_side ** 2
            self.actual_reflecting_area = self.num_tiles * self.tile_area
        else:
            self.pitch_x = 0.0
            self.pitch_z = 0.0
            self.clearance_diameter = 0.0
            self.tile_side = 0.0
            self.tile_area = 0.0
            self.actual_reflecting_area = 0.0

        # Construct tile centers in panel nominal plane (x-z plane at y = panel_center[1])
        centers = []
        x0 = self.panel_center[0] - 0.5 * self.panel_width
        z0 = self.panel_center[2] - 0.5 * self.panel_height
        y_val = self.panel_center[1]

        for r in range(self.rows):
            for c in range(self.cols):
                cx = x0 + (c + 0.5) * self.pitch_x if self.panel_width > 0 else self.panel_center[0]
                cz = z0 + (r + 0.5) * self.pitch_z if self.panel_height > 0 else self.panel_center[2]
                centers.append(np.array([cx, y_val, cz], dtype=np.float64))
        self.tile_centers = centers

    def _init_codebook(self):
        if not self.ris_config.enabled:
            self.configuration_names: List[str] = ['off']
            self.num_configurations: int = 1
            self._codebook_normals: Dict[int, List[np.ndarray]] = {
                0: [np.array([0.0, 1.0, 0.0], dtype=np.float64) for _ in range(self.num_tiles)]
            }
            return

        self.configuration_names: List[str] = [
            'off',
            'alice_to_bob',
            'jammers_to_eve',
            'split_bob_eve',
            'neutral'
        ]
        self.num_configurations: int = 5

        normals_by_config: Dict[int, List[np.ndarray]] = {}
        n_neutral = np.array([0.0, 1.0, 0.0], dtype=np.float64)

        # 0: 'off' (stowed/inactive reference state)
        normals_by_config[0] = [n_neutral.copy() for _ in range(self.num_tiles)]

        # 1: 'alice_to_bob' (all tiles aimed Alice -> Bob)
        normals_1 = []
        for M in self.tile_centers:
            n = aim_normal(self.config.alice_pos, M, self.bob_pos, self.ris_config.max_tilt_deg)
            normals_1.append(n)
        normals_by_config[1] = normals_1

        # 2: 'jammers_to_eve' (deterministic round-robin assignment among friendly jammers)
        normals_2 = []
        num_jammers = len(self.config.jammer_positions)
        for i, M in enumerate(self.tile_centers):
            j_idx = i % num_jammers
            j_pos = self.config.jammer_positions[j_idx]
            n = aim_normal(j_pos, M, self.eve_pos, self.ris_config.max_tilt_deg)
            normals_2.append(n)
        normals_by_config[2] = normals_2

        # 3: 'split_bob_eve' (half tiles Alice -> Bob, half jammers -> Eve)
        normals_3 = []
        n_ab = self.num_tiles // 2
        for i, M in enumerate(self.tile_centers):
            if i < n_ab:
                n = aim_normal(self.config.alice_pos, M, self.bob_pos, self.ris_config.max_tilt_deg)
            else:
                j_idx = (i - n_ab) % num_jammers
                j_pos = self.config.jammer_positions[j_idx]
                n = aim_normal(j_pos, M, self.eve_pos, self.ris_config.max_tilt_deg)
            normals_3.append(n)
        normals_by_config[3] = normals_3

        # 4: 'neutral' (un-tilted nominal wall normal +y)
        normals_by_config[4] = [n_neutral.copy() for _ in range(self.num_tiles)]

        self._codebook_normals = normals_by_config

    def compute_single_tile_gain(
        self,
        source_pos: np.ndarray,
        rx_pos: np.ndarray,
        mirror_center: np.ndarray,
        normal: np.ndarray,
        tile_side: float,
        electrical: bool = True
    ) -> float:
        """Helper to compute optical or electrical gain of a single specular tile.

        Exposed for subdivision and conservation verification tests.
        """
        g_opt = compute_single_tile_optical_gain(
            source_pos=source_pos,
            rx_pos=rx_pos,
            mirror_center=mirror_center,
            normal=normal,
            tile_side=tile_side,
            config=self.config,
            reflectivity=self.ris_config.reflectivity
        )
        if not electrical:
            return g_opt
        return float(self.config.pd_responsivity * self.config.eta * g_opt)

    def _compute_gains_for_index(self, index: int) -> Tuple[float, float, np.ndarray, np.ndarray]:
        num_jammers = len(self.config.jammer_positions)
        zeros_tuple = (
            0.0,
            0.0,
            np.zeros(num_jammers, dtype=np.float64),
            np.zeros(num_jammers, dtype=np.float64)
        )

        if not self.ris_config.enabled or index == 0:
            return zeros_tuple
        if self.ris_config.reflectivity <= 0.0 or self.tile_side <= 0.0:
            return zeros_tuple

        normals = self._codebook_normals[index]

        g_AB_total = 0.0
        g_AE_total = 0.0
        g_JB_list = [0.0] * num_jammers
        g_JE_list = [0.0] * num_jammers

        # Model all links under the SAME physical mirror normals
        for i, M in enumerate(self.tile_centers):
            n = normals[i]
            # Alice -> Bob / Eve
            g_AB_total += compute_single_tile_optical_gain(
                self.config.alice_pos, self.bob_pos, M, n,
                self.tile_side, self.config, self.ris_config.reflectivity
            )
            g_AE_total += compute_single_tile_optical_gain(
                self.config.alice_pos, self.eve_pos, M, n,
                self.tile_side, self.config, self.ris_config.reflectivity
            )

            # Jammers -> Bob / Eve
            for j_idx, j_pos in enumerate(self.config.jammer_positions):
                g_JB_list[j_idx] += compute_single_tile_optical_gain(
                    j_pos, self.bob_pos, M, n,
                    self.tile_side, self.config, self.ris_config.reflectivity
                )
                g_JE_list[j_idx] += compute_single_tile_optical_gain(
                    j_pos, self.eve_pos, M, n,
                    self.tile_side, self.config, self.ris_config.reflectivity
                )

        # Convert optical path gain to electrical gain: h = R * eta * G
        conversion = float(self.config.pd_responsivity * self.config.eta)
        h_AB = float(conversion * g_AB_total)
        h_AE = float(conversion * g_AE_total)
        h_JB = np.array([conversion * g for g in g_JB_list], dtype=np.float64)
        h_JE = np.array([conversion * g for g in g_JE_list], dtype=np.float64)

        return h_AB, h_AE, h_JB, h_JE

    def get_reflected_gains(self, index: int) -> Tuple[float, float, np.ndarray, np.ndarray]:
        """Returns electrical tuple: (h_AB_ris, h_AE_ris, h_JB_ris_vec, h_JE_ris_vec)."""
        if isinstance(index, bool) or not isinstance(index, (int, np.integer)):
            raise TypeError(f"Configuration index must be an integer, got {type(index).__name__}")
        idx = int(index)
        if idx < 0 or idx >= self.num_configurations:
            raise IndexError(
                f"Configuration index {idx} out of range [0, {self.num_configurations - 1}]"
            )

        if idx not in self._gain_cache:
            self._gain_cache[idx] = self._compute_gains_for_index(idx)
        return self._gain_cache[idx]

    def metadata(self) -> Dict[str, Any]:
        """Returns fully JSON-serializable dictionary documenting geometry, normals, and assumptions."""
        fov_rad = math.radians(self.config.fov_deg)
        sin_fov = math.sin(fov_rad)
        g_conc = (self.config.n0 ** 2) / (sin_fov ** 2)
        a_eff = self.config.detector_area * g_conc

        configs_meta = {}
        for idx, name in enumerate(self.configuration_names):
            normals = self._codebook_normals.get(idx, [])
            configs_meta[name] = {
                'index': idx,
                'tile_normals': [n.tolist() for n in normals]
            }

        return {
            'enabled': bool(self.ris_config.enabled),
            'panel_center': self.panel_center.tolist(),
            'panel_width_m': float(self.panel_width),
            'panel_height_m': float(self.panel_height),
            'panel_bounding_area_m2': float(self.bounding_area),
            'rows': int(self.rows),
            'cols': int(self.cols),
            'num_tiles': int(self.num_tiles),
            'grid_pitch_x_m': float(self.pitch_x),
            'grid_pitch_z_m': float(self.pitch_z),
            'tile_clearance_diameter_m': float(self.clearance_diameter),
            'tile_side_m': float(self.tile_side),
            'tile_area_m2': float(self.tile_area),
            'actual_reflecting_area_m2': float(self.actual_reflecting_area),
            'reflectivity': float(self.ris_config.reflectivity),
            'max_tilt_deg': float(self.ris_config.max_tilt_deg),
            'nominal_normal': [0.0, 1.0, 0.0],
            'tile_centers': [c.tolist() for c in self.tile_centers],
            'receiver_effective_entrance_area_m2': float(a_eff),
            'optical_concentrator_gain': float(g_conc),
            'num_configurations': int(self.num_configurations),
            'configuration_names': list(self.configuration_names),
            'configurations': configs_meta,
            'quadrature': {
                'receiver_integration_rule': 'symmetric 3-point triangle quadrature (order 2)',
                'receiver_quadrature_order': 2,
                'mirror_interception_rule': '3x3 Gauss-Legendre quadrature (order 5)',
                'mirror_quadrature_order': 5,
            },
            'physical_assumptions': {
                'optics_model': 'Finite planar specular mirror array with image-source virtual emitters and receiver effective entrance aperture clipping',
                'dc_approximation': 'Direct-current / low-frequency approximation, symbol duration >> propagation delay, negligible delay dispersion and ISI',
                'incoherent_im_dd': 'Intensity modulation with direct detection; scalar optical power addition, no RF complex phase shifts',
                'lambertian_source': 'Co-located Lambertian LED emitters per fixture, downward optical axis [0, 0, -1]',
                'no_diffraction': 'Geometric optics approximation without wave diffraction',
                'no_diffuse_scattering': 'Specular mirror reflection only; diffuse wall reflections ignored',
                'no_blockage': 'Unobstructed line of sight between sources, mirrors, and receivers',
                'power_conservation': 'Collected tile optical power strictly bounded by incident intercepted optical power multiplied by reflectivity',
                'shared_normals': 'Physical mirror normals are fixed per codebook state and shared across all transmitters and receivers',
                'off_state': 'Configuration 0 is an inactive/stowed zero-reflection reference state with exact zero gain',
                'fov_enforcement': 'Receiver field of view strictly enforced at all integration sample points; rays exceeding FoV yield zero gain'
            }
        }
