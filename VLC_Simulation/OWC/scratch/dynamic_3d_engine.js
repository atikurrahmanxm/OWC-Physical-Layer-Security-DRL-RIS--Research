/* =========================================================================
   DYNAMIC 3D VLC / OPTICAL RIS VISUALIZER & DRL REPLAY ENGINE
   =========================================================================
   Pure JavaScript + Canvas 2D Perspective Engine (Dependency-free & offline).
   Physics & channel gains are computed strictly by the Python backend.
   Animation depicts link activity based on computed positive gains (h > 0).
*/
(() => {
  const canvas = document.getElementById('room3D');
  if (!canvas) return;
  const ctx = canvas.getContext('2d');

  // Backend state cache
  let backendData = null;

  // Camera & View Transform State
  let yaw = -0.65;      // Azimuth angle around room center
  let pitch = 0.55;     // Elevation angle
  let zoom = 1.0;       // Scale multiplier
  let panX = 0, panY = 0;
  let activeCameraMode = 'orbit';

  // Animation & Pulse Flow State
  let isPlaying = true;
  let simSpeed = 1.0;
  let animTime = 0;
  let lastTimestamp = performance.now();

  // Layer Visibility Filters
  const layers = {
    direct: true,
    reflected: true,
    jammers: true,
    normals: true,
    grid: true,
    labels: true
  };

  // RIS Mirror Facet Normal Interpolation (Illustrative transition between codebook states)
  const currentNormals = [
    [0, 1, 0], [0, 1, 0], [0, 1, 0],
    [0, 1, 0], [0, 1, 0], [0, 1, 0]
  ];
  let targetNormals = [
    [0, 1, 0], [0, 1, 0], [0, 1, 0],
    [0, 1, 0], [0, 1, 0], [0, 1, 0]
  ];

  // Mouse / Pointer Drag State
  let isDragging = false;
  let dragButton = 0;
  let lastMouseX = 0, lastMouseY = 0;

  // Canvas Dimension & DPR Handling
  let W = 0, H = 0;
  function resizeCanvas() {
    const rect = canvas.getBoundingClientRect();
    const dpr = window.devicePixelRatio || 1;
    W = rect.width;
    H = rect.height;
    if (canvas.width !== Math.round(W * dpr) || canvas.height !== Math.round(H * dpr)) {
      canvas.width = Math.round(W * dpr);
      canvas.height = Math.round(H * dpr);
    }
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
  }
  window.addEventListener('resize', resizeCanvas);
  resizeCanvas();

  // 3D Vector Math Helpers
  const sub = (a, b) => [a[0] - b[0], a[1] - b[1], a[2] - b[2]];
  const add = (a, b) => [a[0] + b[0], a[1] + b[1], a[2] + b[2]];
  const mul = (a, s) => [a[0] * s, a[1] * s, a[2] * s];
  const dot = (a, b) => a[0] * b[0] + a[1] * b[1] + a[2] * b[2];
  const cross = (a, b) => [
    a[1] * b[2] - a[2] * b[1],
    a[2] * b[0] - a[0] * b[2],
    a[0] * b[1] - a[1] * b[0]
  ];
  const unit = a => {
    const l = Math.hypot(...a);
    return l > 1e-12 ? mul(a, 1 / l) : [0, 1, 0];
  };

  // Computes orthonormal tangent basis (u, v) for a finite mirror facet with normal n
  function mirrorBasis(n) {
    const n0 = [0, 1, 0];
    const axis = cross(n0, n);
    const s = Math.hypot(...axis);
    const c = dot(n0, n);
    if (s < 1e-9) {
      return [[c >= 0 ? 1 : -1, 0, 0], [0, 0, 1]];
    }
    const k = mul(axis, 1 / s);
    const rot = v => add(add(mul(v, c), mul(cross(k, v), s)), mul(k, dot(k, v) * (1 - c)));
    return [rot([1, 0, 0]), rot([0, 0, 1])];
  }

  // 3D Perspective Projection: transforms room point [x, y, z] to 2D canvas coordinates
  function project(x, y, z) {
    // Room center is (2.5, 2.5, 1.5) m
    const dx = x - 2.5;
    const dy = y - 2.5;
    const dz = z - 1.5;

    // Azimuth (yaw) rotation around vertical Z axis
    const cosYaw = Math.cos(yaw), sinYaw = Math.sin(yaw);
    const x1 = dx * cosYaw - dy * sinYaw;
    const y1 = dx * sinYaw + dy * cosYaw;
    const z1 = dz;

    // Elevation (pitch) tilt
    const cosPitch = Math.cos(pitch), sinPitch = Math.sin(pitch);
    const camX = x1;
    const camY = y1 * cosPitch - z1 * sinPitch; // camera depth
    const camZ = y1 * sinPitch + z1 * cosPitch; // screen vertical

    // Perspective projection with realistic focal length and distance
    const camDist = 11.2;
    const depth = camDist + camY;
    const focal = (Math.min(W, H) * 1.85) * zoom;
    const scale = focal / Math.max(0.6, depth);

    return {
      x: W / 2 + panX + camX * scale,
      y: H / 2 + panY - camZ * scale,
      scale: scale,
      depth: depth
    };
  }

  // Draw 3D Line
  function drawLine3D(a, b, color, width = 1, dashed = false) {
    const p1 = project(a[0], a[1], a[2]);
    const p2 = project(b[0], b[1], b[2]);
    ctx.beginPath();
    ctx.strokeStyle = color;
    ctx.lineWidth = width;
    ctx.setLineDash(dashed ? [4, 4] : []);
    ctx.moveTo(p1.x, p1.y);
    ctx.lineTo(p2.x, p2.y);
    ctx.stroke();
    ctx.setLineDash([]);
  }

  // =========================================================================
  // MAIN 3D SCENE RENDERER
  // =========================================================================
  function draw3DScene() {
    if (W === 0 || H === 0) resizeCanvas();

    // Clear background with rich dark cosmic gradient
    const bgGrad = ctx.createRadialGradient(W / 2, H / 3, 20, W / 2, H / 2, Math.max(W, H) * 0.8);
    bgGrad.addColorStop(0, '#112238');
    bgGrad.addColorStop(1, '#080f1a');
    ctx.fillStyle = bgGrad;
    ctx.fillRect(0, 0, W, H);

    // 1. Shaded Floor Base Polygon (z = 0)
    if (layers.grid) {
      const fl0 = project(0, 0, 0);
      const fl1 = project(5, 0, 0);
      const fl2 = project(5, 5, 0);
      const fl3 = project(0, 5, 0);
      ctx.beginPath();
      ctx.moveTo(fl0.x, fl0.y);
      ctx.lineTo(fl1.x, fl1.y);
      ctx.lineTo(fl2.x, fl2.y);
      ctx.lineTo(fl3.x, fl3.y);
      ctx.closePath();
      ctx.fillStyle = 'rgba(16, 35, 60, 0.45)';
      ctx.fill();

      // 1m Interval Floor Grid
      ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
      ctx.lineWidth = 1;
      for (let i = 0; i <= 5; i++) {
        drawLine3D([i, 0, 0], [i, 5, 0], 'rgba(255, 255, 255, 0.07)', 1);
        drawLine3D([0, i, 0], [5, i, 0], 'rgba(255, 255, 255, 0.07)', 1);
      }

      // Floor corner coordinate text
      if (layers.labels) {
        ctx.fillStyle = '#64748b';
        ctx.font = '10px monospace';
        const c00 = project(0, 0, 0); ctx.fillText('(0,0)m', c00.x - 22, c00.y + 12);
        const c50 = project(5, 0, 0); ctx.fillText('(5,0)m', c50.x + 6, c50.y + 12);
        const c55 = project(5, 5, 0); ctx.fillText('(5,5)m', c55.x + 6, c55.y - 6);
        const c05 = project(0, 5, 0); ctx.fillText('(0,5)m', c05.x - 32, c05.y - 6);
      }
    }

    // 2. Room 3D Cube Edges (5m x 5m x 3m)
    const cubeEdges = [
      [[0,0,0],[5,0,0]], [[5,0,0],[5,5,0]], [[5,5,0],[0,5,0]], [[0,5,0],[0,0,0]], // Floor
      [[0,0,3],[5,0,3]], [[5,0,3],[5,5,3]], [[5,5,3],[0,5,3]], [[0,5,3],[0,0,3]], // Ceiling
      [[0,0,0],[0,0,3]], [[5,0,0],[5,0,3]], [[5,5,0],[5,5,3]], [[0,5,0],[0,5,3]]  // Vertical pillars
    ];
    cubeEdges.forEach(([p1, p2]) => {
      drawLine3D(p1, p2, 'rgba(100, 130, 160, 0.4)', 1.2);
    });

    // Ceiling Plane Translucent Boundary
    const ceil0 = project(0, 0, 3);
    const ceil1 = project(5, 0, 3);
    const ceil2 = project(5, 5, 3);
    const ceil3 = project(0, 5, 3);
    ctx.beginPath();
    ctx.moveTo(ceil0.x, ceil0.y); ctx.lineTo(ceil1.x, ceil1.y); ctx.lineTo(ceil2.x, ceil2.y); ctx.lineTo(ceil3.x, ceil3.y);
    ctx.closePath();
    ctx.fillStyle = 'rgba(139, 92, 246, 0.04)';
    ctx.fill();

    // If backend data is not yet loaded, render placeholder
    if (!backendData) {
      ctx.fillStyle = '#94a3b8';
      ctx.font = '14px sans-serif';
      ctx.fillText('Waiting for Python backend geometry metadata...', 24, 40);
      return;
    }

    const g = backendData.geometry;
    const r = backendData.ris;
    const s = backendData.selected;
    const risCenter = r.panel_center;
    const bob = g.bob;
    const eve = g.eve;
    const alice = g.alice;
    const jammers = g.jammers;

    // Read authoritative weights from backend response directly, with finite number validation
    const currentWeights = (s && Array.isArray(s.beamformer))
      ? s.beamformer.map(w => Number.isFinite(w) ? w : 0.0)
      : [0, 1, 2, 3].map(i => {
          const el = document.getElementById('w' + i);
          const val = el ? parseFloat(el.value) : 0.0;
          return Number.isFinite(val) ? val : 0.0;
        });

    // 3. Drop Lines & Ground Footprints (z = 0)
    if (layers.grid) {
      // Alice drop line & soft floor spotlight
      const pAliceFloor = project(alice[0], alice[1], 0);
      drawLine3D(alice, [alice[0], alice[1], 0], 'rgba(245, 158, 11, 0.25)', 1, true);
      ctx.fillStyle = 'rgba(245, 158, 11, 0.08)';
      ctx.beginPath();
      ctx.ellipse(pAliceFloor.x, pAliceFloor.y, 22 * pAliceFloor.scale / 70, 11 * pAliceFloor.scale / 70, 0, 0, Math.PI * 2);
      ctx.fill();

      // Bob drop line & ground ring
      const pBobFloor = project(bob[0], bob[1], 0);
      drawLine3D(bob, [bob[0], bob[1], 0], 'rgba(59, 130, 246, 0.35)', 1, true);
      ctx.fillStyle = 'rgba(59, 130, 246, 0.15)';
      ctx.beginPath();
      ctx.ellipse(pBobFloor.x, pBobFloor.y, 16 * pBobFloor.scale / 70, 8 * pBobFloor.scale / 70, 0, 0, Math.PI * 2);
      ctx.fill();

      // Eve drop line & ground ring
      const pEveFloor = project(eve[0], eve[1], 0);
      drawLine3D(eve, [eve[0], eve[1], 0], 'rgba(239, 68, 68, 0.35)', 1, true);
      ctx.fillStyle = 'rgba(239, 68, 68, 0.15)';
      ctx.beginPath();
      ctx.ellipse(pEveFloor.x, pEveFloor.y, 16 * pEveFloor.scale / 70, 8 * pEveFloor.scale / 70, 0, 0, Math.PI * 2);
      ctx.fill();

      // Jammers drop lines
      jammers.forEach(j => {
        drawLine3D(j, [j[0], j[1], 0], 'rgba(168, 85, 247, 0.18)', 1, true);
      });
    }

    // 4. Bob-to-Eve 3D Separation Line & Distance Badge
    if (layers.labels) {
      drawLine3D(bob, eve, 'rgba(255, 255, 255, 0.35)', 1.2, true);
      const pB = project(bob[0], bob[1], bob[2]);
      const pE = project(eve[0], eve[1], eve[2]);
      const midX = (pB.x + pE.x) / 2;
      const midY = (pB.y + pE.y) / 2;
      const distBE = Math.hypot(bob[0] - eve[0], bob[1] - eve[1], bob[2] - eve[2]);
      ctx.fillStyle = distBE < 0.4 ? '#ef4444' : '#f1f5f9';
      ctx.font = 'bold 11px monospace';
      ctx.fillText(`${distBE.toFixed(2)}m`, midX + 6, midY - 6);
    }

    // 5. South Wall Optical RIS Backplane Mount Plate (y = 0.25m)
    const bw = 1.0, bh = 0.7; // Backplate frame width & height
    const b0 = project(risCenter[0] - bw / 2, risCenter[1], risCenter[2] - bh / 2);
    const b1 = project(risCenter[0] + bw / 2, risCenter[1], risCenter[2] - bh / 2);
    const b2 = project(risCenter[0] + bw / 2, risCenter[1], risCenter[2] + bh / 2);
    const b3 = project(risCenter[0] - bw / 2, risCenter[1], risCenter[2] + bh / 2);
    ctx.beginPath();
    ctx.moveTo(b0.x, b0.y); ctx.lineTo(b1.x, b1.y); ctx.lineTo(b2.x, b2.y); ctx.lineTo(b3.x, b3.y);
    ctx.closePath();
    ctx.fillStyle = 'rgba(15, 23, 42, 0.92)';
    ctx.fill();
    ctx.strokeStyle = 'rgba(56, 189, 248, 0.4)';
    ctx.lineWidth = 1.5;
    ctx.stroke();

    // 6. Six Finite Specular Mirror Tiles (actual tile side derived from backend metadata)
    const actualTileSide = Number.isFinite(r.tile_side_m) ? r.tile_side_m : 0.1591;
    const tileHalf = actualTileSide / 2;
    const tileCenters = r.tile_centers;
    const tileObjects = tileCenters.map((tc, idx) => {
      const curN = currentNormals[idx] || [0, 1, 0];
      const pC = project(tc[0], tc[1], tc[2]);
      return { idx, center: tc, normal: curN, pCenter: pC, depth: pC.depth };
    });
    // Sort tiles back-to-front for proper depth occlusion
    tileObjects.sort((a, b) => b.depth - a.depth);

    tileObjects.forEach(t => {
      const [u, v] = mirrorBasis(t.normal);
      // 4 corners of square mirror facet
      const c1 = add(t.center, add(mul(u, -tileHalf), mul(v, -tileHalf)));
      const c2 = add(t.center, add(mul(u, tileHalf), mul(v, -tileHalf)));
      const c3 = add(t.center, add(mul(u, tileHalf), mul(v, tileHalf)));
      const c4 = add(t.center, add(mul(u, -tileHalf), mul(v, tileHalf)));

      const p1 = project(c1[0], c1[1], c1[2]);
      const p2 = project(c2[0], c2[1], c2[2]);
      const p3 = project(c3[0], c3[1], c3[2]);
      const p4 = project(c4[0], c4[1], c4[2]);

      ctx.beginPath();
      ctx.moveTo(p1.x, p1.y); ctx.lineTo(p2.x, p2.y); ctx.lineTo(p3.x, p3.y); ctx.lineTo(p4.x, p4.y);
      ctx.closePath();

      if (s.ris_index === 0) {
        // q = 0: Stowed / Inactive neutral slate mirror
        ctx.fillStyle = 'rgba(71, 85, 105, 0.85)';
        ctx.fill();
        ctx.strokeStyle = 'rgba(148, 163, 184, 0.7)';
        ctx.lineWidth = 1.2;
        ctx.stroke();
      } else {
        // q > 0: Active aligned specular mirror with cyan reflection & specular gleam
        ctx.fillStyle = 'rgba(6, 182, 212, 0.85)';
        ctx.fill();
        ctx.strokeStyle = '#e0f2fe';
        ctx.lineWidth = 1.5;
        ctx.stroke();

        // Diagonal specular gleam line
        ctx.beginPath();
        ctx.strokeStyle = 'rgba(255, 255, 255, 0.75)';
        ctx.lineWidth = 1.0;
        ctx.moveTo(p1.x, p1.y); ctx.lineTo(p3.x, p3.y);
        ctx.stroke();
      }

      // 3D Mirror Normal Vector Arrow
      if (layers.normals) {
        const normTip = add(t.center, mul(t.normal, 0.28));
        const pTip = project(normTip[0], normTip[1], normTip[2]);
        ctx.beginPath();
        ctx.strokeStyle = s.ris_index === 0 ? 'rgba(203, 213, 225, 0.6)' : '#38bdf8';
        ctx.lineWidth = 1.6;
        ctx.moveTo(t.pCenter.x, t.pCenter.y);
        ctx.lineTo(pTip.x, pTip.y);
        ctx.stroke();

        // Arrowhead dot at normal tip
        ctx.fillStyle = s.ris_index === 0 ? '#94a3b8' : '#e0f2fe';
        ctx.beginPath();
        ctx.arc(pTip.x, pTip.y, 2.5, 0, Math.PI * 2);
        ctx.fill();
      }

      // Tile Label
      if (layers.labels) {
        ctx.fillStyle = '#bae6fd';
        ctx.font = '9px monospace';
        ctx.fillText(`T${t.idx + 1}`, t.pCenter.x - 6, t.pCenter.y + 3);
      }
    });

    // 7. Optical Signal Beams (Direct, Jamming, Reflected)
    const pAlice = project(alice[0], alice[1], alice[2]);
    const pBob = project(bob[0], bob[1], bob[2]);
    const pEve = project(eve[0], eve[1], eve[2]);
    const pRisCenter = project(risCenter[0], risCenter[1], risCenter[2]);

    // (A) Direct Alice -> Bob (Main Confidential Beam)
    if (layers.direct && s.direct_gains.h_AB > 0) {
      drawLine3D(alice, bob, 'rgba(16, 185, 129, 0.95)', 3.2);
    }

    // (B) Direct Alice -> Eve (Eavesdropping Leakage Beam)
    if (layers.direct && s.direct_gains.h_AE > 0) {
      drawLine3D(alice, eve, 'rgba(245, 158, 11, 0.7)', 1.8, true);
    }

    // (C) 4 Friendly Jammers to Eve & Null-Space Trace to Bob
    if (layers.jammers) {
      jammers.forEach((j, i) => {
        const wMag = Math.abs(currentWeights[i]);
        if (s.direct_gains.h_JE[i] > 0) {
          if (wMag > 1e-6) {
            // Emitted modulated jamming: thick solid purple wavefront
            drawLine3D(j, eve, `rgba(192, 132, 252, ${0.4 + 0.6 * wMag})`, 1.5 + 3.0 * wMag);
          } else {
            // w_i = 0: Channel exists geometrically but is unmodulated (distinguished honestly)
            drawLine3D(j, eve, 'rgba(168, 85, 247, 0.20)', 1.0, true);
          }
        }
        // Null-space trace to Bob (showing zero/minimal leakage)
        if (s.direct_gains.h_JB[i] > 0) {
          drawLine3D(j, bob, 'rgba(56, 189, 248, 0.22)', 1.0, true);
        }
      });
    }

    // (D) Reflected Alice -> RIS Panel -> Bob (Reflected Confidential Link)
    if (layers.reflected && s.reflected_gains.h_AB > 1e-12) {
      drawLine3D(alice, risCenter, 'rgba(6, 182, 212, 0.85)', 2.2, true);
      drawLine3D(risCenter, bob, 'rgba(6, 182, 212, 0.95)', 3.0);
    }

    // (E) Reflected Jammers -> RIS Panel -> Eve (Reflected Jamming Links)
    if (layers.reflected) {
      jammers.forEach((j, i) => {
        if (s.reflected_gains.h_JE[i] > 1e-12 && Math.abs(currentWeights[i]) > 1e-6) {
          drawLine3D(j, risCenter, 'rgba(232, 121, 249, 0.75)', 1.5, true);
          drawLine3D(risCenter, eve, 'rgba(232, 121, 249, 0.85)', 2.0);
        }
      });
    }

    // 8. Animated Flowing Photons (Illustrative Activity Flow)
    if (isPlaying) {
      const numPhotons = 12;
      for (let p = 0; p < numPhotons; p++) {
        const prog = (animTime * 0.7 + p * (1.0 / numPhotons)) % 1.0;

        // Direct Data Photon (Alice -> Bob)
        if (layers.direct && s.direct_gains.h_AB > 0) {
          const bx = pAlice.x + (pBob.x - pAlice.x) * prog;
          const by = pAlice.y + (pBob.y - pAlice.y) * prog;
          ctx.fillStyle = '#34d399';
          ctx.beginPath(); ctx.arc(bx, by, 3.8, 0, Math.PI * 2); ctx.fill();
        }

        // Direct Leakage Photon (Alice -> Eve)
        if (layers.direct && s.direct_gains.h_AE > 0) {
          const ex = pAlice.x + (pEve.x - pAlice.x) * prog;
          const ey = pAlice.y + (pEve.y - pAlice.y) * prog;
          ctx.fillStyle = '#fbbf24';
          ctx.beginPath(); ctx.arc(ex, ey, 2.8, 0, Math.PI * 2); ctx.fill();
        }

        // Jamming Pulse from Active Jammer -> Eve (strictly gated by w_i > 0)
        if (layers.jammers) {
          const jIdx = p % 4;
          if (Math.abs(currentWeights[jIdx]) > 1e-6 && s.direct_gains.h_JE[jIdx] > 0) {
            const pj = project(jammers[jIdx][0], jammers[jIdx][1], jammers[jIdx][2]);
            const jx = pj.x + (pEve.x - pj.x) * prog;
            const jy = pj.y + (pEve.y - pj.y) * prog;
            ctx.fillStyle = '#c084fc';
            ctx.beginPath(); ctx.arc(jx, jy, 3.2, 0, Math.PI * 2); ctx.fill();
          }
        }

        // Reflected Photon (Alice -> RIS -> Bob)
        if (layers.reflected && s.reflected_gains.h_AB > 1e-12) {
          let rx, ry;
          if (prog < 0.5) {
            const seg = prog * 2.0;
            rx = pAlice.x + (pRisCenter.x - pAlice.x) * seg;
            ry = pAlice.y + (pRisCenter.y - pAlice.y) * seg;
          } else {
            const seg = (prog - 0.5) * 2.0;
            rx = pRisCenter.x + (pBob.x - pRisCenter.x) * seg;
            ry = pRisCenter.y + (pBob.y - pRisCenter.y) * seg;
          }
          ctx.fillStyle = '#38bdf8';
          ctx.beginPath(); ctx.arc(rx, ry, 3.4, 0, Math.PI * 2); ctx.fill();
        }
      }
    }

    // 9. Transceiver Device Nodes
    // Alice (Tx Emitter on Ceiling)
    ctx.fillStyle = '#f59e0b';
    ctx.beginPath(); ctx.arc(pAlice.x, pAlice.y, 11, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 2.5; ctx.stroke();
    ctx.fillStyle = '#ffffff'; ctx.beginPath(); ctx.arc(pAlice.x, pAlice.y, 4, 0, Math.PI * 2); ctx.fill();
    if (layers.labels) {
      ctx.fillStyle = '#fef08a';
      ctx.font = 'bold 12px sans-serif';
      ctx.fillText('Alice Tx (2.5, 2.5, 3.0)m', pAlice.x + 14, pAlice.y + 4);
    }

    // 4 Friendly Jammers
    jammers.forEach((j, idx) => {
      const pj = project(j[0], j[1], j[2]);
      const w = currentWeights[idx];
      const isMod = Math.abs(w) > 1e-6;
      ctx.fillStyle = isMod ? '#9333ea' : '#475569';
      ctx.beginPath(); ctx.arc(pj.x, pj.y, 8, 0, Math.PI * 2); ctx.fill();
      ctx.strokeStyle = '#fff'; ctx.lineWidth = 2.0; ctx.stroke();

      if (layers.labels) {
        ctx.fillStyle = isMod ? '#e9d5ff' : '#94a3b8';
        ctx.font = 'bold 10.5px sans-serif';
        const wStr = isMod ? (w >= 0 ? '+' : '') + w.toFixed(2) : '0.0 (idle)';
        ctx.fillText(`J${idx + 1} (${wStr})`, pj.x + 11, pj.y + 3);
      }
    });

    // Bob Rx (Legitimate Receiver)
    ctx.fillStyle = '#3b82f6';
    ctx.beginPath(); ctx.arc(pBob.x, pBob.y, 11, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 2.5; ctx.stroke();

    // Bob Pulsating Secrecy / Null-Space Safety Ring
    const bobPulse = 18 + 4 * Math.sin(animTime * 4.0);
    ctx.strokeStyle = 'rgba(16, 185, 129, 0.75)';
    ctx.lineWidth = 2.0;
    ctx.beginPath(); ctx.arc(pBob.x, pBob.y, bobPulse, 0, Math.PI * 2); ctx.stroke();
    if (layers.labels) {
      ctx.fillStyle = '#93c5fd';
      ctx.font = 'bold 12px sans-serif';
      ctx.fillText(`Bob Rx (${bob[0].toFixed(2)}, ${bob[1].toFixed(2)}, ${bob[2].toFixed(2)})m`, pBob.x + 14, pBob.y + 4);
    }

    // Eve Rx (Eavesdropper / Wiretapper)
    ctx.fillStyle = '#ef4444';
    ctx.beginPath(); ctx.arc(pEve.x, pEve.y, 11, 0, Math.PI * 2); ctx.fill();
    ctx.strokeStyle = '#fff'; ctx.lineWidth = 2.5; ctx.stroke();

    // Eve Warning Ring
    const evePulse = 17 + 3 * Math.cos(animTime * 5.0);
    ctx.strokeStyle = 'rgba(239, 68, 68, 0.75)';
    ctx.lineWidth = 1.8;
    ctx.beginPath(); ctx.arc(pEve.x, pEve.y, evePulse, 0, Math.PI * 2); ctx.stroke();
    if (layers.labels) {
      ctx.fillStyle = '#fca5a5';
      ctx.font = 'bold 12px sans-serif';
      ctx.fillText(`Eve Rx (${eve[0].toFixed(2)}, ${eve[1].toFixed(2)}, ${eve[2].toFixed(2)})m`, pEve.x + 14, pEve.y + 4);
    }

    // 10. Update HUD Text Displays
    const degYaw = (yaw * 180 / Math.PI).toFixed(1);
    const degPitch = (pitch * 180 / Math.PI).toFixed(1);
    const elCam = document.getElementById('hudCamInfo');
    if (elCam) elCam.textContent = `Camera: Yaw ${degYaw}° · Pitch ${degPitch}° · Zoom ${zoom.toFixed(1)}x`;

    const sideStr = Number.isFinite(r.tile_side_m) ? r.tile_side_m.toFixed(3) : '0.159';
    const elRoom = document.getElementById('hudRoomInfo');
    if (elRoom) {
      elRoom.innerHTML = `<strong>Room:</strong> 5.0m × 5.0m × 3.0m · ${r.num_tiles || 6} Specular Mirror Tiles (${sideStr}m × ${sideStr}m)`;
    }

    const elRis = document.getElementById('hudRisInfo');
    if (elRis && backendData.configuration_names) {
      const cfgName = backendData.configuration_names[s.ris_index] || ('Config ' + s.ris_index);
      elRis.textContent = `RIS State: ${s.ris_index} (${cfgName}) · ${r.num_tiles} Specular Tiles (${sideStr}m × ${sideStr}m)`;
    }

    const elDist = document.getElementById('hudDistInfo');
    if (elDist) {
      const distBE = Math.hypot(bob[0] - eve[0], bob[1] - eve[1], bob[2] - eve[2]);
      elDist.textContent = `Bob: (${bob[0].toFixed(2)}, ${bob[1].toFixed(2)}, ${bob[2].toFixed(2)})m · Eve: (${eve[0].toFixed(2)}, ${eve[1].toFixed(2)}, ${eve[2].toFixed(2)})m · d_BE = ${distBE.toFixed(2)}m`;
    }
  }

  // =========================================================================
  // ANIMATION LOOP WITH SMOOTH NORMAL INTERPOLATION
  // =========================================================================
  function animate(now) {
    const dt = Math.min(0.1, (now - lastTimestamp) * 0.001);
    lastTimestamp = now;

    if (isPlaying) {
      animTime += dt * simSpeed;
    }

    // Smoothly interpolate currentNormals toward targetNormals
    for (let i = 0; i < currentNormals.length; i++) {
      const cur = currentNormals[i];
      const tgt = targetNormals[i] || [0, 1, 0];
      const diff = Math.hypot(tgt[0] - cur[0], tgt[1] - cur[1], tgt[2] - cur[2]);
      if (diff > 0.001) {
        cur[0] += (tgt[0] - cur[0]) * 0.16;
        cur[1] += (tgt[1] - cur[1]) * 0.16;
        cur[2] += (tgt[2] - cur[2]) * 0.16;
        const l = Math.hypot(cur[0], cur[1], cur[2]) || 1;
        cur[0] /= l; cur[1] /= l; cur[2] /= l;
      } else {
        cur[0] = tgt[0]; cur[1] = tgt[1]; cur[2] = tgt[2];
      }
    }

    draw3DScene();
    requestAnimationFrame(animate);
  }
  requestAnimationFrame(animate);

  // =========================================================================
  // INTERACTIVE POINTER / MOUSE CONTROLS
  // =========================================================================
  canvas.addEventListener('pointerdown', e => {
    isDragging = true;
    dragButton = e.button;
    lastMouseX = e.clientX;
    lastMouseY = e.clientY;
    canvas.setPointerCapture(e.pointerId);
    canvas.style.cursor = 'grabbing';
  });

  canvas.addEventListener('pointermove', e => {
    if (!isDragging) return;
    const dx = e.clientX - lastMouseX;
    const dy = e.clientY - lastMouseY;
    lastMouseX = e.clientX;
    lastMouseY = e.clientY;

    if (dragButton === 2 || e.shiftKey) {
      // Pan camera in screen space
      panX += dx;
      panY += dy;
    } else {
      // Orbit around room center
      yaw += dx * 0.007;
      pitch = Math.max(-0.25, Math.min(1.57, pitch + dy * 0.007));
      activeCameraMode = 'custom';
      updateCameraButtons();
    }
  });

  const stopDrag = () => {
    isDragging = false;
    canvas.style.cursor = 'grab';
  };
  canvas.addEventListener('pointerup', stopDrag);
  canvas.addEventListener('pointercancel', stopDrag);

  // Prevent right-click context menu so right-click pan works cleanly
  canvas.addEventListener('contextmenu', e => e.preventDefault());

  // Mouse wheel to zoom
  canvas.addEventListener('wheel', e => {
    e.preventDefault();
    const factor = Math.exp(-e.deltaY * 0.0012);
    zoom = Math.max(0.45, Math.min(3.8, zoom * factor));
  }, { passive: false });

  // Double click resets camera
  canvas.addEventListener('dblclick', () => {
    window.resetCamera();
  });

  // =========================================================================
  // EXPOSED WINDOW CONTROLS & HUD HANDLERS
  // =========================================================================
  function updateCameraButtons() {
    ['Orbit', 'Top', 'Side', 'Front'].forEach(m => {
      const btn = document.getElementById('btnCam' + m);
      if (btn) btn.classList.toggle('active', activeCameraMode === m.toLowerCase());
    });
  }

  window.setCameraMode = mode => {
    activeCameraMode = mode;
    panX = 0; panY = 0;
    if (mode === 'orbit') {
      yaw = -0.65; pitch = 0.55; zoom = 1.0;
    } else if (mode === 'top') {
      yaw = 0.0; pitch = 1.57; zoom = 1.0;
    } else if (mode === 'side') {
      yaw = 0.0; pitch = 0.0; zoom = 1.0;
    } else if (mode === 'front') {
      yaw = Math.PI; pitch = 0.22; zoom = 1.25;
    }
    updateCameraButtons();
  };

  window.resetCamera = () => {
    window.setCameraMode('orbit');
  };

  window.zoomCamera = factor => {
    zoom = Math.max(0.45, Math.min(3.8, zoom * factor));
  };

  window.togglePulseFlow = () => {
    isPlaying = !isPlaying;
    const btn = document.getElementById('btnPulseFlow');
    if (btn) btn.textContent = isPlaying ? '⏸ Pause Flow' : '▶ Play Flow';
  };

  window.setFlowSpeed = val => {
    simSpeed = parseFloat(val) || 1.0;
  };

  window.toggleLayer = (layerName, checked) => {
    if (layerName in layers) {
      layers[layerName] = checked;
    }
  };

  window.switchStageView = view => {
    const c3D = document.getElementById('container3D');
    const c2D = document.getElementById('container2D');
    const b3D = document.getElementById('tabStage3D');
    const b2D = document.getElementById('tabStage2D');

    if (view === '3d') {
      if (c3D) c3D.style.display = 'block';
      if (c2D) c2D.style.display = 'none';
      if (b3D) b3D.classList.add('active');
      if (b2D) b2D.classList.remove('active');
      resizeCanvas();
    } else {
      if (c3D) c3D.style.display = 'none';
      if (c2D) c2D.style.display = 'block';
      if (b3D) b3D.classList.remove('active');
      if (b2D) b2D.classList.add('active');
    }
  };

  // Backwards compatibility for existing test suite
  window.room3DView = view => {
    window.setCameraMode(view);
  };

  // =========================================================================
  // BACKEND METRICS EVENT LISTENER
  // =========================================================================
  window.addEventListener('ris-3d-update', e => {
    backendData = e.detail;
    if (!backendData) return;

    // Update targetNormals from backend metadata
    const r = backendData.ris;
    const s = backendData.selected;
    const cfgName = backendData.configuration_names[s.ris_index];
    if (r && r.configurations && r.configurations[cfgName]) {
      targetNormals = r.configurations[cfgName].tile_normals.map(n => [...n]);
    }
  });

})();

// =========================================================================
// RECORDED-ACTION REPLAY TIMELINE CONTROLLER FOR DRL SMOKE RUN
// =========================================================================
let replayRun = null;
let replaySlot = 0;
let replayTimer = null;
let replayScenario = null;
let isReplayActive = false;

function initReplay(res) {
  const runs = (res && res.runs) || [];
  if (runs.length === 0) return;

  // Snapshot the run scenario for consistency lock
  replayRun = runs.find(r => r.scheme.toLowerCase().includes('joint')) || runs[0];
  if (!replayRun || !replayRun.actions || replayRun.actions.length === 0) return;

  const scen = replayRun.scenario || (res && res.scenarios && res.scenarios[0]) || {
    bob: [parseFloat(document.getElementById('bx').value), parseFloat(document.getElementById('by').value), parseFloat(document.getElementById('bz').value)],
    eve: [parseFloat(document.getElementById('ex').value), parseFloat(document.getElementById('ey').value), parseFloat(document.getElementById('ez').value)]
  };
  replayScenario = {
    bob: [...scen.bob],
    eve: [...scen.eve],
    energy_model: replayRun.energy_model || document.getElementById('energyModel').value
  };

  const totalSlots = replayRun.actions.length;
  const slider = document.getElementById('replaySlider');
  if (slider) {
    slider.min = 1;
    slider.max = totalSlots;
    slider.value = 1;
  }
  replaySlot = 0;
  isReplayActive = true;
  const replayBox = document.getElementById('smokeReplayBox');
  if (replayBox) replayBox.style.display = 'block';
  updateReplaySlot(0);
}

function updateReplaySlot(idx) {
  if (!replayRun || !replayRun.actions) return;
  const totalSlots = replayRun.actions.length;
  replaySlot = Math.max(0, Math.min(totalSlots - 1, idx));

  const slider = document.getElementById('replaySlider');
  if (slider) slider.value = replaySlot + 1;

  const badge = document.getElementById('replaySlotBadge');
  if (badge) badge.textContent = `Slot k = ${replaySlot + 1} / ${totalSlots}`;

  const act = replayRun.actions[replaySlot];
  const obs = (replayRun.observations && replayRun.observations[replaySlot]) || null;
  const hist = replayRun.history;
  const rate = (hist && hist.secrecy_rate && hist.secrecy_rate[replaySlot] !== undefined)
    ? hist.secrecy_rate[replaySlot]
    : (obs ? obs.secrecy_rate : 0);
  const ber = (hist && hist.ber && hist.ber[replaySlot] !== undefined)
    ? hist.ber[replaySlot]
    : (obs ? obs.ber : 0);

  // Decode action vector
  const w = act.slice(0, 4);
  let risIdx = 0;
  if (act.length >= 5) {
    const rawRis = act[4];
    risIdx = Math.max(0, Math.min(4, Math.round((rawRis + 1.0) / 2.0 * 4.0)));
  } else if (obs && obs.ris_index !== undefined) {
    risIdx = obs.ris_index;
  }

  const readout = document.getElementById('replayActionReadout');
  if (readout) {
    readout.innerHTML = `
      <strong>Scheme:</strong> ${replayRun.scheme} |
      <strong>Action:</strong> w = [${w.map(x => (x >= 0 ? '+' : '') + x.toFixed(2)).join(', ')}],
      <strong>RIS Config:</strong> ${risIdx} |
      <strong>Secrecy:</strong> ${rate.toFixed(4)} bps/Hz |
      <strong>Bob BER:</strong> ${ber === 0 ? '0.0' : ber.toExponential(2)}
    `;
  }

  // Sync to live controls & 3D scene if checked
  const chk = document.getElementById('chkSync3D');
  if (chk && chk.checked) {
    window._isReplayingSlot = true;
    try {
      // Restore and lock scenario geometry so replay does not blend mismatched settings
      if (replayScenario) {
        document.getElementById('bx').value = replayScenario.bob[0].toFixed(2);
        document.getElementById('by').value = replayScenario.bob[1].toFixed(2);
        document.getElementById('bz').value = replayScenario.bob[2].toFixed(2);
        document.getElementById('ex').value = replayScenario.eve[0].toFixed(2);
        document.getElementById('ey').value = replayScenario.eve[1].toFixed(2);
        document.getElementById('ez').value = replayScenario.eve[2].toFixed(2);
        document.getElementById('energyModel').value = replayScenario.energy_model;
      }

      document.getElementById('w0').value = w[0].toFixed(2);
      document.getElementById('w1').value = w[1].toFixed(2);
      document.getElementById('w2').value = w[2].toFixed(2);
      document.getElementById('w3').value = w[3].toFixed(2);
      currentRisIndex = risIdx;
      for (let i = 0; i <= 4; i++) {
        const btn = document.getElementById('cfg' + i);
        if (btn) btn.className = (i === risIdx ? 'active primary' : '');
      }

      // Direct observation replay: updates 3D scene with the genuine recorded data
      if (obs) {
        const replayedData = {
          selected: obs,
          baseline: obs,
          ris: replayRun.ris || (backendData ? backendData.ris : null),
          configuration_names: ['0: Off (Stowed)', '1: Aim Alice → Bob', '2: Jammers → Eve', '3: Split Bob/Eve', '4: Neutral [0,1,0]'],
          geometry: {
            alice: [2.5, 2.5, 3.0],
            jammers: [[1.5, 1.5, 3.0], [1.5, 3.5, 3.0], [3.5, 1.5, 3.0], [3.5, 3.5, 3.0]],
            bob: replayScenario ? replayScenario.bob : [1.8, 1.6, 0.85],
            eve: replayScenario ? replayScenario.eve : [3.2, 3.4, 0.85]
          }
        };
        window.dispatchEvent(new CustomEvent('ris-3d-update', { detail: replayedData }));
        if (typeof renderMetricsTable === 'function') renderMetricsTable(replayedData);
      } else {
        triggerUpdate();
      }
    } finally {
      window._isReplayingSlot = false;
    }
  }
}

function onReplaySlider(val) {
  updateReplaySlot(parseInt(val, 10) - 1);
}

function stepReplay(delta) {
  if (replayTimer) {
    clearInterval(replayTimer);
    replayTimer = null;
    const btn = document.getElementById('btnReplayPlay');
    if (btn) btn.textContent = '▶ Play Replay';
  }
  updateReplaySlot(replaySlot + delta);
}

function toggleReplayPlay() {
  const btn = document.getElementById('btnReplayPlay');
  if (replayTimer) {
    clearInterval(replayTimer);
    replayTimer = null;
    if (btn) btn.textContent = '▶ Play Replay';
  } else {
    if (!replayRun || !replayRun.actions) return;
    if (btn) btn.textContent = '⏸ Pause Replay';
    replayTimer = setInterval(() => {
      const totalSlots = replayRun.actions.length;
      if (replaySlot >= totalSlots - 1) {
        clearInterval(replayTimer);
        replayTimer = null;
        if (btn) btn.textContent = '▶ Play Replay';
      } else {
        updateReplaySlot(replaySlot + 1);
      }
    }, 200);
  }
}

// Invalidate replay when user manually changes geometry, presets or weights
function invalidateReplay(reason) {
  if (isReplayActive) {
    isReplayActive = false;
    if (replayTimer) { clearInterval(replayTimer); replayTimer = null; }
    const btn = document.getElementById('btnReplayPlay');
    if (btn) btn.textContent = '▶ Play Replay';
    const badge = document.getElementById('replaySlotBadge');
    if (badge) badge.textContent = `Paused (${reason || 'Manual Mode'})`;
  }
}

const _origSetPreset = typeof setPreset === 'function' ? setPreset : null;
if (_origSetPreset) {
  setPreset = function(presetName) {
    invalidateReplay('Preset ' + presetName);
    return _origSetPreset(presetName);
  };
}

const _origSetWeights = typeof setWeights === 'function' ? setWeights : null;
if (_origSetWeights) {
  setWeights = function(w) {
    invalidateReplay('Manual Weights');
    return _origSetWeights(w);
  };
}

const _origTriggerUpdate = typeof triggerUpdate === 'function' ? triggerUpdate : null;
if (_origTriggerUpdate) {
  triggerUpdate = function() {
    if (!window._isReplayingSlot) {
      invalidateReplay('Manual Edit');
    }
    return _origTriggerUpdate.apply(this, arguments);
  };
}

// Hook initReplay into displaySmokeResults
const _origDisplaySmokeResults = typeof displaySmokeResults === 'function' ? displaySmokeResults : null;
displaySmokeResults = function(res) {
  if (_origDisplaySmokeResults) _origDisplaySmokeResults(res);
  initReplay(res);
};
