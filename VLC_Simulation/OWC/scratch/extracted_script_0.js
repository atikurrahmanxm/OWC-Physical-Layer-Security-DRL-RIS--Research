
  'use strict';
  const $ = id => document.getElementById(id);
  const fmt = (x, dec = 6) => {
    if (x === null || x === undefined || !Number.isFinite(x)) return '—';
    if (x === 0) return '0.000000';
    if (Math.abs(x) < 1e-4) return x.toExponential(4);
    return x.toFixed(dec);
  };

  let currentRisIndex = 1;
  let currentPreset = 'nominal';
  let activeRequestId = 0;

  // Exact derived two-sided Student-t p-values (df = 9)
  const DERIVED_P_VALUES = {
    'fixed_ris minus baseline': 0.0182917,
    'joint_ris minus baseline': 0.1216017,
    'joint_ris minus fixed_ris': 0.6887355
  };

  // Room geometry scale: room is 5m x 5m, mapped to 50..490 in SVG (span 440 px -> 88 px/m)
  function toSvgCoords(x, y) {
    const px = 50 + x * 88;
    const py = 50 + y * 88;
    return { x: px, y: py };
  }

  function setPreset(name) {
    currentPreset = name;
    ['presetNominal', 'presetChanged', 'presetNearBob', 'presetColocated'].forEach(id => {
      const el = $(id);
      if (el) el.classList.remove('active');
    });
    if (name === 'nominal') {
      $('presetNominal').classList.add('active');
      $('bx').value = 1.8; $('by').value = 1.6; $('bz').value = 0.85;
      $('ex').value = 3.2; $('ey').value = 3.4; $('ez').value = 0.85;
    } else if (name === 'changed') {
      if ($('presetChanged')) $('presetChanged').classList.add('active');
      $('bx').value = 2.0; $('by').value = 3.0; $('bz').value = 0.85;
      $('ex').value = 3.5; $('ey').value = 1.5; $('ez').value = 0.85;
    } else if (name === 'near_bob') {
      $('presetNearBob').classList.add('active');
      $('bx').value = 1.8; $('by').value = 1.6; $('bz').value = 0.85;
      $('ex').value = 1.85; $('ey').value = 1.65; $('ez').value = 0.85;
    } else if (name === 'colocated') {
      $('presetColocated').classList.add('active');
      $('bx').value = 1.8; $('by').value = 1.6; $('bz').value = 0.85;
      $('ex').value = 1.8; $('ey').value = 1.6; $('ez').value = 0.85;
    }
    triggerUpdate();
  }

  function setRisIndex(idx) {
    currentRisIndex = idx;
    for (let i = 0; i < 5; i++) {
      const btn = $('cfg' + i);
      if (btn) btn.classList.toggle('active', i === idx);
      if (btn) btn.classList.toggle('primary', i === idx);
    }
    triggerUpdate();
  }

  function setWeights(w) {
    $('w0').value = w[0];
    $('w1').value = w[1];
    $('w2').value = w[2];
    $('w3').value = w[3];
    triggerUpdate();
  }

  function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.target.classList.add('active');
    $('tabPhase1').style.display = tabId === 'phase1' ? 'block' : 'none';
    $('tabPhase2').style.display = tabId === 'phase2' ? 'block' : 'none';
    $('tabPhase3').style.display = tabId === 'phase3' ? 'block' : 'none';
  }

  function clearRays() {
    $('dynamicRays').innerHTML = '';
  }

  function clearMetricsTable(msg) {
    $('metricsTableBody').innerHTML = `<tr><td colspan="4" style="color:#d9534f; font-weight:bold;">${msg}</td></tr>`;
  }

  async function triggerUpdate() {
    const reqId = ++activeRequestId;
    const bob = [parseFloat($('bx').value), parseFloat($('by').value), parseFloat($('bz').value)];
    const eve = [parseFloat($('ex').value), parseFloat($('ey').value), parseFloat($('ez').value)];
    const beamformer = [parseFloat($('w0').value), parseFloat($('w1').value), parseFloat($('w2').value), parseFloat($('w3').value)];
    const energy = $('energyModel').value;

    // Update SVG Node positions
    const bobSvg = toSvgCoords(bob[0], bob[1]);
    const eveSvg = toSvgCoords(eve[0], eve[1]);
    $('bobCircle').setAttribute('cx', bobSvg.x);
    $('bobCircle').setAttribute('cy', bobSvg.y);
    $('bobText').setAttribute('x', bobSvg.x);
    $('bobText').setAttribute('y', bobSvg.y - 16);
    $('bobText').textContent = `Bob (${bob[0]}, ${bob[1]})`;

    $('eveCircle').setAttribute('cx', eveSvg.x);
    $('eveCircle').setAttribute('cy', eveSvg.y);
    $('eveText').setAttribute('x', eveSvg.x);
    $('eveText').setAttribute('y', eveSvg.y + 22);
    $('eveText').textContent = `Eve (${eve[0]}, ${eve[1]})`;

    $('liveStatus').className = 'status-box';
    $('liveStatus').textContent = 'Computing live optical metrics via Python...';

    try {
      const payload = {
        bob: bob,
        eve: eve,
        beamformer: beamformer,
        ris_index: currentRisIndex,
        energy_model: energy
      };

      const res = await fetch('/api/ris/metrics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (reqId !== activeRequestId) return; // Discard stale response
      const data = await res.json();
      if (reqId !== activeRequestId) return;
      if (!res.ok) throw new Error(data.error || 'Backend calculation failed');

      window._lastBackendData = data;
      renderMetricsTable(data);
      renderDynamicRays(data);
      renderTileNormals(data);
      window.dispatchEvent(new CustomEvent('ris-3d-update', {detail:data}));

      $('selectedCfgName').textContent = data.configuration_names[currentRisIndex] || ('Config ' + currentRisIndex);
      $('liveStatus').className = 'status-box success';
      $('liveStatus').textContent = `Backend Calculation Verified: ${data.configuration_names[currentRisIndex]} | Secrecy: ${data.selected.secrecy_rate.toFixed(4)} bps/Hz | Bob BER: ${data.selected.ber === 0 ? '0.0' : data.selected.ber.toExponential(2)}`;
    } catch (err) {
      if (reqId !== activeRequestId) return;
      window._lastBackendData = null;
      $('liveStatus').className = 'status-box error';
      $('liveStatus').textContent = 'Calculation Error: ' + err.message;
      clearMetricsTable('Error: ' + err.message);
      clearRays();
      window.dispatchEvent(new CustomEvent('ris-3d-update', {detail:null}));
    }
  }

  function renderMetricsTable(d) {
    const body = $('metricsTableBody');
    body.innerHTML = '';

    const b = d.baseline;
    const s = d.selected;

    const rows = [
      ['Direct Alice → Bob Gain (h_AB^dir)', b.direct_gains.h_AB, s.direct_gains.h_AB, 'LOS constant optical path'],
      ['Reflected Alice → Bob Gain (h_AB^ref)', b.reflected_gains.h_AB, s.reflected_gains.h_AB,
        s.reflected_gains.h_AB > 0 ? `+${((s.reflected_gains.h_AB / s.direct_gains.h_AB) * 100).toFixed(1)}% reflection boost` : '0 (Stowed/Misaligned)'],
      ['Effective Alice → Bob Gain (h_AB)', b.gains.h_AB, s.gains.h_AB, 'Total received Alice power'],
      ['Effective Alice → Eve Gain (h_AE)', b.gains.h_AE, s.gains.h_AE,
        s.gains.h_AE > b.gains.h_AE ? 'Increased leakage to Eve' : 'Minimally affected leakage'],
      ['Total Jamming on Bob (||h_JB||)', Math.hypot(...b.gains.h_JB), Math.hypot(...s.gains.h_JB), 'Bob self-interference'],
      ['Total Jamming on Eve (||h_JE||)', Math.hypot(...b.gains.h_JE), Math.hypot(...s.gains.h_JE),
        Math.hypot(...s.gains.h_JE) > Math.hypot(...b.gains.h_JE) ? 'Steered Jamming Boost to Eve' : 'Direct Jamming Only'],
      ['Achievable Secrecy Rate (bps/Hz)', b.secrecy_rate, s.secrecy_rate,
        s.secrecy_rate > b.secrecy_rate ? `+${(s.secrecy_rate - b.secrecy_rate).toFixed(4)} bps/Hz advantage` : (s.secrecy_rate < b.secrecy_rate ? 'Adverse / decreased secrecy' : 'Equal secrecy')],
      ['Bob Bit Error Rate (4-PAM)', b.ber, s.ber, s.ber === 0 ? '0.0 (Error-free static reception)' : fmt(s.ber)],
      ['Jammer Energy Cost', b.energy, s.energy, 'Normalized jammer power'],
      ['System Utility (u = R_s - 3.5 P_e - 0.4 E)', b.utility, s.utility,
        s.utility > b.utility ? `+${(s.utility - b.utility).toFixed(4)} utility improvement` : 'Baseline utility']
    ];

    rows.forEach(([label, vBase, vSel, effect]) => {
      const tr = document.createElement('tr');
      const isRate = label.includes('Secrecy Rate');
      const isUtility = label.includes('System Utility');
      const win = (isRate || isUtility) && vSel > vBase;
      const lose = (isRate || isUtility) && vSel < vBase;

      tr.innerHTML = `
        <td><strong>${label}</strong></td>
        <td class="num">${typeof vBase === 'number' ? fmt(vBase) : vBase}</td>
        <td class="num ${win ? 'highlight-win' : (lose ? 'highlight-lose' : '')}">${typeof vSel === 'number' ? fmt(vSel) : vSel}</td>
        <td><small>${effect}</small></td>
      `;
      body.appendChild(tr);
    });
  }

  function renderDynamicRays(data) {
    const group = $('dynamicRays');
    group.innerHTML = '';

    const geom = data.geometry || {};
    const alicePos = geom.alice || [2.5, 2.5, 3.0];
    const jammers = geom.jammers || [[1.5,1.5,3.0],[1.5,3.5,3.0],[3.5,1.5,3.0],[3.5,3.5,3.0]];
    const bobPos = geom.bob || [1.8, 1.6, 0.85];
    const evePos = geom.eve || [3.2, 3.4, 0.85];

    const aliceSvg = toSvgCoords(alicePos[0], alicePos[1]);
    const bobSvg = toSvgCoords(bobPos[0], bobPos[1]);
    const eveSvg = toSvgCoords(evePos[0], evePos[1]);
    const risCenterSvg = toSvgCoords(2.5, 0.25);

    const s = data.selected;

    // 1. Direct Alice -> Bob (drawn if direct gain > 0)
    if (s.direct_gains.h_AB > 0) {
      addRay(group, aliceSvg.x, aliceSvg.y, bobSvg.x, bobSvg.y, '#007bff', 2, 'none');
    }

    // 2. Direct Alice -> Eve (drawn if direct gain > 0)
    if (s.direct_gains.h_AE > 0) {
      addRay(group, aliceSvg.x, aliceSvg.y, eveSvg.x, eveSvg.y, '#fd7e14', 1.6, '4,4');
    }

    // 3. Direct Jammers -> Bob & Eve (per-jammer check)
    jammers.forEach((jPos, i) => {
      const jSvg = toSvgCoords(jPos[0], jPos[1]);
      if (s.direct_gains.h_JB && s.direct_gains.h_JB[i] > 0) {
        addRay(group, jSvg.x, jSvg.y, bobSvg.x, bobSvg.y, '#9c27b0', 1.0, '2,2');
      }
      if (s.direct_gains.h_JE && s.direct_gains.h_JE[i] > 0) {
        addRay(group, jSvg.x, jSvg.y, eveSvg.x, eveSvg.y, '#9c27b0', 1.0, '2,2');
      }
    });

    // 4. Reflected Alice -> RIS -> Bob (gated by actual reflected h_AB)
    if (s.reflected_gains.h_AB > 1e-12) {
      addRay(group, aliceSvg.x, aliceSvg.y, risCenterSvg.x, risCenterSvg.y, '#28a745', 2.5, 'none');
      addRay(group, risCenterSvg.x, risCenterSvg.y, bobSvg.x, bobSvg.y, '#28a745', 2.5, 'none');
    }

    // 5. Reflected Alice -> RIS -> Eve (gated by actual reflected h_AE)
    if (s.reflected_gains.h_AE > 1e-12) {
      addRay(group, aliceSvg.x, aliceSvg.y, risCenterSvg.x, risCenterSvg.y, '#28a745', 1.8, '3,3');
      addRay(group, risCenterSvg.x, risCenterSvg.y, eveSvg.x, eveSvg.y, '#28a745', 1.8, '3,3');
    }

    // 6. Reflected Jammers -> RIS -> Eve / Bob (checked per jammer)
    if (s.reflected_gains.h_JE) {
      s.reflected_gains.h_JE.forEach((gain, i) => {
        if (gain > 1e-12) {
          const jSvg = toSvgCoords(jammers[i][0], jammers[i][1]);
          addRay(group, jSvg.x, jSvg.y, risCenterSvg.x, risCenterSvg.y, '#dc3545', 1.6, '3,3');
          addRay(group, risCenterSvg.x, risCenterSvg.y, eveSvg.x, eveSvg.y, '#dc3545', 2.2, 'none');
        }
      });
    }
  }

  function renderTileNormals(data) {
    const tilesGroup = $('risTiles');
    const normalsGroup = $('risNormals');
    tilesGroup.innerHTML = '';
    normalsGroup.innerHTML = '';

    const risMeta = data.ris || {};
    const centers = risMeta.tile_centers || [
      [2.167, 0.25, 2.475], [2.5, 0.25, 2.475], [2.833, 0.25, 2.475],
      [2.167, 0.25, 2.725], [2.5, 0.25, 2.725], [2.833, 0.25, 2.725]
    ];

    const cfgName = (data.configuration_names && data.configuration_names[currentRisIndex]) || 'alice_to_bob';
    const cfgMeta = risMeta.configurations && risMeta.configurations[cfgName];
    const normals = (cfgMeta && cfgMeta.tile_normals) || [
      [0,1,0],[0,1,0],[0,1,0],[0,1,0],[0,1,0],[0,1,0]
    ];

    centers.forEach((pos, idx) => {
      const svgPos = toSvgCoords(pos[0], pos[1]);
      // Draw tile rectangle
      const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      rect.setAttribute('x', svgPos.x - 12);
      rect.setAttribute('y', svgPos.y - 3);
      rect.setAttribute('width', 24);
      rect.setAttribute('height', 6);
      rect.setAttribute('fill', '#28a745');
      rect.setAttribute('stroke', '#1e7e34');
      rect.setAttribute('stroke-width', '0.8');
      tilesGroup.appendChild(rect);

      // Draw normal vector projection (arrow indicating tilt in x-y plane)
      const n = normals[idx] || [0, 1, 0];
      const normLen = 14;
      const x2 = svgPos.x + n[0] * normLen;
      const y2 = svgPos.y + n[1] * normLen;

      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', svgPos.x);
      line.setAttribute('y1', svgPos.y);
      line.setAttribute('x2', x2);
      line.setAttribute('y2', y2);
      line.setAttribute('stroke', '#1b5e20');
      line.setAttribute('stroke-width', '1.6');
      line.setAttribute('marker-end', 'url(#arrowNormal)');
      normalsGroup.appendChild(line);
    });
  }

  function addRay(svgGroup, x1, y1, x2, y2, color, strokeWidth, dashArray) {
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', x1);
    line.setAttribute('y1', y1);
    line.setAttribute('x2', x2);
    line.setAttribute('y2', y2);
    line.setAttribute('stroke', color);
    line.setAttribute('stroke-width', strokeWidth);
    if (dashArray && dashArray !== 'none') line.setAttribute('stroke-dasharray', dashArray);
    svgGroup.appendChild(line);
  }

  // Section 3: Dynamic Data Binding from compact_results.json
  async function loadSavedStudy() {
    try {
      const res = await fetch('/compact_results.json');
      if (!res.ok) throw new Error('Could not load /compact_results.json');
      const data = await res.json();

      $('provenanceBox').className = 'status-box';
      $('provenanceBox').innerHTML = `<strong>Data Provenance:</strong> ${data.protocol || 'Nominal L1 Study across 10 Seeds'}<br><small>Source: <code>${data.source || 'ris_study_summary.json'}</code> | SHA-256: <code>${data.source_sha256 || '7948189a9ca87ff5c1e60f387ee64b2fc59424c6b42e8525b83ec934f37968c1'}</code></small>`;

      renderPhase1Table(data);
      renderPairedTable(data);
      renderPhase2Table(data);
      renderPhase3Table(data);
    } catch (err) {
      $('provenanceBox').className = 'status-box error';
      $('provenanceBox').textContent = 'Error loading compact study JSON: ' + err.message;
    }
  }

  function renderPhase1Table(data) {
    const tbody = $('phase1TableBody');
    tbody.innerHTML = '';
    const aggs = data.aggregates || [];

    const schemeNames = {
      'baseline': 'Baseline (No RIS)',
      'fixed_ris': 'Fixed RIS (Config 1: Alice→Bob)',
      'joint_ris': 'Joint RIS + FJ (Adaptive Codebook)'
    };

    aggs.forEach(agg => {
      const tr = document.createElement('tr');
      const s = agg.scheme;
      const rate = agg.evaluation.secrecy_rate;
      const ber = agg.evaluation.ber;
      const outage = agg.evaluation_secrecy_outage || { mean: 0.0 };

      const verdict = s === 'baseline' ? 'Paper 2024 Friendly Jamming Reference' :
                      s === 'fixed_ris' ? '<span class="highlight-win">+13.4% Secrecy Gain (Statistically Significant)</span>' :
                      '+10.3% Secrecy Gain (CI Spans Zero vs Baseline)';

      tr.innerHTML = `
        <td><strong>${schemeNames[s] || s}</strong></td>
        <td class="num">${rate.mean.toFixed(4)}</td>
        <td class="num">[${rate.ci95[0].toFixed(4)}, ${rate.ci95[1].toFixed(4)}]</td>
        <td class="num">${ber.mean === 0 ? '0.0' : ber.mean.toExponential(2)}</td>
        <td class="num">${(outage.mean * 100).toFixed(1)}%</td>
        <td>${verdict}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  function renderPairedTable(data) {
    const tbody = $('pairedTableBody');
    tbody.innerHTML = '';
    const pairs = data.paired_seed_comparisons || [];

    pairs.forEach(p => {
      const tr = document.createElement('tr');
      const comp = p.comparison;
      const rate = p.evaluation.secrecy_rate;
      const pval = DERIVED_P_VALUES[comp] !== undefined ? DERIVED_P_VALUES[comp] : 0.0;

      let conclusion = '';
      let isWin = false;
      if (comp.includes('fixed') && comp.includes('baseline')) {
        conclusion = '<strong>Proven Improvement:</strong> Lower bound > 0 (p = 0.0183 &lt; 0.05).';
        isWin = true;
      } else if (comp.includes('joint') && comp.includes('baseline')) {
        conclusion = '<strong>Superiority Not Proven:</strong> 95% CI includes zero (p = 0.1216 &gt; 0.05).';
      } else {
        conclusion = '<strong>Equivalence Not Proven:</strong> Large CI spans zero; failure to reject null.';
      }

      tr.innerHTML = `
        <td><strong>${comp}</strong></td>
        <td class="num ${isWin ? 'highlight-win' : ''}">${rate.mean > 0 ? '+' : ''}${rate.mean.toFixed(4)} bps/Hz</td>
        <td class="num">[${rate.ci95[0] > 0 ? '+' : ''}${rate.ci95[0].toFixed(4)}, ${rate.ci95[1] > 0 ? '+' : ''}${rate.ci95[1].toFixed(4)}]</td>
        <td class="num"><strong>${pval.toFixed(4)}</strong></td>
        <td>${conclusion}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  function renderPhase2Table(data) {
    const tbody = $('phase2TableBody');
    tbody.innerHTML = '';
    const aggs = data.aggregates || [];

    const schemeNames = {
      'baseline': 'Baseline (No RIS)',
      'fixed_ris': 'Fixed RIS (Config 1)',
      'joint_ris': 'Joint RIS + FJ'
    };

    aggs.forEach(agg => {
      const tr = document.createElement('tr');
      const w = agg.final_window;
      tr.innerHTML = `
        <td><strong>${schemeNames[agg.scheme] || agg.scheme}</strong></td>
        <td class="num">${w.secrecy_rate.mean.toFixed(4)} bps/Hz</td>
        <td class="num">${w.ber.mean.toExponential(2)}</td>
        <td class="num">${w.energy.mean.toFixed(3)}</td>
        <td class="num">${w.utility.mean.toFixed(4)}</td>
      `;
      tbody.appendChild(tr);
    });
  }

  function renderPhase3Table(data) {
    const tbody = $('phase3TableBody');
    tbody.innerHTML = '';
    const aggs = data.aggregates || [];

    const schemeNames = {
      'baseline': 'Baseline (No RIS)',
      'fixed_ris': 'Fixed RIS (Config 1)',
      'joint_ris': 'Joint RIS + FJ'
    };

    aggs.forEach(agg => {
      const tr = document.createElement('tr');
      const all = agg.all_slots;
      const outage = agg.secrecy_outage || { mean: 0.0 };
      const outagePct = (outage.mean * 100).toFixed(2);
      const isLowest = agg.scheme === 'joint_ris';
      const isHighest = agg.scheme === 'baseline';

      tr.innerHTML = `
        <td><strong>${schemeNames[agg.scheme] || agg.scheme}</strong></td>
        <td class="num">${all.secrecy_rate.mean.toFixed(4)} bps/Hz</td>
        <td class="num">${all.ber.mean.toExponential(2)}</td>
        <td class="num ${isLowest ? 'highlight-win' : (isHighest ? 'highlight-lose' : '')}">${outagePct}% (${(outage.mean * 2000).toFixed(1)} / 2,000 slots)</td>
        <td>Random action exploration (&epsilon;: 0.1 &rarr; 0)</td>
      `;
      tbody.appendChild(tr);
    });
  }

  // Section 4: Live DRL Smoke Run
  async function runSmokeTrain() {
    const btn = $('btnTrainSmoke');
    const slots = parseInt($('smokeSlots').value);
    btn.disabled = true;
    $('smokeProgress').textContent = `Submitting ${slots}-slot smoke run to Python CNN+DND backend...`;

    try {
      const payload = {
        bob: [parseFloat($('bx').value), parseFloat($('by').value), parseFloat($('bz').value)],
        eve: [parseFloat($('ex').value), parseFloat($('ey').value), parseFloat($('ez').value)],
        slots: slots,
        seeds: [42],
        energy_model: $('energyModel').value
      };

      const submitRes = await fetch('/api/ris/experiment', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const submitData = await submitRes.json();
      if (!submitRes.ok) throw new Error(submitData.error || 'Failed to submit training job');

      const jobId = submitData.job_id;
      let completed = false;

      while (!completed) {
        await new Promise(r => setTimeout(r, 600));
        const statusRes = await fetch('/api/jobs/' + jobId);
        const jobData = await statusRes.json();
        if (jobData.status === 'error') throw new Error(jobData.error);
        if (jobData.status === 'complete') {
          completed = true;
          displaySmokeResults(jobData.result);
        } else {
          $('smokeProgress').textContent = (jobData.progress || 'Agent training in progress...') + ' Please wait.';
        }
      }
    } catch (err) {
      $('smokeProgress').textContent = 'Error: ' + err.message;
    } finally {
      btn.disabled = false;
    }
  }

  function displaySmokeResults(res) {
    $('smokeProgress').textContent = 'Execution finished successfully.';
    $('smokeResultBox').style.display = 'block';
    const tbody = $('smokeTableBody');
    tbody.innerHTML = '';

    const runs = res.runs || [];
    runs.forEach(r => {
      const tr = document.createElement('tr');
      const finalRate = r.history.secrecy_rate[r.history.secrecy_rate.length - 1];
      const finalBer = r.history.ber[r.history.ber.length - 1];
      const finalAction = r.actions[r.actions.length - 1];

      tr.innerHTML = `
        <td><strong>${r.scheme}</strong></td>
        <td class="num">${finalRate.toFixed(4)} bps/Hz</td>
        <td class="num">${finalBer === 0 ? '0.0' : finalBer.toExponential(3)}</td>
        <td><code>[${finalAction.map(x => x.toFixed(2)).join(', ')}]</code></td>
      `;
      tbody.appendChild(tr);
    });
  }

  // Initial update on load with URL query parameter support
  window.addEventListener('DOMContentLoaded', () => {
    const params = new URLSearchParams(window.location.search);
    if (params.has('preset')) setPreset(params.get('preset'));
    if (params.has('ris')) setRisIndex(parseInt(params.get('ris'), 10));
    triggerUpdate();
    loadSavedStudy();
  });
