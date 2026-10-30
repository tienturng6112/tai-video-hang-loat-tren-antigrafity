@echo off
title Trinh Tai Video TikTok - Facebook Reels
chcp 65001 >nul
cls
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

