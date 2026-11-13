"""Script to update supervisor_demo.html with dynamic 3D visualizer and DRL action replay."""
import re
from pathlib import Path

html_path = Path("supervisor_demo.html")
content = html_path.read_text(encoding="utf-8")

# 1. Add CSS for 3D stage and replay card
css_additions = """
    /* 3D Dynamic Visualizer Stage Styles */
    .stage3d-wrapper {
      background: radial-gradient(circle at 50% 20%, #112238 0%, #080f1a 100%);
      border: 1px solid #1e3a5f;
      border-radius: 12px;
      overflow: hidden;
      margin-bottom: 20px;
      position: relative;
      box-shadow: 0 6px 24px rgba(0, 0, 0, 0.28);
    }
    .stage3d-toolbar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 8px;
      background: rgba(13, 27, 42, 0.95);
      border-bottom: 1px solid #1e3a5f;
      padding: 8px 14px;
      backdrop-filter: blur(8px);
    }
    .stage3d-group {
      display: flex;
      gap: 6px;
      align-items: center;
      flex-wrap: wrap;
    }
    .stage3d-btn {
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.16);
      color: #e2eeff;
      padding: 5px 10px;
      border-radius: 5px;
      font-size: 12px;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.15s ease;
    }
    .stage3d-btn:hover {
      background: rgba(21, 87, 153, 0.45);
      border-color: #3b82f6;
      color: #fff;
    }
    .stage3d-btn.active {
      background: #155799;
      border-color: #38bdf8;
      color: #fff;
    }
    .stage3d-hud {
      position: absolute;
      pointer-events: none;
      font-family: monospace;
      font-size: 11.5px;
      color: #cbd5e1;
      text-shadow: 0 1px 3px rgba(0, 0, 0, 0.9);
      padding: 8px 12px;
      z-index: 10;
    }
    .stage3d-hud-tl { top: 48px; left: 8px; line-height: 1.5; }
    .stage3d-hud-bl { bottom: 38px; left: 10px; right: 10px; font-size: 11px; color: #94a3b8; line-height: 1.4; }
    .stage3d-footer-toggles {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      gap: 12px;
      background: rgba(13, 27, 42, 0.95);
      border-top: 1px solid #1e3a5f;
      padding: 7px 14px;
      font-size: 12px;
      color: #94a3b8;
    }
    .stage3d-footer-toggles label {
      cursor: pointer;
      display: inline-flex;
      align-items: center;
      gap: 5px;
      user-select: none;
    }
    .stage3d-footer-toggles label:hover { color: #f1f5f9; }
    .pulse-badge {
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-size: 11.5px;
      font-weight: 600;
      background: rgba(16, 185, 129, 0.18);
      color: #34d399;
      border: 1px solid rgba(16, 185, 129, 0.35);
      padding: 3px 8px;
      border-radius: 999px;
    }
    .pulse-dot {
      width: 7px;
      height: 7px;
      border-radius: 50%;
      background: #34d399;
      box-shadow: 0 0 8px #34d399;
      animation: pulseAnim 1.8s infinite ease-in-out;
    }
    @keyframes pulseAnim {
      0%, 100% { opacity: 0.4; transform: scale(0.85); }
      50% { opacity: 1.0; transform: scale(1.15); }
    }
    /* DRL Recorded-Action Replay Scrubber Styles */
    .replay-card {
      margin-top: 16px;
      padding: 14px;
      background: #f0f7ff;
      border-radius: 8px;
      border: 1px solid #bfdbfe;
    }
    .replay-header {
      display: flex;
      justify-content: space-between;
      align-items: center;
      flex-wrap: wrap;
      margin-bottom: 6px;
    }
    .replay-badge {
      font-size: 12px;
      font-weight: bold;
      background: #1e40af;
      color: #fff;
      padding: 3px 9px;
      border-radius: 12px;
    }
    .replay-ctrls {
      display: flex;
      gap: 8px;
      align-items: center;
      flex-wrap: wrap;
      margin-top: 8px;
    }
    .replay-readout {
      margin-top: 10px;
      font-family: monospace;
      font-size: 12px;
      background: #fff;
      padding: 8px 12px;
      border-radius: 6px;
      border: 1px solid #cbd5e1;
    }
"""

if ".stage3d-wrapper" not in content:
    content = content.replace(".img-grid img { width: 100%; height: auto; border: 1px solid #d8e2ec; border-radius: 6px; background: white; }",
                            ".img-grid img { width: 100%; height: auto; border: 1px solid #d8e2ec; border-radius: 6px; background: white; }" + css_additions)

