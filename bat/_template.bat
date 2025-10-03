
@echo off
rem _template.bat use for copy & paste 
set pwd=%CD%

call colors.bat %*
call myenv.bat %*

:: Count number of arguments
set NUM_ARGS=0
for %%x in (%*) do Set /A NUM_ARGS+=1
if %NUM_ARGS% equ 0 goto continue
echo %C_T%### RUN %C_PROG%%~f0%C_PY%
:continue
goto end

:end
set NUM_ARGS=
set pwd=

