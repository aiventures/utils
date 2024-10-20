@echo off
rem set_vars.bat: setting environment variables
__COMMENT__
rem create an ESC Sequence
rem https://en.wikipedia.org/wiki/ANSI_escape_code
rem https://ss64.com/nt/syntax-ansi.html
for /F %%a in ('echo prompt $E ^| cmd') do set "ESC=%%a"

set SHOWENV=0
__SET__
if /I "%SHOWENV%" EQU "1" (goto show_vars ) ELSE ( goto end )
:show_vars
__ECHO__
:end