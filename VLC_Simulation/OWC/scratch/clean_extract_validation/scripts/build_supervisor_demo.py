"""Build and verify supervisor_demo.html with dynamic 3D visualizer and DRL action replay.

Enforces strict assertion of exactly ONE script replacement.
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEMO_HTML = ROOT / "supervisor_demo.html"
ENGINE_JS = ROOT / "scratch" / "dynamic_3d_engine.js"


def main():
    if not DEMO_HTML.exists():
        raise FileNotFoundError(f"Missing {DEMO_HTML}")
    if not ENGINE_JS.exists():
        raise FileNotFoundError(f"Missing {ENGINE_JS}")

    html_content = DEMO_HTML.read_text(encoding="utf-8")
    engine_code = ENGINE_JS.read_text(encoding="utf-8")

    # 1. Update static HUD markup if old 0.2m x 0.2m label exists
    old_hud_str = "<div><strong>Room:</strong> 5.0m × 5.0m × 3.0m · 6 Specular Mirror Tiles (0.2m × 0.2m)</div>"
    new_hud_str = '<div id="hudRoomInfo"><strong>Room:</strong> 5.0m × 5.0m × 3.0m · 6 Specular Mirror Tiles (0.159m × 0.159m)</div>'
    if old_hud_str in html_content:
        html_content, hud_count = re.subn(re.escape(old_hud_str), new_hud_str, html_content, count=1)
        assert hud_count == 1, f"Expected exactly 1 HUD replacement, got {hud_count}"
        print("Updated static HUD tile-size markup to 0.159m x 0.159m.")
    elif new_hud_str in html_content:
        print("Static HUD markup already up to date with 0.159m x 0.159m.")
    else:
        print("Warning: Neither old nor new HUD markup found; checking hudTopLeft...")

    # 2. Strict replacement of the 3D engine script immediately preceding </body>
    # The pattern matches the final <script> tag before </body>
    engine_script_pattern = re.compile(
        r'<script[^>]*>(?:(?!<script)[\s\S])*?</script>\s*</body>',
        re.DOTALL
    )

    replacement = f"<script>\n{engine_code}\n</script>\n</body>"
    new_html, count = engine_script_pattern.subn(replacement, html_content, count=1)

    assert count == 1, f"BUILD INTEGRATION FAILED: Expected exactly 1 engine script replacement, got {count}!"

    # 3. Verify that new HTML contains the required fixes
    assert "Number.isFinite(w) ? w : 0.0" in new_html, "Verification failed: Number.isFinite check missing in HTML"
    assert "replayScenario" in new_html, "Verification failed: replayScenario isolation missing in HTML"
    assert "tile_side_m" in new_html, "Verification failed: tile_side_m missing in HTML"
    assert "0.2m x 0.2m" not in new_html and "0.2m × 0.2m" not in new_html, "Verification failed: 0.2m tile size still present in HTML"

    DEMO_HTML.write_text(new_html, encoding="utf-8")
    print(f"Successfully rebuilt {DEMO_HTML.name} ({len(new_html)} bytes, exactly 1 engine script replaced).")

    # 4. Extract embedded scripts and run node --check
    scripts = re.findall(r'<script.*?>([\s\S]*?)</script>', new_html)
    for idx, s in enumerate(scripts):
        tmp_file = ROOT / "scratch" / f"extracted_script_{idx}.js"
        tmp_file.write_text(s, encoding="utf-8")
        res = subprocess.run(["node", "--check", str(tmp_file)], capture_output=True, text=True)
        if res.returncode != 0:
            raise RuntimeError(f"Syntax error in embedded script {idx}:\n{res.stderr}")
        print(f"Script {idx} ({len(s)} chars) passed node --check.")


if __name__ == "__main__":
    main()

