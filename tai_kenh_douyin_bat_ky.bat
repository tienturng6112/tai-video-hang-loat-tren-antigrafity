@echo off
title Trinh Tai Kenh Douyin Tu Chon
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
