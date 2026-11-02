@echo off
title Trinh Tai Video TikTok - Facebook Reels
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
