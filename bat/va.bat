
@echo off
rem va.bat [venv] venv activate VENV in MY_P_VENV/VENV (Default is MY_P_VENV_WORK)

@REM In windows command line, assume there is a venv located by env variable p_venv. write a bat script that allows to pass a variable venv_name. 
@REM do the follwoinga actions: 
@REM - count number of passed arguments to bat file in variable NUM_ARGS
@REM - if the path p_venv/venv_name is a valid path, activate venv by calling %p_venv%/venv_name/Scripts/activate.bat 
@REM - if nothing is passed, activate a default venv located in %p_venv%/venv_work
call colors.bat
call myenv.bat

echo %C_T%### RUN %C_PROG%%~f0%C_PY%

:: Count number of arguments
set NUM_ARGS=0
for %%x in (%*) do Set /A NUM_ARGS+=1
:: Check if any argument was passed
if "%~1"=="" (
    echo No venv_name provided. Activating default: %C_P%%MY_P_VENV_WORK%
    :: Check if a venv is already activated
    if defined VIRTUAL_ENV (
        echo %C_PY%Deactivating currently active venv: %C_P%%VIRTUAL_ENV%
        call deactivate
    )        
    call "%MY_P_VENV_WORK%\Scripts\activate.bat"
    echo %C_0%
    goto :eof
)

:: Set venv_name from first argument
set "venv_name=%~1"
set "venv_path=%MY_P_VENV%\%venv_name%"

:: Check if the venv path exists
if exist "%venv_path%\Scripts\activate.bat" (
    :: Check if a venv is already activated
    if defined VIRTUAL_ENV (
        echo %C_PY%Deactivating currently active venv: %C_P%%VIRTUAL_ENV%
        call deactivate
    )    
    echo %C_PY%Activating virtual environment: %C_P%%venv_path%
    call "%venv_path%\Scripts\activate.bat"
) else (
    echo %C_E%ERROR: Virtual environment not found at %C_P%%venv_path%
)
echo %C_0%