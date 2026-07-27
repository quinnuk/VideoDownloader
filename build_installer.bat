@echo off
setlocal
cd /d "%~dp0"
set "PYTHON=python"

echo Installing the packaging tool if needed...
%PYTHON% -m pip install --upgrade pyinstaller
if errorlevel 1 goto :error

echo Looking for FFmpeg to include with the app...
set "FFMPEG="
for /f "delims=" %%F in ('where ffmpeg 2^>nul') do if not defined FFMPEG set "FFMPEG=%%F"

echo Building Video Downloader...
if defined FFMPEG (
    %PYTHON% -m PyInstaller --noconfirm --clean --windowed --onefile --name "Video Downloader" --icon "video_downloader_icon.ico" --collect-all customtkinter --collect-all yt_dlp --add-binary "%FFMPEG%;." main.py
) else (
    echo FFmpeg was not found. The app will build, but MP3 conversion and some video downloads will require FFmpeg on the other PC.
    %PYTHON% -m PyInstaller --noconfirm --clean --windowed --onefile --name "Video Downloader" --icon "video_downloader_icon.ico" --collect-all customtkinter --collect-all yt_dlp main.py
)
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
