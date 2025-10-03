
@echo off
rem color_list.bat Show ANSI Color list (using /config/ansi_color_codes.py)
call colors.bat
call myenv.bat

set pwd=%CD%
set "py_program=%MY_P_UTILS_CONFIG%\ansi_color_codes.py"
echo %C_T%### RUN %C_PROG%%~f0%C_PY%
echo %C_T%Run Python Program %C_PY%%py_program%%C_0%
echo %C_PY%[%MY_F_MYENV_BAT%] ^> [%MY_F_MYENV_PY%] %C_PY%

:: Count number of arguments
set NUM_ARGS=0
for %%x in (%*) do Set /A NUM_ARGS+=1
python "%py_program%" 
set "py_program=%MY_P_UTILS_CONFIG%\colors.py"
python "%py_program%" 
goto end

:end
set NUM_ARGS=
set pwd=
set py_program=
echo %C_0%


