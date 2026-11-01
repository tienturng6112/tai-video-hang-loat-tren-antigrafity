@echo off
title Cai Dat Moi Truong Cho May Moi
chcp 65001 >nul
cd /d "%~dp0"
cls
echo ================================================================
echo          TỰ ĐỘNG CÀI ĐẶT MÔI TRƯỜNG DỰ ÁN CHO MÁY MỚI
echo ================================================================
echo.

:: 1. Kiem tra Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [LỖI] Máy tính của bạn chưa cài Python!
    echo Vui lòng tải và cài đặt Python từ: https://www.python.org/downloads/
    echo LƯU Ý: Nhớ tích chọn ô [x] "Add python.exe to PATH" khi cài!
    echo.
    pause
    exit /b
)

echo [1/3] Đang khởi tạo môi trường ảo Python (.venv)...
if not exist ".venv" (
    python -m venv .venv
) else (
    echo (.venv đã tồn tại, tiếp tục bước tiếp theo...)
)

echo.
echo [2/3] Đang cài đặt các thư viện cần thiết...
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

echo.
echo [3/3] Đang tải trình duyệt Chromium cho Playwright...
.\.venv\Scripts\python.exe -m playwright install chromium

echo.
echo ================================================================
echo        ĐÃ CÀI ĐẶT THÀNH CÔNG VÀ SẴN SÀNG SỬ DỤNG!
echo ================================================================
echo.
echo Các bước sử dụng:
echo  1. Nhấp đúp chuột vào file: run_login.bat (để quét mã QR đăng nhập)
echo  2. Nhấp đúp chuột vào file: tai_kenh_douyin_bat_ky.bat (để tải video)
echo.
pause

