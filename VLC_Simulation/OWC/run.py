#!/usr/bin/env python3
"""
Master Runner & Chat Portability Utility for Secure VLC Friendly Jamming Simulator.
IEEE Transactions on Wireless Communications (2024).

Features:
1. Unified Launcher: Desktop App, 3D Web Visualizer, Simulations, Tests, & Evals.
2. Chat & Brain Backup: Backup Antigravity conversations and brain files to 'anti_backup/.gemini'.
3. Chat & Brain Restore: Seamlessly restore conversation history and brain onto another device.
4. Interactive Terminal Menu: Run without arguments for an easy-to-use menu.
"""

import os
import sys
import shutil
import json
import time
import argparse
import platform
import subprocess
from datetime import datetime
from pathlib import Path

# Ensure repository root is on Python path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Default Active Conversation ID for this workspace
DEFAULT_CONV_ID = "1b0ef9f9-7359-4e98-952b-d5d6bf76f276"
DEFAULT_BACKUP_DIR = ROOT_DIR / "anti_backup" / ".gemini"


def get_default_gemini_dir() -> Path:
    """Returns the default .gemini directory path on the current system."""
    home = Path.home()
    return home / ".gemini"


# ==============================================================================
# CHAT & BRAIN BACKUP / RESTORE MODULE
# ==============================================================================

