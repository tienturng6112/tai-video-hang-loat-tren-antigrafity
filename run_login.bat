@echo off
title Dang Nhap Douyin
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
echo   DANG NHAP DOUYIN DE MO KHOA TAI HET TAT CA VIDEO
echo =======================================================
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

.\.venv\Scripts\python.exe login_helper.py
pause
