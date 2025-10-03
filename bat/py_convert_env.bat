
@echo off
rem py_convert_env.bat converts env from bat to python using convert_bat_env_to_python.py

call colors.bat
call myenv.bat

set "py_program=%MY_P_UTILS_SCRIPTS%\convert_bat_env_to_python.py"
echo %C_T%### RUN %C_PROG%%~f0%C_PY%
echo %C_T%Run Python Program %C_PY%%py_program%%C_0%
echo %C_PY%[%MY_F_MYENV_BAT%] ^> [%MY_F_MYENV_PY%] %C_PY%

:: Count number of arguments
set NUM_ARGS=0
for %%x in (%*) do Set /A NUM_ARGS+=1
python "%py_program%" --input "%MY_F_MYENV_BAT%" --output "%MY_F_MYENV_PY%"
echo %C_O%
cat %MY_F_MYENV_PY%
goto end

:end
echo %C_0%