# 2. Update Section 1 with tab switcher and full 3D stage
sec1_pattern = re.compile(
    r'<section class="card">\s*<h2>1 · Optical Geometry & Channel Gain Activity \(Top-Down Floorplan Projection\)</h2>.*?'
    r'<div class="grid-2">\s*<!-- SVG Floorplan -->\s*<div class="svg-container">',
    re.DOTALL
)

sec1_replacement = """<section class="card">
    <h2>1 · Optical Geometry & Channel Gain Activity (Top-Down Floorplan Projection)</h2>
    <p class="note">
      Interactive 3D indoor VLC/RIS environment and 2D floorplan projection for the 5.0 m × 5.0 m × 3.0 m room. Node coordinates, mirror facet centers, and tile normals are bound directly to Python backend geometry metadata. Active optical links and flowing photon pulses reflect backend-computed direct and reflected gains (&gt; 0).
    </p>

    <!-- Stage View Selector Tabs -->
    <div class="tab-bar no-print" style="margin-bottom: 12px;">
      <button type="button" class="tab-btn active" id="tabStage3D" onclick="switchStageView('3d')">🏢 3D Dynamic Interactive Room &amp; Optical Light Beams</button>
      <button type="button" class="tab-btn" id="tabStage2D" onclick="switchStageView('2d')">🗺️ 2D Floorplan Schematic Projection</button>
    </div>

    <!-- 3D Interactive Stage Container -->
    <div id="container3D" class="stage3d-wrapper">
      <div class="stage3d-toolbar">
        <div class="stage3d-group">
          <span style="font-size:12px; font-weight:bold; color:#e2eeff; margin-right:4px;">Camera Angle:</span>
          <button type="button" class="stage3d-btn active" id="btnCamOrbit" onclick="setCameraMode('orbit')">🪐 3D Orbit</button>
          <button type="button" class="stage3d-btn" id="btnCamTop" onclick="setCameraMode('top')">🦅 Top-Down</button>
          <button type="button" class="stage3d-btn" id="btnCamSide" onclick="setCameraMode('side')">📐 Side Elevation</button>
          <button type="button" class="stage3d-btn" id="btnCamFront" onclick="setCameraMode('front')">🪞 Front Wall (RIS)</button>
          <button type="button" class="stage3d-btn" onclick="resetCamera()">🔄 Reset</button>
        </div>
        <div class="stage3d-group">
          <button type="button" class="stage3d-btn" onclick="zoomCamera(1.2)" title="Zoom in">🔍 +</button>
          <button type="button" class="stage3d-btn" onclick="zoomCamera(0.85)" title="Zoom out">🔍 −</button>
          <button type="button" class="stage3d-btn" id="btnPulseFlow" onclick="togglePulseFlow()">⏸ Pause Flow</button>
          <select id="flowSpeedSel" class="stage3d-btn" onchange="setFlowSpeed(this.value)" style="padding:4px 6px;">
            <option value="1.0" selected>1.0x Speed</option>
            <option value="0.5">0.5x Speed</option>
            <option value="2.0">2.0x Speed</option>
          </select>
          <div class="pulse-badge"><div class="pulse-dot"></div><span>Active Flowing Beams</span></div>
        </div>
      </div>

      <div style="position:relative; width:100%; height:520px;">
        <canvas id="room3D" style="display:block; width:100%; height:100%; touch-action:none; cursor:grab;" aria-label="Interactive 3D indoor VLC room with optical RIS, Alice LED, Friendly Jammers, Bob and Eve"></canvas>
        <div id="hudTopLeft" class="stage3d-hud stage3d-hud-tl">
          <div><strong>Room:</strong> 5.0m × 5.0m × 3.0m · 6 Specular Mirror Tiles (0.2m × 0.2m)</div>
          <div id="hudCamInfo">Camera: Yaw -37.2° · Pitch 31.5° · Zoom 1.0x</div>
          <div id="hudRisInfo" style="color:#38bdf8; font-weight:bold;">RIS State: 1 (Aim Alice → Bob) · 6 Tiles Aligned</div>
          <div id="hudDistInfo" style="color:#fbbf24;">Bob: (1.80, 1.60, 0.85)m · Eve: (3.20, 3.40, 0.85)m · d_BE = 2.28m</div>
        </div>
        <div id="hudBottom" class="stage3d-hud stage3d-hud-bl">
          <strong>Illustrative Visualizer:</strong> Pulse flow depicts link activity and direction based on backend computed positive gains (h &gt; 0). No packet timing, photon counts, or propagation delays are modeled by animation alone. Reflected paths connect via the optical RIS panel.
        </div>
      </div>

      <div class="stage3d-footer-toggles">
        <label><input type="checkbox" id="chkDirect" checked onchange="toggleLayer('direct', this.checked)"> Direct Links (Alice→Bob, Alice→Eve)</label>
        <label><input type="checkbox" id="chkReflected" checked onchange="toggleLayer('reflected', this.checked)"> Reflected Links (via RIS Panel)</label>
        <label><input type="checkbox" id="chkJammers" checked onchange="toggleLayer('jammers', this.checked)"> Friendly Jammers &amp; Nulls</label>
        <label><input type="checkbox" id="chkNormals" checked onchange="toggleLayer('normals', this.checked)"> Mirror Normals &amp; Tilts</label>
        <label><input type="checkbox" id="chkGrid" checked onchange="toggleLayer('grid', this.checked)"> Floor Grid &amp; Shadows</label>
        <label><input type="checkbox" id="chkLabels" checked onchange="toggleLayer('labels', this.checked)"> Labels &amp; Distances</label>
      </div>
    </div>

    <!-- 2D Floorplan Projection Container (Collapsible / Secondary Tab) -->
    <div id="container2D" style="display:none; margin-bottom:20px;">
      <div class="svg-container">"""

