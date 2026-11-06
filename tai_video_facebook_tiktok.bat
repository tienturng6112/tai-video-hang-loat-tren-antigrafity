@echo off
title Trinh Tai Video TikTok - Facebook Reels - YouTube (Ho tro tai song song)
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
echo    (Chat luong cao nhat - Khong logo - TAI SONG SONG HANG LOAT)
echo ================================================================
echo.
echo HUONG DAN:
echo  1. Nhan ENTER ngay: Tu dong tai toan bo link trong file 'links.txt'
echo     (He thong se tai song song nhieu video cung luc sieu nhanh!)
echo  2. Hoac dan truc tiep link video / link kenh
echo  3. Hoac dan nhieu link cung luc cach nhau boi dau cach
echo  4. Hoac nhap ten file danh sach khac (vi du: links_maki.txt)
echo.
set "TARGET_URL="
set /p "TARGET_URL=Nhap link hoac file [Nhan ENTER de chon links.txt]: "

if "%TARGET_URL%"=="" (
    set "TARGET_URL=links.txt"
    echo.
    echo -> Da chon mac dinh: links.txt
)

echo.
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1

.\.venv\Scripts\python.exe download_mxh.py "%TARGET_URL%"
echo.
pause
