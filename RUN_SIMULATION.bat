@echo off
title Running OWC PLS Simulation Suite
cd /d "%~dp0"
echo ======================================================================
echo  Optical Wireless Communication (OWC) Physical Layer Security
echo  Deep Reinforcement Learning (DRL) with Optical RIS and Jamming
echo ======================================================================
echo.
echo Running Quick Simulation (300 Time Slots) to verify results...
python -u run_simulation.py --quick
echo.
echo ======================================================================
echo Simulation Finished! Opening generated plots now...
echo ======================================================================
start "" "figures\fig1_convergence_curves.png"
start "" "figures\fig2_spatial_secrecy_heatmaps.png"
start "" "figures\fig5_blockage_resilience.png"
start "" "figures"
echo.
echo Press any key to close this console window.
pause
