@echo off
chcp 65001 >nul
echo =======================================================
echo   ĐĂNG NHẬP DOUYIN ĐỂ MỞ KHÓA TẢI HẾT TẤT CẢ VIDEO
echo =======================================================
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
.\.venv\Scripts\python.exe login_helper.py
pause

