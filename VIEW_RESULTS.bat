@echo off
title Opening OWC Simulation Results and Figures
cd /d "%~dp0"
echo ========================================================
echo  Opening Generated Figures and Documentation
echo ========================================================
echo.
echo Opening figures directory in Windows Explorer...
start "" "figures"
echo.
echo Opening Figure 1 (Convergence Curves)...
start "" "figures\fig1_convergence_curves.png"
echo.
echo Opening Figure 2 (Spatial Heatmaps)...
start "" "figures\fig2_spatial_secrecy_heatmaps.png"
echo.
echo Opening Figure 5 (LoS Blockage Resilience)...
start "" "figures\fig5_blockage_resilience.png"
echo.
echo Opening Figure 6 (3D Indoor System Architecture)...
start "" "figures\fig6_3d_indoor_setup.png"
echo.
echo Opening Research Report...
start "" "RESEARCH_REPORT.md"
echo.
echo Done! All graphs and files are opened on your screen.
timeout /t 5
