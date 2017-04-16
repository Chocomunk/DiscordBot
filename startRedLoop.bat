@echo off
chcp 65001
echo.
pushd %~dp0

:loopstart

::Attempts to start py launcher without relying on PATH
%SYSTEMROOT%\py.exe --version > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 GOTO attempt
%SYSTEMROOT%\py.exe -3.5 red.py
timeout 3
GOTO loopstart

::Attempts to start py launcher by relying on PATH
:attempt
python3 --version > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 GOTO lastattempt
python3 red.py
timeout 3
GOTO loopstart

::As a last resort, attempts to start whatever Python there is
:lastattempt
python3.exe --version > NUL 2>&1
IF %ERRORLEVEL% NEQ 0 GOTO message
python3.exe red.py
timeout 3
GOTO loopstart

:message
echo Couldn't find a valid Python 3.5 installation. Python needs to be installed and available in the PATH environment 
echo variable. 
echo https://twentysix26.github.io/Red-Docs/red_win_requirements/#software
PAUSE

:end