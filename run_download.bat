@echo off
title Douyin Channel Downloader - 1080p No Watermark
cd /d "%~dp0"
cls

if not exist ".venv\Scripts\python.exe" (
    echo [THONG BAO] Chua tim thay thu muc .venv!
    echo Dang tu dong chay cai dat moi truong...
    call CAI_DAT_MAY_MOI.bat
)

if not exist ".venv\Scripts\python.exe" (
    echo [LOI] Chua khoi tao duoc moi truong .venv!
    pause
    exit /b 1
)

echo =======================================================
echo   TRINH TAI TOAN BO VIDEO DOUYIN 1080P/4K KHONG LOGO
echo   Kenh: Dao Dan Mo Mo (100 video)
echo =======================================================
echo.
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

.\.venv\Scripts\python.exe download_channel.py %*
echo.
pause
