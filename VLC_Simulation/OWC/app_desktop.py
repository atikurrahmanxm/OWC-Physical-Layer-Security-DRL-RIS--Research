"""
Native Desktop Application for Secure VLC Friendly Jamming Simulator.
Launches the 3D Interactive Simulator and Live Telemetry as a native Windows
desktop application window (standalone software mode) without browser tabs.
"""

import os
import sys

ROOT_DIR = os.path.abspath(os.path.dirname(__file__))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import webview


def launch_desktop_app():
    html_file = os.path.join(ROOT_DIR, "index.html")
    if not os.path.exists(html_file):
        html_file = os.path.join(ROOT_DIR, "visualizer.html")
    if not os.path.exists(html_file):
        print(f"Error: Could not find index.html at {html_file}")
        sys.exit(1)

    print("=" * 70)
    print("Launching VLC Smart Jamming Simulator in Desktop Application Mode...")
    print("=" * 70)

    # Create native standalone desktop window
    window = webview.create_window(
        title="Secure Visible Light Communication - Smart Friendly Jamming 3D Simulator",
        url=f"file:///{html_file}",
        width=1400,
        height=880,
        min_size=(1024, 700),
        resizable=True,
        fullscreen=False,
    )

    # Start the desktop application GUI event loop
    webview.start(gui="edgechromium")


if __name__ == "__main__":
    launch_desktop_app()
