@echo off
title Trinh Tai Video TikTok - Facebook Reels
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
echo       TRINH TAI VIDEO TIKTOK / FACEBOOK REELS / YOUTUBE
echo             (Chat luong cao nhat - Khong logo)
echo ================================================================
echo.
echo Ban co the:
echo  1. Dan truc tiep 1 link video / link kenh TikTok / Reel FB
echo  2. Hoac nhap: links.txt (neu ban co 1 danh sach nhieu link)
echo.
set /p "TARGET_URL=Nhap link hoac file: "
if "%TARGET_URL%"=="" (
    echo Ban chua nhap link!
    pause
    exit /b
)
echo.
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

.\.venv\Scripts\python.exe download_mxh.py "%TARGET_URL%"
echo.
pause
