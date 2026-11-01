@echo off
title Trinh Tai Kenh Douyin Tu Chon
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

echo ================================================================
echo        TRINH TAI TOAN BO VIDEO TU BAT KY KENH DOUYIN
echo       (Tu dong xoa logo / watermark - 1080p va 4K goc)
echo ================================================================
echo.
set /p "DOUYIN_URL=Dan link kenh Douyin (VD: https://www.douyin.com/user/...): "
if "%DOUYIN_URL%"=="" (
    echo Ban chua dan link!
    pause
    exit /b
)
echo.
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

.\.venv\Scripts\python.exe download_douyin_universal.py "%DOUYIN_URL%"
echo.
pause
