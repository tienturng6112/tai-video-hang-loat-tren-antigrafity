@echo off
title Douyin Channel Downloader - 1080p No Watermark
chcp 65001 >nul
cls
echo =======================================================
echo   TRINH TAI TOAN BO VIDEO DOUYIN 1080P/4K KHONG LOGO
echo   Kenh: Dao Dan Mo Mo (100 video)
echo =======================================================
echo.
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
.\.venv\Scripts\python.exe download_channel.py %*
echo.
pause
