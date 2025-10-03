@echo off
rem myenv.bat setting local env variables with MY_ prefix 
rem working venv with additional Libraries
call colors.bat
echo %COL_GREY_DARK%### RUN %~f0%C_0%
rem working path set accordingly
set "MY_P_WORK=C:\<Path to a working directory>"
rem path to utils repo
set "MY_P_UTILS=%MY_P_WORK%\<path to>\utils"
rem path to utils bat scripts 
set "MY_P_UTILS_BAT=%MY_P_UTILS%\bat"
rem path to utils python scripts 
set "MY_P_UTILS_SCRIPTS=%MY_P_UTILS%\src\scripts"
rem path to utils config folder
set "MY_P_UTILS_CONFIG=%MY_P_UTILS%\src\config"
rem path containing venvs
set "MY_P_VENV=%MY_P_WORK%\VENV"
rem path containing work venv 
set "MY_P_VENV_WORK=%MY_P_VENV%\WORK"
rem path to store locally buffered environment variables 
rem so as to store them from python to command line
set "MY_P_MYENV=%MY_P_WORK%\MYENV"
rem VSCODE Project Location
set "MY_P_VSCODE_PROJECTS=%MY_P_WORK%\vscode_workspaces"
rem My Default VSCOE Project 
set "MY_F_VSCODE_PROJECT=%MY_P_VSCODE_PROJECTS%\utils.code-workspace"
rem BAT File containing MYENV Variables (this file)
set "MY_F_MYENV_BAT=%MY_P_UTILS_BAT%\myenv.bat"
rem PY File containing MYENV Variables (converted using convert_bat_env_to_python.py)
set "MY_F_MYENV_PY=%MY_P_UTILS_CONFIG%\myenv.py"
rem BAT File containing color codes 
set "MY_F_COLORS_BAT=%MY_P_UTILS_BAT%\colors.bat"
rem PY File containing Color Variables (converted using convert_bat_colors_to_python.py)
set "MY_F_COLORS_PY=%MY_P_UTILS_CONFIG%\colors.py"
