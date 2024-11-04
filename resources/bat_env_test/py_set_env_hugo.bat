@echo off
rem Sample pattern to set environment frompython
rem you can verify this is not working ... 
rem so the only way to create from os from python to be used in 
rem python is to export env vars as script and include this 
rem in batch script
rem COMMAND_LINE => ENV => PYTHON ENV (works)
rem PYTHON ENV => ENV => COMMAND_LINE (not working)
rem PYTHON ENV => export to ENV BAT FILE => CALL ENV BAT (working)
call clear_env_hugo.bat
python set_env_hugo.py
call read_env_hugo.bat

