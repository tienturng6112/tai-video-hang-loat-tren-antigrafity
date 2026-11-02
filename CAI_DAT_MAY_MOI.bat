@echo off
title Cai Dat Moi Truong Cho May Moi
cd /d "%~dp0"
cls
echo ================================================================
echo          CAI DAT MOI TRUONG DU AN CHO MAY MOI
echo ================================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [LOI] May tinh cua ban chua cai dat Python!
    echo Vui long cai Python tu: https://www.python.org/downloads/
    echo LUU Y: Nho tich chon vao o [x] "Add python.exe to PATH" khi cai dat!
    echo.
    pause
    exit /b 1
)

echo [1/3] Dang khoi tao moi truong ao (.venv)...
if not exist ".venv\Scripts\python.exe" (
    python -m venv .venv
) else (
    echo .venv da ton tai, bo qua buoc tao.
)

echo.
echo [2/3] Dang cai dat cac thu vien can thiet...
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo [3/3] Dang tai trinh duyet Chromium cho Playwright...
.\.venv\Scripts\python.exe -m playwright install chromium

echo.
echo ================================================================
echo        DA CAI DAT THANH CONG VA SAN SANG SU DUNG!
echo ================================================================
echo.
echo Cac buoc tiep theo:
echo  1. Nhap dup chuot: run_login.bat (quet ma QR dang nhap Douyin)
echo  2. Nhap dup chuot: tai_kenh_douyin_bat_ky.bat (tai video Douyin)
echo  3. Nhap dup chuot: tai_video_facebook_tiktok.bat (tai TikTok/FB)
echo.
pause
