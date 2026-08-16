@echo off
setlocal
cd /d "%~dp0"
set "PYTHON=python"

echo Installing build requirements if needed...
%PYTHON% -m pip install -r requirements-build.txt
if errorlevel 1 goto :error

echo Looking for FFmpeg to include with the app...
if not defined FFMPEG_PATH (
    for /f "delims=" %%F in ('where ffmpeg 2^>nul') do if not defined FFMPEG_PATH set "FFMPEG_PATH=%%F"
)
if defined FFMPEG_PATH (
    echo Using FFmpeg at: %FFMPEG_PATH%
) else (
    echo FFmpeg was not found on PATH; Video_Downloader.spec will fall back to its
    echo built-in default path. Set FFMPEG_PATH first if that fallback is wrong
    echo on this machine.
)

echo Building Video Downloader (via Video_Downloader.spec)...
REM Built from the same .spec file as build_exe.bat, so both scripts bundle
REM FFmpeg and package options identically instead of drifting apart.
%PYTHON% -m PyInstaller --noconfirm --clean "Video_Downloader.spec"
if errorlevel 1 goto :error

set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=C:\Program Files\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" goto :portable

echo Creating Windows installer...
"%ISCC%" installer.iss
if errorlevel 1 goto :error
echo.
echo Done. Send the installer in the output folder to your friends.
pause
exit /b 0

:portable
echo.
echo The portable app is ready in the dist folder.
echo To make a normal installer too, install Inno Setup 6 and run this file again.
pause
exit /b 0

:error
echo.
echo The build did not finish. Copy this window's message and send it to me.
pause
exit /b 1
