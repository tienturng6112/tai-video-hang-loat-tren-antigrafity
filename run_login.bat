@echo off
title Dang Nhap Douyin
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
echo   ĐĂNG NHẬP DOUYIN ĐỂ MỞ KHÓA TẢI HẾT TẤT CẢ VIDEO
echo =======================================================
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

.\.venv\Scripts\python.exe login_helper.py
pause
