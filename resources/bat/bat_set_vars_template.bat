@echo off
rem set_vars.bat: setting environment variables
__COMMENT__
set SHOWENV=0
if /I "%SHOWENV%" EQU "1" (goto show_vars ) ELSE ( goto end )
__SET__
:show_vars
__ECHO__
:end