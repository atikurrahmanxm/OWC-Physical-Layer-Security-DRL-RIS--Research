#!/usr/bin/env python3
"""Dedicated launcher for the Optical RIS + Friendly Jamming Supervisor Demo."""
import sys
import threading
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def check_dependencies():
    missing = []
    for pkg in ["numpy", "torch", "matplotlib"]:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)
    if missing:
        print("=" * 76)
        print("   OPTICAL RIS + FRIENDLY JAMMING SECURE VLC: SUPERVISOR DEMO LAUNCHER")
        print("=" * 76)
        print(f"\n[ERROR] Missing required Python package(s): {', '.join(missing)}")
        print("Please install them before running the supervisor demo:")
        print(f"    pip install {' '.join(missing)}\n")
        sys.exit(1)


def main():
    check_dependencies()
    print("=" * 76)
    print("   OPTICAL RIS + FRIENDLY JAMMING SECURE VLC: SUPERVISOR DEMO LAUNCHER")
    print("=" * 76)
    try:
        from app_server import start_server
        server, url = start_server()
    except Exception as exc:
        print(f"\n[ERROR] Failed to start simulation loopback service: {exc}")
        sys.exit(1)

    demo_url = f"{url}demo"
    print(f"\n[+] Local Loopback Server started successfully on ephemeral IPv4 loopback!")
    print(f"    Supervisor Demo URL : {demo_url}")
    print(f"    Full Research Controls: {url}ris")
    print(f"    Paper Visualizer     : {url}")
    print("\n[*] Opening demonstration page in default web browser...")
    webbrowser.open(demo_url)
    print("\n[!] The simulation service is actively running and processing requests.")
    print("    Press Ctrl+C in this terminal window to stop the demo server cleanly.\n" + "-" * 76)
    try:
        while True:
            threading.Event().wait(1)
    except KeyboardInterrupt:
        print("\n[*] Shutting down simulation service...")
    finally:
        server.shutdown()
        server.server_close()
        print("[+] Service stopped cleanly. No background processes left running.")


if __name__ == "__main__":
    main()
