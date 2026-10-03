@echo off
setlocal
pushd "%~dp0"
where py >nul 2>&1
if errorlevel 1 goto python
py -3 tools\build.py %*
goto done
:python
python tools\build.py %*
:done
set "DENSHA_BUILD_RESULT=%ERRORLEVEL%"
popd
exit /b %DENSHA_BUILD_RESULT%
