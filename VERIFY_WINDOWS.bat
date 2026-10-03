@echo off
setlocal
where py >nul 2>&1
if errorlevel 1 goto python
py -3 "%~dp0tools\check_release.py" %*
goto done
:python
python "%~dp0tools\check_release.py" %*
:done
exit /b %ERRORLEVEL%
