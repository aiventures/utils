
@echo off
rem bat2py.bat synchs variables and colors from bat to python
set pwd=%CD%

call colors.bat
call myenv.bat

echo %C_T%### RUN %C_PROG%%~f0%C_PY%

:: Count number of arguments
set NUM_ARGS=0
for %%x in (%*) do Set /A NUM_ARGS+=1
call py_convert_env.bat
call py_convert_colors.bat
goto end

:end
set NUM_ARGS=
set pwd=

