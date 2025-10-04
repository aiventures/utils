@echo off
rem _template_py_args.bat use for copy & paste to call python scripts with multiple args 
:: Count number of arguments
set pwd=%CD%
set "py_program=%MY_P_UTILS_SCRIPTS%\colors.py"
set num_args=0
for %%x in (%*) do set /A num_args+=1
if %num_args% equ 0 goto run_without_args

rem show info on run programs
:show_info
echo %C_T%### RUN %C_PROG%%~f0%C_PY%
echo %C_T%Run Python Program %C_PY%%py_program%with params%C_H% [%*]%C_0%

:continue
call colors.bat %*
call myenv.bat %*

rem handle up to 4 goal-based arguments
if not "%~4"=="" goto args4
if not "%~3"=="" goto args3
if not "%~2"=="" goto args2
if not "%~1"=="" goto args1

rem run without commands 
:run_without_args
echo no args
python "%py_program%" 
goto end

:args1
rem your code for arg1 here
echo args1
rem python "%py_program%" --p1 "%MY_F_MYENV_BAT%" --output "%MY_F_MYENV_PY%"
goto end

:args2
rem your code for arg2 here
echo args2
goto end

:args3
rem your code for arg3 here
echo args3
goto end

:args4
rem your code for arg4 here
echo args4
goto end

:end
set num_args=
set pwd=
set py_program=
echo %C_0%