def backup_chats(
    conv_id: str = DEFAULT_CONV_ID,
    backup_root: Path = DEFAULT_BACKUP_DIR,
    backup_all: bool = False,
    source_gemini: Path = None,
) -> bool:
    """
    Backs up Antigravity conversation databases (.db, .db-wal, .db-shm),
    brain folders (transcripts, artifacts, uploads), and configurations
    to backup_root (default: anti_backup/.gemini).
    """
    if source_gemini is None:
        source_gemini = get_default_gemini_dir()

    print("\n" + "=" * 76)
    print("              ANTIGRAVITY CHATS & BRAIN BACKUP UTILITY")
    print("=" * 76)
    print(f"Source .gemini Directory : {source_gemini}")
    print(f"Target Backup Directory  : {backup_root}")

    if not source_gemini.exists():
        print(f"[!] ERROR: Source .gemini directory not found at: {source_gemini}")
        return False

    ide_dir = source_gemini / "antigravity-ide"
    conv_dir = ide_dir / "conversations"
    brain_dir = ide_dir / "brain"
    config_dir = source_gemini / "config"

    # Determine conversation IDs to back up
    target_ids = []
    if backup_all:
        if conv_dir.exists():
            for f in conv_dir.glob("*.db"):
                target_ids.append(f.stem)
        if not target_ids and conv_id:
            target_ids.append(conv_id)
    else:
        target_ids.append(conv_id)

    print(f"Target Conversation IDs  : {', '.join(target_ids)}")
    print("-" * 76)

    # Prepare backup destination paths
    dest_ide = backup_root / "antigravity-ide"
    dest_conv = dest_ide / "conversations"
    dest_brain = dest_ide / "brain"
    dest_config = backup_root / "config"

    dest_conv.mkdir(parents=True, exist_ok=True)
    dest_brain.mkdir(parents=True, exist_ok=True)
    dest_config.mkdir(parents=True, exist_ok=True)

    files_copied = 0
    bytes_copied = 0

    # 1. Backup conversation SQLite DB files
    print("\n[1/3] Backing up Conversation Database(s)...")
    if conv_dir.exists():
        for cid in target_ids:
            for ext in [".db", ".db-wal", ".db-shm"]:
                db_file = conv_dir / f"{cid}{ext}"
                if db_file.exists():
                    dest_file = dest_conv / db_file.name
                    shutil.copy2(db_file, dest_file)
                    size = db_file.stat().st_size
                    files_copied += 1
                    bytes_copied += size
                    print(f"  + Copied DB: {db_file.name} ({size / (1024*1024):.2f} MB)")
    else:
        print("  - conversations/ directory not found in source.")

    # 2. Backup Brain Directories (transcripts, artifacts, uploads)
    print("\n[2/3] Backing up Brain Directories (Transcripts, Artifacts, Media)...")
    if brain_dir.exists():
        for cid in target_ids:
            src_cid_brain = brain_dir / cid
            if src_cid_brain.exists():
                dest_cid_brain = dest_brain / cid
                dest_cid_brain.mkdir(parents=True, exist_ok=True)
                for root, dirs, files in os.walk(src_cid_brain):
                    rel = Path(root).relative_to(src_cid_brain)
                    target_sub = dest_cid_brain / rel
                    target_sub.mkdir(parents=True, exist_ok=True)
                    for file in files:
                        sfile = Path(root) / file
                        dfile = target_sub / file
                        shutil.copy2(sfile, dfile)
                        fsize = sfile.stat().st_size
                        files_copied += 1
                        bytes_copied += fsize
                brain_size_mb = sum(f.stat().st_size for f in dest_cid_brain.rglob("*") if f.is_file()) / (1024*1024)
                print(f"  + Copied Brain [{cid}]: {brain_size_mb:.2f} MB")
            else:
                print(f"  - No brain directory found for [{cid}]")
    else:
        print("  - brain/ directory not found in source.")

    # 3. Backup Configs & Manifest
    print("\n[3/3] Backing up Configs & Creating Manifest...")
    if config_dir.exists():
        for cfg_file in config_dir.glob("*"):
            if cfg_file.is_file():
                shutil.copy2(cfg_file, dest_config / cfg_file.name)
                files_copied += 1
                bytes_copied += cfg_file.stat().st_size
                print(f"  + Copied Config: {cfg_file.name}")

    # Write backup manifest
    manifest = {
        "timestamp": datetime.now().isoformat(),
        "source_os": platform.platform(),
        "source_user": os.environ.get("USERNAME") or os.environ.get("USER"),
        "conversation_ids": target_ids,
        "total_files": files_copied,
        "total_bytes": bytes_copied,
        "total_megabytes": round(bytes_copied / (1024 * 1024), 2),
        "instructions": "To restore on another device, clone repo and run: python run.py --restore-chats"
    }

    manifest_path = backup_root / "backup_manifest.json"
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)

    print("\n" + "=" * 76)
    print("BACKUP COMPLETED SUCCESSFULLY!")
    print(f"Total Files Copied : {files_copied}")
    print(f"Total Size         : {bytes_copied / (1024*1024):.2f} MB")
    print(f"Manifest File      : {manifest_path}")
    print(f"Destination Folder : {backup_root}")
    print("=" * 76 + "\n")
    return True


