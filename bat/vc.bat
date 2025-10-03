
@echo off
rem vc.bat opend default vscode vs code project defined in MY_F_VSCODE_PROJECT

call colors.bat
call myenv.bat

echo %C_T%### RUN %C_PROG%%~f0%C_PY%

:: Count number of arguments
set NUM_ARGS=0
for %%x in (%*) do Set /A NUM_ARGS+=1
echo %C_T%OPEN VSCODE: %C_S%[%MY_F_VSCODE_PROJECT%]%C_0%
code "%MY_F_VSCODE_PROJECT%"


