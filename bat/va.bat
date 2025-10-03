
@echo off
rem va.bat [venv] venv activate VENV in MY_P_VENV/VENV (Default is MY_P_VENV_WORK)

@REM In windows command line, assume there is a venv located by env variable p_venv. write a bat script that allows to pass a variable venv_name. 
@REM do the follwoinga actions: 
@REM - count number of passed arguments to bat file in variable NUM_ARGS
@REM - if the path p_venv/venv_name is a valid path, activate venv by calling %p_venv%/venv_name/Scripts/activate.bat 
@REM - if nothing is passed, activate a default venv located in %p_venv%/venv_work
@echo off
rem va.bat [venv_name] - activates VENV from %MY_P_VENV%, or defaults to %MY_P_VENV_WORK%

call colors.bat
call myenv.bat

echo %C_T%### RUN %C_PROG%%~f0%C_PY%

:: Count arguments
set NUM_ARGS=0
for %%x in (%*) do set /A NUM_ARGS+=1

:: Default setup if no argument is passed
if "%~1"=="" (
    echo No venv_name provided. Activating default: %C_P%%MY_P_VENV_WORK%
    if defined VIRTUAL_ENV (
        echo %C_PY%Deactivating current venv: %C_P%%VIRTUAL_ENV%
        call deactivate
        call p.bat
    )
    call "%MY_P_VENV_WORK%\Scripts\activate.bat"
    call p.bat
    echo %C_0%
    goto :eof
)

:: Use first argument as venv_name
set "venv_name=%~1"
set "venv_path=%MY_P_VENV%\%venv_name%"

:: Check existence and activate venv
if exist "%venv_path%\Scripts\activate.bat" (
    if defined VIRTUAL_ENV (
        echo %C_PY%Deactivating current venv: %C_P%%VIRTUAL_ENV%
        call deactivate
        call p.bat
    )
    echo %C_PY%Activating virtual environment: %C_P%%venv_path%
    call "%venv_path%\Scripts\activate.bat"
    call p.bat
) else (
    echo %C_E%ERROR: Virtual environment not found at %C_P%%venv_path%
)
echo %C_0%