def restore_chats(
    backup_root: Path = DEFAULT_BACKUP_DIR,
    target_gemini: Path = None,
    overwrite: bool = True,
) -> bool:
    """
    Restores Antigravity conversation databases (.db, .db-wal, .db-shm),
    brain folders, and configurations from backup_root onto the current device.
    """
    if target_gemini is None:
        target_gemini = get_default_gemini_dir()

    print("\n" + "=" * 76)
    print("              ANTIGRAVITY CHATS & BRAIN RESTORE UTILITY")
    print("=" * 76)
    print(f"Source Backup Directory : {backup_root}")
    print(f"Target .gemini Profile  : {target_gemini}")

    if not backup_root.exists():
        print(f"[!] ERROR: Backup folder not found at: {backup_root}")
        print("    Make sure the 'anti_backup/.gemini' folder is present in the repository.")
        return False

    manifest_path = backup_root / "backup_manifest.json"
    if manifest_path.exists():
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
            print(f"Backup Created On       : {manifest.get('timestamp')}")
            print(f"Backup Created On OS    : {manifest.get('source_os')}")
            print(f"Backed Up Conversations : {manifest.get('conversation_ids')}")
            print(f"Backup Size             : {manifest.get('total_megabytes')} MB")
        except Exception as e:
            print(f"  Note: Manifest read warning: {e}")
    print("-" * 76)

    # Destination paths on this machine
    dest_ide = target_gemini / "antigravity-ide"
    dest_conv = dest_ide / "conversations"
    dest_brain = dest_ide / "brain"
    dest_config = target_gemini / "config"

    dest_conv.mkdir(parents=True, exist_ok=True)
    dest_brain.mkdir(parents=True, exist_ok=True)
    dest_config.mkdir(parents=True, exist_ok=True)

    src_ide = backup_root / "antigravity-ide"
    src_conv = src_ide / "conversations"
    src_brain = src_ide / "brain"
    src_config = backup_root / "config"

    files_restored = 0
    bytes_restored = 0

    # 1. Restore conversation databases
    print("\n[1/3] Restoring Conversation Databases...")
    if src_conv.exists():
        for db_file in src_conv.glob("*"):
            if db_file.is_file():
                dest_file = dest_conv / db_file.name
                if dest_file.exists() and not overwrite:
                    print(f"  - Skipped (exists): {db_file.name}")
                    continue
                shutil.copy2(db_file, dest_file)
                fsize = db_file.stat().st_size
                files_restored += 1
                bytes_restored += fsize
                print(f"  + Restored DB: {db_file.name} ({fsize / (1024*1024):.2f} MB)")
    else:
        print("  - No conversations directory found in backup.")

    # 2. Restore brain directory
    print("\n[2/3] Restoring Brain Directories (Transcripts, Artifacts, Media)...")
    if src_brain.exists():
        for cid_dir in src_brain.glob("*"):
            if cid_dir.is_dir():
                dest_cid = dest_brain / cid_dir.name
                dest_cid.mkdir(parents=True, exist_ok=True)
                for root, dirs, files in os.walk(cid_dir):
                    rel = Path(root).relative_to(cid_dir)
                    target_sub = dest_cid / rel
                    target_sub.mkdir(parents=True, exist_ok=True)
                    for file in files:
                        sfile = Path(root) / file
                        dfile = target_sub / file
                        shutil.copy2(sfile, dfile)
                        fsize = sfile.stat().st_size
                        files_restored += 1
                        bytes_restored += fsize
                cid_mb = sum(f.stat().st_size for f in dest_cid.rglob("*") if f.is_file()) / (1024*1024)
                print(f"  + Restored Brain [{cid_dir.name}]: {cid_mb:.2f} MB")
    else:
        print("  - No brain directory found in backup.")

    # 3. Restore config files
    print("\n[3/3] Restoring Configs...")
    if src_config.exists():
        for cfg_file in src_config.glob("*"):
            if cfg_file.is_file():
                dest_file = dest_config / cfg_file.name
                shutil.copy2(cfg_file, dest_file)
                files_restored += 1
                bytes_restored += cfg_file.stat().st_size
                print(f"  + Restored Config: {cfg_file.name}")

    print("\n" + "=" * 76)
    print("RESTORE COMPLETED SUCCESSFULLY!")
    print(f"Total Files Restored : {files_restored}")
    print(f"Total Size Restored  : {bytes_restored / (1024*1024):.2f} MB")
    print(f"Active Profile       : {target_gemini}")
    print("-" * 76)
    print("HOW TO OPEN RESTORED CHATS ON THIS DEVICE:")
    print("1. Launch Antigravity IDE on this machine.")
    print("2. The conversation database and transcripts are now in your active profile.")
    print("3. You can continue conversations with full past context, artifacts, and logs.")
    print("=" * 76 + "\n")
    return True


