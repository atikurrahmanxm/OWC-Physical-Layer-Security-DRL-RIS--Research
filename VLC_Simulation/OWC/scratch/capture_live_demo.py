"""Script to start app_server and capture headless Edge screenshots of the 3D demo."""
import subprocess
import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from app_server import start_server

EDGE_PATH = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not Path(EDGE_PATH).exists():
    print(f"Edge not found at {EDGE_PATH}")
    sys.exit(1)

OUTPUT_DIR = Path("supervisor_package/figures")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

server, base_url = start_server()
print(f"Server started at {base_url}")

try:
    time.sleep(1.0)
    
    # 1. Capture Nominal 3D Scene (Default)
    url_nominal = f"{base_url}demo"
    out_nominal = str((OUTPUT_DIR / "demo_3d_nominal.png").resolve())
    out_main = str((OUTPUT_DIR / "demo_screenshot.png").resolve())
    print(f"Capturing {out_nominal} from {url_nominal}...")
    
    cmd1 = [
        EDGE_PATH,
        "--headless",
        "--disable-gpu",
        "--window-size=1280,1024",
        f"--screenshot={out_nominal}",
        url_nominal
    ]
    res1 = subprocess.run(cmd1, timeout=20)
    print("res1:", res1.returncode)
    
    cmd_main = [
        EDGE_PATH,
        "--headless",
        "--disable-gpu",
        "--window-size=1280,1024",
        f"--screenshot={out_main}",
        url_nominal
    ]
    res_m = subprocess.run(cmd_main, timeout=20)
    print("res_m:", res_m.returncode)
    
    # 2. Capture Changed Configuration: Near-Bob Boundary Preset
    url_near_bob = f"{base_url}demo?preset=near_bob"
    out_near_bob = str((OUTPUT_DIR / "demo_3d_near_bob.png").resolve())
    print(f"Capturing {out_near_bob} from {url_near_bob}...")
    cmd2 = [
        EDGE_PATH,
        "--headless",
        "--disable-gpu",
        "--window-size=1280,1024",
        f"--screenshot={out_near_bob}",
        url_near_bob
    ]
    res2 = subprocess.run(cmd2, timeout=20)
    print("res2:", res2.returncode)
    
    # 3. Capture Changed Configuration: Stowed/Off RIS (Config 0)
    url_stowed = f"{base_url}demo?ris=0"
    out_stowed = str((OUTPUT_DIR / "demo_3d_stowed.png").resolve())
    print(f"Capturing {out_stowed} from {url_stowed}...")
    cmd3 = [
        EDGE_PATH,
        "--headless",
        "--disable-gpu",
        "--window-size=1280,1024",
        f"--screenshot={out_stowed}",
        url_stowed
    ]
    res3 = subprocess.run(cmd3, timeout=20)
    print("res3:", res3.returncode)
    
    print("All screenshots successfully captured!")
finally:
    print("Shutting down server...")
    server.shutdown()
    server.server_close()
