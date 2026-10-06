"""
Graphical User Interface (GUI) Dashboard for OWC Physical Layer Security.
Provides an interactive desktop application for:
- Running simulations interactively with live progress logs
- Viewing all 6 publication figures directly inside the application
- Switching between tabs to inspect convergence, spatial heatmaps, SNR, RIS scaling, and blockage resilience
- Opening output directories and research documentation with one click
"""

import os
import sys
import threading
import subprocess
import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk

# Base directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FIGURES_DIR = os.path.join(BASE_DIR, "figures")
RESULTS_DIR = os.path.join(BASE_DIR, "results")
REPORT_FILE = os.path.join(BASE_DIR, "RESEARCH_REPORT.md")

class PLSDashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DRL-Based Physical Layer Security of OWC Systems - Simulation Testbed")
        self.root.geometry("1100x820")
        self.root.minsize(900, 680)

        # Configure style
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        # Color palette
        self.bg_color = "#1e1e2e"
        self.card_bg = "#2b2b3d"
        self.accent_color = "#00adb5"
        self.text_color = "#eeeeee"
        self.success_color = "#00e676"

        self.root.configure(bg=self.bg_color)

        self._build_header()
        self._build_control_bar()
        self._build_main_display()
        self._build_status_log()

        # Load initial figures if available
        self.refresh_figures()

    def _build_header(self):
        header_frame = tk.Frame(self.root, bg=self.card_bg, pady=12, padx=16)
        header_frame.pack(fill=tk.X, side=tk.TOP)

        title_label = tk.Label(
            header_frame,
            text="Deep Reinforcement Learning-Based Physical Layer Security of OWC Systems",
            font=("Helvetica", 16, "bold"),
            bg=self.card_bg,
            fg="#00d2d3"
        )
        title_label.pack(anchor="w")

        subtitle_label = tk.Label(
            header_frame,
            text="Virtual Simulation Testbed: Optical Reconfigurable Intelligent Surface (O-RIS) + Friendly Jamming (FJ)",
            font=("Helvetica", 10),
            bg=self.card_bg,
            fg="#c8d6e5"
        )
        subtitle_label.pack(anchor="w", pady=(2, 0))

    def _build_control_bar(self):
        ctrl_frame = tk.Frame(self.root, bg=self.bg_color, pady=10, padx=16)
        ctrl_frame.pack(fill=tk.X, side=tk.TOP)

        # Quick simulation button
        self.btn_quick = tk.Button(
            ctrl_frame,
            text="▶ Run Quick Test (300 Slots)",
            font=("Helvetica", 10, "bold"),
            bg="#0984e3",
            fg="white",
            activebackground="#74b9ff",
            relief=tk.FLAT,
            padx=12,
            pady=6,
            command=lambda: self.start_simulation(quick=True)
        )
        self.btn_quick.pack(side=tk.LEFT, padx=(0, 10))

        # Full simulation button
        self.btn_full = tk.Button(
            ctrl_frame,
            text="🚀 Run Full Simulation (1500 Slots)",
            font=("Helvetica", 10, "bold"),
            bg="#6c5ce7",
            fg="white",
            activebackground="#a29bfe",
            relief=tk.FLAT,
            padx=12,
            pady=6,
            command=lambda: self.start_simulation(quick=False)
        )
        self.btn_full.pack(side=tk.LEFT, padx=(0, 10))

        # Open figures folder
        self.btn_open_figs = tk.Button(
            ctrl_frame,
            text="📁 Open Figures Folder",
            font=("Helvetica", 10),
            bg="#2d3436",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=6,
            command=self.open_figures_folder
        )
        self.btn_open_figs.pack(side=tk.LEFT, padx=(0, 10))

        # Open Research Report
        self.btn_report = tk.Button(
            ctrl_frame,
            text="📄 Open Research Report",
            font=("Helvetica", 10),
            bg="#2d3436",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=6,
            command=self.open_report
        )
        self.btn_report.pack(side=tk.LEFT, padx=(0, 10))

        # Launch Web Virtual Lab
        self.btn_web_lab = tk.Button(
            ctrl_frame,
            text="🌐 3D Interactive Web Lab",
            font=("Helvetica", 10, "bold"),
            bg="#00b894",
            fg="white",
            activebackground="#55efc4",
            relief=tk.FLAT,
            padx=10,
            pady=6,
            command=self.open_web_lab
        )
        self.btn_web_lab.pack(side=tk.LEFT, padx=(0, 10))

        # Reload figures button
        self.btn_refresh = tk.Button(
            ctrl_frame,
            text="🔄 Refresh Graphs",
            font=("Helvetica", 10),
            bg="#00b894",
            fg="white",
            relief=tk.FLAT,
            padx=10,
            pady=6,
            command=self.refresh_figures
        )
        self.btn_refresh.pack(side=tk.RIGHT)

    def _build_main_display(self):
        self.notebook_frame = tk.Frame(self.root, bg=self.bg_color, padx=16, pady=4)
        self.notebook_frame.pack(fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(self.notebook_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        self.tabs = {}
        self.image_labels = {}
        self.img_refs = {}

        tab_info = [
            ("Fig 1: Convergence", "fig1_convergence_curves.png"),
            ("Fig 2: 2D Spatial Heatmaps", "fig2_spatial_secrecy_heatmaps.png"),
            ("Fig 3: Optical SNR (4-20 dB)", "fig3_snr_performance.png"),
            ("Fig 4: RIS Element Scaling", "fig4_ris_elements_scaling.png"),
            ("Fig 5: LoS Blockage Resilience", "fig5_blockage_resilience.png"),
            ("Fig 6: 3D System Architecture", "fig6_3d_indoor_setup.png"),
        ]

        for title, fname in tab_info:
            tab = tk.Frame(self.notebook, bg="#11111b")
            self.notebook.add(tab, text=f" {title} ")
            
            lbl = tk.Label(tab, bg="#11111b", text="Graph not generated yet. Click 'Run Quick Test' above.", fg="#888888", font=("Helvetica", 12))
            lbl.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            self.tabs[fname] = tab
            self.image_labels[fname] = lbl

    def _build_status_log(self):
        log_frame = tk.Frame(self.root, bg=self.card_bg, padx=16, pady=8)
        log_frame.pack(fill=tk.X, side=tk.BOTTOM)

        top_row = tk.Frame(log_frame, bg=self.card_bg)
        top_row.pack(fill=tk.X)

        self.status_label = tk.Label(
            top_row,
            text="Status: Ready. All 6 publication figures are ready to view.",
            font=("Helvetica", 9, "bold"),
            bg=self.card_bg,
            fg="#00e676"
        )
        self.status_label.pack(side=tk.LEFT)

        self.progress_bar = ttk.Progressbar(top_row, mode="indeterminate", length=200)
        self.progress_bar.pack(side=tk.RIGHT)

        # Log text box
        self.log_text = tk.Text(log_frame, height=4, bg="#11111b", fg="#00ffcc", font=("Consolas", 8), relief=tk.FLAT)
        self.log_text.pack(fill=tk.X, pady=(6, 0))
        self.log_text.insert(tk.END, "Ready. Select an action above to run simulations or inspect generated plots.\n")
        self.log_text.see(tk.END)

    def log(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)

    def refresh_figures(self):
        """Loads and resizes PNG figures onto their respective tabs."""
        for fname, lbl in self.image_labels.items():
            path = os.path.join(FIGURES_DIR, fname)
            if os.path.exists(path):
                try:
                    img = Image.open(path)
                    # Resize to fit window while preserving aspect ratio
                    max_w = 1000
                    max_h = 560
                    img.thumbnail((max_w, max_h), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    
                    lbl.configure(image=photo, text="")
                    self.img_refs[fname] = photo  # Keep reference to prevent GC
                except Exception as e:
                    lbl.configure(text=f"Error displaying image: {e}")
            else:
                lbl.configure(text=f"File {fname} not found in figures/. Click Run Simulation above.")

    def start_simulation(self, quick=True):
        self.btn_quick.config(state=tk.DISABLED)
        self.btn_full.config(state=tk.DISABLED)
        self.progress_bar.start(10)
        
        mode = "Quick (300 Slots)" if quick else "Full (1500 Slots)"
        self.status_label.config(text=f"Status: Running {mode} Simulation in background...", fg="#f39c12")
        self.log(f"\n[INFO] Starting {mode} simulation...")

        thread = threading.Thread(target=self._run_sim_worker, args=(quick,))
        thread.daemon = True
        thread.start()

    def _run_sim_worker(self, quick):
        slots_arg = ["--quick"] if quick else ["--slots", "1500"]
        cmd = [sys.executable, "-u", os.path.join(BASE_DIR, "run_simulation.py")] + slots_arg

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=BASE_DIR
            )

            for line in iter(process.stdout.readline, ""):
                if line:
                    clean_line = line.strip()
                    self.root.after(0, self.log, clean_line)

            process.stdout.close()
            process.wait()

            self.root.after(0, self._simulation_finished, process.returncode)
        except Exception as e:
            self.root.after(0, self.log, f"[ERROR] Simulation failed: {e}")
            self.root.after(0, self._simulation_finished, -1)

    def _simulation_finished(self, returncode):
        self.progress_bar.stop()
        self.btn_quick.config(state=tk.NORMAL)
        self.btn_full.config(state=tk.NORMAL)

        if returncode == 0:
            self.status_label.config(text="Status: Simulation Completed Successfully! Graphs updated.", fg="#00e676")
            self.log("[SUCCESS] Simulation completed and all figures updated.")
            self.refresh_figures()
            messagebox.showinfo("Success", "Simulation finished! All graphs have been updated in the tabs.")
        else:
            self.status_label.config(text="Status: Simulation finished with errors. See log.", fg="#ff4757")
            messagebox.showerror("Error", "Simulation encountered an error. Check log for details.")

    def open_figures_folder(self):
        try:
            if sys.platform == "win32":
                os.startfile(FIGURES_DIR)
            else:
                subprocess.Popen(["xdg-open", FIGURES_DIR])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open directory: {e}")

    def open_web_lab(self):
        try:
            web_lab_path = os.path.join(BASE_DIR, "virtual_lab.html")
            if sys.platform == "win32":
                os.startfile(web_lab_path)
            else:
                subprocess.Popen(["xdg-open", web_lab_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open virtual lab: {e}")

    def open_report(self):
        try:
            if sys.platform == "win32":
                os.startfile(REPORT_FILE)
            else:
                subprocess.Popen(["xdg-open", REPORT_FILE])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open report: {e}")

def main():
    root = tk.Tk()
    app = PLSDashboardApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
