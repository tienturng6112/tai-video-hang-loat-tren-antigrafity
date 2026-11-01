@echo off
title Douyin Channel Downloader - 1080p No Watermark
chcp 65001 >nul
cd /d "%~dp0"
cls

if not exist ".\.venv\Scripts\python.exe" (
    echo ================================================================
    echo [THÔNG BÁO] Máy tính này chưa được cài đặt môi trường dự án!
    echo Đang tự động chuyển sang cài đặt tự động...
    echo ================================================================
    echo.
    call CAI_DAT_MAY_MOI.bat
    if not exist ".\.venv\Scripts\python.exe" (
        echo Cài đặt chưa thành công. Vui lòng kiểm tra lại Python!
        pause
        exit /b
    )
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
