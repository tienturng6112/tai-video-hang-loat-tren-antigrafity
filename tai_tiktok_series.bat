@echo off
title Trinh Tai Tron Bo Phim Ngan - Series TikTok
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
echo       TRINH TAI TRON BO PHIM NGAN / SERIES TIKTOK
echo             (Chat luong cao nhat - Khong logo)
echo ================================================================
echo.
echo Ban chi can dan link 1 tap bat ky cua phim (VD tap 1 hoac tap bat ky):
echo He thong se tu dong quet va tai tron bo tat ca cac tap!
echo.
set /p "TARGET_URL=Nhap link tap phim TikTok: "
if "%TARGET_URL%"=="" (
    echo Ban chua nhap link!
    pause
    exit /b
)
echo.
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

.\.venv\Scripts\python.exe tai_tiktok_series.py "%TARGET_URL%"
echo.
pause

