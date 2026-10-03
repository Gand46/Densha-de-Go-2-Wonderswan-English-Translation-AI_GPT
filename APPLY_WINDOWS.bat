@echo off
setlocal
where py >nul 2>&1
if errorlevel 1 goto python
py -3 "%~dp0tools\apply_patch.py" %*
goto done
:python
python "%~dp0tools\apply_patch.py" %*
:done
exit /b %ERRORLEVEL%
