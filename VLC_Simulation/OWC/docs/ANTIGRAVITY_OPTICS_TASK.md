# Antigravity implementation task: finite-area optical RIS

The user explicitly requests using Antigravity to implement this research extension. Read `AGENTS.md` and `Agent.MD`. Other integration code is already being written; avoid overlapping edits.

## Files you may create

- `vlc/ris.py`
- `tests/test_ris_optics.py`
- Optional `docs/RIS_OPTICS_DERIVATION.md`

Do not change other source files. Use built-in file read/write/edit tools. Do not use terminal/command tools in this headless session: they require unavailable interactive approval. The integrating agent will run the tests. Do not change settings, credentials, install packages, commit or delete existing work.

## Required API (integration depends on these exact names)

```python
@dataclass
class OpticalRISConfig:
    enabled: bool = True
    panel_center: tuple = (2.5, 0.25, 2.6)
    panel_width_m: float = 1.0
    panel_height_m: float = 0.5
    rows: int = 2
    cols: int = 3
    reflectivity: float = 0.85
    max_tilt_deg: float = 85.0

class OpticalRIS:
    def __init__(self, config, ris_config, bob_pos=None, eve_pos=None): ...
    num_configurations: int
    configuration_names: list[str]
    def get_reflected_gains(self, index):
        # ELECTRICAL tuple: (h_AB_ris,h_AE_ris,h_JB_ris_vec,h_JE_ris_vec)
        ...
    def metadata(self): ... # fully JSON serializable incl geometry/actual area/normals/assumptions
```

The underlying `VLCConfig` is paper mode. Compute optical path fractions first, aggregate `num_leds_per_fixture` exactly once, and convert through `pd_responsivity*eta` exactly once. Model every Alice/jammer to Bob/Eve RIS path under the SAME physical mirror normals for each codebook configuration.

## Scientific model to implement

Use finite planar specular mirrors with image-source geometry and finite receiver-aperture clipping. This is a geometric-optics/DC approximation for small co-located Lambertian LED sources, no diffraction, delay/ISI, diffuse reflections, occlusion or hidden Eve detector. State all assumptions; do not insert arbitrary RIS gain factors or RF complex phases.

The panel's nominal plane is x-z, inward wall normal +y; its 0.25 m standoff permits mirror rotation inside the room. Grid centers partition panel width/height. Use square tiles whose rotation-clearance diameter is 0.9*min(grid pitches), so square side = diameter/sqrt(2). Report actual reflecting area separately from panel bounding area. This avoids colliding elements when tilted. Allow zero reflectivity or zero area to yield exact zero reflection. Reject invalid dimensions, indices, normals and reflectivity outside [0,1]. Disabled config may expose only off; enabled config should have stable codebook size even if no path reaches a receiver.

Codebook: five static scenario-specific configurations named off, alice_to_bob, jammers_to_eve, split_bob_eve, neutral. Normals aimed from a source S through mirror center M to receiver R use normalize(normalize(S-M)+normalize(R-M)); constrain active normals to max_tilt_deg from +y. For jammer-focused patterns assign tiles deterministically across all friendly jammer fixtures. Mixed assigns some tiles Alice-to-Bob, others jammer-to-Eve. This is an oracle-geometry codebook, not unrestricted continuous orientation learning. Index0 must yield exact0 reflected gains. Explicitly describe off as an inactive/covered/stowed zero-reflection reference state; do not imply fixed-reflectivity mirrors are transparent without a stated deactivation assumption.

For a tile center M and unit normal n, virtual source S'=S-2*n*dot(n,S-M); virtual LED axis is its reflected downward normal. Require source and receiver on the reflecting halfspace. Mirror corners project from S' onto the horizontal receiver plane. Reject invalid horizon/backward projections. Clip the projected convex quadrilateral against a square effective entrance aperture centered at the receiver with area `detector_area*n0**2/sin(fov)**2`. Integrate virtual-source Lambertian irradiance over the clipped polygon by triangle quadrature; enforce receiver FoV at integration samples. Do NOT multiply the concentrator gain again after using the enlarged effective entrance area.

At receiver sample point R, image-source DC contribution per differential entrance area is

`rho * N_LED * (m+1)/(2*pi*L**2) * cos(phi)**m * cos(psi) * dA_eff`,

with L=|R-S'|, actual LED irradiance angle obtained from reflected LED axis, upward PD normal and FoV gate. On valid specular paths this image distance equals total source-mirror-receiver path length.

Also integrate source irradiance over each finite mirror to compute intercepted optical power (using actual source-to-mirror distance, original downward LED axis and mirror incidence cosine). Bound each tile's collected output by its reflected intercepted power. State the numerical quadrature order. Under the nominal geometry a number of wall-to-Eve paths can be outside the upward-facing PD's FoV: keep them zero instead of inventing gain. Exact finite aperture clipping is preferred over a center-ray binary visibility model, which can overcount arbitrarily small mirrors.

Implement clipping and quadrature with NumPy (already installed); no new geometry packages. Convex polygon clipping, shoelace area and triangle integration are sufficient.

## Independent tests to add

- disabled, rho0 and area0 produce exact zero optical/electrical RIS gains;
- aiming a tile toward a receiver yields a valid positive path under a deliberately FoV-feasible geometry;
- backside/FoV-invalid paths yield zero;
- shrinking a tile below the projected receiver footprint reduces gain;
- coplanar finite-mirror subdivision conserves integrated gain within declared quadrature tolerance (if expose helper);
- gain never exceeds reflected intercepted power;
- reflectivity scales gain linearly, LED count and R*eta each apply once;
- all sources use the same stored normals, not per-link re-aiming;
- invalid settings/index reject clearly;
- deterministic metadata/codebook and stable receiver co-location behavior.

Do not claim the model is experimentally validated or that RIS improves secrecy before the integrating agent runs measured studies. End with a concise implementation summary and any derivation limitations.