def list_chats(backup_root: Path = DEFAULT_BACKUP_DIR, source_gemini: Path = None):
    """Lists conversations found in the active Antigravity profile and backup folder."""
    if source_gemini is None:
        source_gemini = get_default_gemini_dir()

    print("\n" + "=" * 76)
    print("                 ANTIGRAVITY CONVERSATION STATUS")
    print("=" * 76)

    # Active profile
    print(f"[A] Active Profile: {source_gemini}")
    active_conv_dir = source_gemini / "antigravity-ide" / "conversations"
    active_brain_dir = source_gemini / "antigravity-ide" / "brain"
    if active_conv_dir.exists():
        dbs = list(active_conv_dir.glob("*.db"))
        if dbs:
            for db in sorted(dbs, key=lambda x: x.stat().st_mtime, reverse=True):
                mtime = datetime.fromtimestamp(db.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                size_mb = db.stat().st_size / (1024 * 1024)
                has_brain = (active_brain_dir / db.stem).exists()
                is_curr = " [ACTIVE / RECENT]" if db.stem == DEFAULT_CONV_ID else ""
                print(f"  * {db.stem}{is_curr}")
                print(f"      Size: {size_mb:.2f} MB | Modified: {mtime} | Brain folder: {'Yes' if has_brain else 'No'}")
        else:
            print("  (No conversation databases found)")
    else:
        print("  (Active conversations directory does not exist yet)")

    # Backup profile
    print(f"\n[B] Backup Folder: {backup_root}")
    bak_conv_dir = backup_root / "antigravity-ide" / "conversations"
    bak_brain_dir = backup_root / "antigravity-ide" / "brain"
    if bak_conv_dir.exists():
        bdbs = list(bak_conv_dir.glob("*.db"))
        if bdbs:
            for db in sorted(bdbs, key=lambda x: x.stat().st_mtime, reverse=True):
                mtime = datetime.fromtimestamp(db.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
                size_mb = db.stat().st_size / (1024 * 1024)
                has_brain = (bak_brain_dir / db.stem).exists()
                print(f"  * {db.stem}")
                print(f"      Size: {size_mb:.2f} MB | Modified: {mtime} | Brain folder: {'Yes' if has_brain else 'No'}")
        else:
            print("  (No backed-up conversations found)")
    else:
        print("  (No backup directory found at anti_backup/.gemini)")
    print("=" * 76 + "\n")


# ==============================================================================
# MAIN APPLICATION LAUNCHERS
# ==============================================================================

def launch_desktop():
    """Launches standalone native Desktop Application."""
    from app_desktop import launch_desktop_app
    print("[*] Launching VLC Smart Friendly Jamming Desktop App...")
    launch_desktop_app()


def launch_web_gui():
    """Opens interactive 3D Web Visualizer in browser."""
    import webbrowser
    html_path = ROOT_DIR / "index.html"
    if not html_path.exists():
        html_path = ROOT_DIR / "visualizer.html"
    print(f"[*] Opening 3D Web Visualizer: {html_path.resolve()}")
    webbrowser.open(f"file:///{html_path.resolve()}")


def run_unit_tests():
    """Executes full automated unit test suite (21 tests)."""
    print("[*] Running all 21 automated unit tests in tests/ ...")
    cmd = [sys.executable, "-m", "unittest", "discover", "tests"]
    res = subprocess.run(cmd, cwd=str(ROOT_DIR))
    if res.returncode != 0:
        print("\n[!] Some tests failed.")
        sys.exit(res.returncode)
    else:
        print("\n[+] All tests passed successfully!")


def run_all_simulations(slots: int = 2000, grid_res: int = 25, save_dir: str = "output_figures"):
    """Runs all simulation figures (Fig 5, Fig 6, Fig 7)."""
    from simulations.run_all import run_all
    run_all(save_dir=save_dir, slots=slots, grid_res=grid_res)


def run_evaluation(bob, eve, snr: float = 12.0, delta1: float = 3.5, delta2: float = 0.4):
    """Evaluates custom Bob/Eve coordinates and SNR."""
    from main import evaluate_custom_scenario
    evaluate_custom_scenario(
        bob_x=bob[0], bob_y=bob[1], bob_z=bob[2],
        eve_x=eve[0], eve_y=eve[1], eve_z=eve[2],
        snr_db=snr, delta1=delta1, delta2=delta2
    )


# ==============================================================================
# INTERACTIVE TERMINAL MENU
# ==============================================================================

def interactive_menu():
    """Presents a clean interactive menu when run without command line arguments."""
    while True:
        print("\n" + "=" * 76)
        print("    VISIBLE LIGHT COMMUNICATION: SMART FRIENDLY JAMMING SIMULATOR")
        print("          IEEE Transactions on Wireless Communications (2024)")
        print("=" * 76)
        print(" [1]  Launch Desktop App (Native Window GUI)")
        print(" [2]  Open 3D Web Visualizer (in Browser)")
        print(" [3]  Run Automated Unit Tests (21 Tests)")
        print(" [4]  Evaluate Default Nominal Scenario (Bob/Eve/SNR)")
        print(" [5]  Generate All Figures (Fig 5, Fig 6, Fig 7)")
        print(" [6]  Train DRL-FJ Agent (CNN + DND Memory)")
        print("----------------------------------------------------------------------------")
        print(" [7]  📦 Backup Chats & Brain (to anti_backup/.gemini)")
        print(" [8]  📥 Restore Chats & Brain (from anti_backup/.gemini)")
        print(" [9]  📋 List Active & Backed-Up Conversations")
        print(" [0]  Exit")
        print("=" * 76)

        try:
            choice = input("Enter option [0-9]: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            break

        if choice == "1":
            launch_desktop()
        elif choice == "2":
            launch_web_gui()
        elif choice == "3":
            run_unit_tests()
        elif choice == "4":
            run_evaluation([1.8, 1.6, 0.85], [3.2, 3.4, 0.85], snr=12.0)
        elif choice == "5":
            run_all_simulations()
        elif choice == "6":
            from vlc.config import VLCConfig
            from vlc.environment import VLCEnvironment
            from vlc.drl_fj import DRLFJAgent
            import numpy as np
            cfg = VLCConfig()
            env = VLCEnvironment(config=cfg, bob_pos=np.array([1.8, 1.6, 0.85]), eve_pos=np.array([3.2, 3.4, 0.85]))
            print("\nTraining DRL-FJ (CNN + DND) over 200 slots...")
            agent = DRLFJAgent(env, cfg)
            res = agent.train(num_slots=200)
            print(f"Training completed! Final Secrecy Rate: {res['secrecy_rate'][-1]:.4f} bps/Hz")
        elif choice == "7":
            backup_chats()
        elif choice == "8":
            restore_chats()
        elif choice == "9":
            list_chats()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("[!] Invalid option. Please enter a number between 0 and 9.")


# ==============================================================================
# CLI ENTRY POINT
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Master Runner & Chat Portability Utility for Secure VLC Simulator",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    # Core Execution Modes
    parser.add_argument("--mode", type=str, choices=["app", "gui", "test", "eval", "fig", "train", "all", "backup", "restore", "list"],
                        help="Execution mode:\n"
                             "  app:      Launch Desktop App\n"
                             "  gui:      Open 3D Web Visualizer in Browser\n"
                             "  test:     Run all 21 unit tests\n"
                             "  eval:     Evaluate custom scenario\n"
                             "  fig:      Generate paper figures\n"
                             "  train:    Train RL or DRL agent\n"
                             "  all:      Run all simulations & generate figures\n"
                             "  backup:   Backup chats & brain to anti_backup/.gemini\n"
                             "  restore:  Restore chats & brain from anti_backup/.gemini\n"
                             "  list:     List active and backed-up conversations")

    # Quick Shorthand Flags
    parser.add_argument("--app", action="store_true", help="Shorthand for --mode app")
    parser.add_argument("--gui", action="store_true", help="Shorthand for --mode gui")
    parser.add_argument("--test", action="store_true", help="Shorthand for --mode test")
    parser.add_argument("--all", action="store_true", help="Shorthand for --mode all")

    # Chat & Brain Portability Options
    parser.add_argument("--backup-chats", action="store_true", help="Backup conversation database and brain to anti_backup/.gemini")
    parser.add_argument("--restore-chats", action="store_true", help="Restore conversation database and brain from anti_backup/.gemini")
    parser.add_argument("--list-chats", action="store_true", help="List active and backed-up conversation IDs")
    parser.add_argument("--conv-id", type=str, default=DEFAULT_CONV_ID, help=f"Conversation ID to backup/restore (default: {DEFAULT_CONV_ID})")
    parser.add_argument("--backup-all", action="store_true", help="Backup all conversation databases found in profile")
    parser.add_argument("--backup-dir", type=str, default=str(DEFAULT_BACKUP_DIR), help=f"Target backup directory (default: {DEFAULT_BACKUP_DIR})")

    # Custom Simulation Parameters
    parser.add_argument("--bob", nargs=3, type=float, default=[1.8, 1.6, 0.85], metavar=("X", "Y", "Z"), help="Bob coordinates (m)")
    parser.add_argument("--eve", nargs=3, type=float, default=[3.2, 3.4, 0.85], metavar=("X", "Y", "Z"), help="Eve coordinates (m)")
    parser.add_argument("--snr", type=float, default=12.0, help="Operating SNR in dB [default: 12.0]")
    parser.add_argument("--delta1", type=float, default=3.5, help="Utility weight delta1 for BER [default: 3.5]")
    parser.add_argument("--delta2", type=float, default=0.4, help="Utility weight delta2 for Energy [default: 0.4]")
    parser.add_argument("--fig", type=str, choices=["5", "6", "7", "all"], default="all", help="Figure to generate: 5, 6, 7, all")
    parser.add_argument("--slots", type=int, default=2000, help="Time slots for Fig. 6 [default: 2000]")
    parser.add_argument("--grid_res", type=int, default=25, help="Grid resolution for Fig. 5 [default: 25]")
    parser.add_argument("--save_dir", type=str, default="output_figures", help="Directory to save figures")

    args = parser.parse_args()

    # Determine action
    b_dir = Path(args.backup_dir)

    if args.backup_chats or args.mode == "backup":
        backup_chats(conv_id=args.conv_id, backup_root=b_dir, backup_all=args.backup_all)
    elif args.restore_chats or args.mode == "restore":
        restore_chats(backup_root=b_dir)
    elif args.list_chats or args.mode == "list":
        list_chats(backup_root=b_dir)
    elif args.app or args.mode == "app":
        launch_desktop()
    elif args.gui or args.mode == "gui":
        launch_web_gui()
    elif args.test or args.mode == "test":
        run_unit_tests()
    elif args.all or args.mode == "all":
        run_all_simulations(slots=args.slots, grid_res=args.grid_res, save_dir=args.save_dir)
    elif args.mode == "eval":
        run_evaluation(args.bob, args.eve, snr=args.snr, delta1=args.delta1, delta2=args.delta2)
    elif args.mode == "fig":
        if args.fig == "all":
            run_all_simulations(slots=args.slots, grid_res=args.grid_res, save_dir=args.save_dir)
        elif args.fig == "5":
            from simulations.sim_fig5_spatial import simulate_fig5
            simulate_fig5(grid_res=args.grid_res, save_dir=args.save_dir)
        elif args.fig == "6":
            from simulations.sim_fig6_convergence import simulate_fig6
            simulate_fig6(num_slots=args.slots, save_dir=args.save_dir)
        elif args.fig == "7":
            from simulations.sim_fig7_snr import simulate_fig7
            simulate_fig7(save_dir=args.save_dir)
    elif args.mode == "train":
        from main import main as main_py_main
        main_py_main()
    else:
        # If no arguments provided, launch interactive menu
        interactive_menu()


if __name__ == "__main__":
    main()