content = sec1_pattern.sub(sec1_replacement, content, count=1)

# Close #container2D
svg_close_pattern = re.compile(
    r'(<div class="legend-box">.*?</div>\s*</div>)(\s*<!-- Geometry Presets & Controls -->)',
    re.DOTALL
)
content = svg_close_pattern.sub(r'\1\n    </div><!-- End #container2D -->\n\n    <!-- Geometry Presets & Controls Grid -->\n    <div class="grid-2">\2', content, count=1)

# Also ensure closing div for the grid-2 before </section>
# Let's inspect around lines 345-355
if '</div>\n  </section>\n\n  <!-- SECTION 2: LIVE POINT METRICS -->' in content:
    content = content.replace('</div>\n  </section>\n\n  <!-- SECTION 2: LIVE POINT METRICS -->',
                              '</div><!-- End grid-2 -->\n  </section>\n\n  <!-- SECTION 2: LIVE POINT METRICS -->')

# 3. Add Replay card in Section 4
replay_html = """
      <!-- Recorded-Action Replay Timeline Scrubber -->
      <div id="smokeReplayBox" class="replay-card" style="display:none;">
        <div class="replay-header">
          <strong>🎬 Recorded-Action Replay Timeline (Post-Training)</strong>
          <span id="replaySlotBadge" class="replay-badge">Slot k = 1 / 24</span>
        </div>
        <p style="font-size:12px; color:#475569; margin:4px 0 10px 0;">
          Replay genuine recorded action vectors from the completed Python smoke run. Training was executed synchronously on the Python backend prior to replay.
        </p>
        <div class="replay-ctrls">
          <button type="button" class="btn-preset" id="btnReplayPrev" onclick="stepReplay(-1)">⏮ Prev Slot</button>
          <button type="button" class="primary" id="btnReplayPlay" onclick="toggleReplayPlay()">▶ Play Replay</button>
          <button type="button" class="btn-preset" id="btnReplayNext" onclick="stepReplay(1)">Next Slot ⏭</button>
          <input type="range" id="replaySlider" min="1" max="24" value="1" style="flex:1; min-width:140px;" oninput="onReplaySlider(this.value)">
          <label style="font-size:12.5px; font-weight:600; display:flex; align-items:center; gap:4px; user-select:none;">
            <input type="checkbox" id="chkSync3D" checked> Sync 3D Scene
          </label>
        </div>
        <div id="replayActionReadout" class="replay-readout">
          Ready for playback.
        </div>
      </div>
"""

if '<div id="smokeReplayBox"' not in content:
    content = content.replace('      </table>\n    </div>\n  </section>\n\n  <!-- SECTION 5:',
                              '      </table>\n' + replay_html + '    </div>\n  </section>\n\n  <!-- SECTION 5:')

# 4. Replace script at bottom
old_3d_script = re.compile(
    r'<script>\s*/\* Dependency-free 3D geometry projection.*?</script>\s*</body>',
    re.DOTALL
)

new_script = Path("scratch/dynamic_3d_engine.js").read_text(encoding="utf-8")
content = old_3d_script.sub(f"<script>\n{new_script}\n</script>\n</body>", content)

html_path.write_text(content, encoding="utf-8")
print("Updated supervisor_demo.html successfully.")

