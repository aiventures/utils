
@echo off
rem _template.bat use for copy & paste to call python scripts 
:: Count number of arguments
set pwd=%CD%
set "py_program=%MY_P_UTILS_SCRIPTS%\convert_bat_env_to_python.py"
set NUM_ARGS=0
for %%x in (%*) do Set /A NUM_ARGS+=1
if %NUM_ARGS% equ 0 goto continue
rem show info on run programs
:show_info
echo %C_T%### RUN %C_PROG%%~f0%C_PY%
echo %C_T%Run Python Program %C_PY%%py_program%%C_0%
echo %C_PY%[%MY_F_MYENV_BAT%] ^> [%MY_F_MYENV_PY%] %C_PY%

:continue
call colors.bat %*
call myenv.bat %*

python "%py_program%" --input "%MY_F_MYENV_BAT%" --output "%MY_F_MYENV_PY%"
goto end

:end
set NUM_ARGS=
set pwd=
set py_program=
echo %C_0%


