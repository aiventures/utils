
@echo off
rem p.bat create a prompt 
rem set unicode code page to display special characters
chcp 65001

:: Count number of arguments
set NUM_ARGS=0
for %%x in (%*) do Set /A NUM_ARGS+=1

call colors.bat
call myenv.bat
echo %COL_GREY_DARK%### RUN %~f0%C_0%

set "py_program=%MY_P_UTILS_SCRIPTS%\prompt.py"

rem create the prompt string and put it into a temporary file
python "%py_program%"
rem read the command from the file 
set /p cmd_prompt=< "%MY_F_MYENV_PROMPT%"
rem set the prompt
%cmd_prompt%
goto end

:end
set NUM_ARGS=
set cmd_prompt=
set py_program=
echo %C_0%


