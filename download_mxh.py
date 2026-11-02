import os
import sys
import shutil
import subprocess

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
except Exception:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(SCRIPT_DIR, "Downloaded", "TikTok_Facebook")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

venv_ytdlp = os.path.join(SCRIPT_DIR, ".venv", "Scripts", "yt-dlp.exe")
if os.path.exists(venv_ytdlp):
    YTDLP_EXE = venv_ytdlp
elif shutil.which("yt-dlp"):
    YTDLP_EXE = shutil.which("yt-dlp")
else:
    YTDLP_EXE = "yt-dlp"

def download(url_or_file):
    print("==================================================")
    print("  TRINH TAI VIDEO TIKTOK / FACEBOOK REELS")
    print("  (Tu dong tai chat luong cao nhat va khong logo)")
    print(f"  Thu muc luu: {DOWNLOAD_DIR}")
    print("==================================================")

    cmd = [
        YTDLP_EXE,
        "-P", DOWNLOAD_DIR,
        "-o", "%(uploader,creator,title)s_%(id)s.%(ext)s",
        "--impersonate", "chrome",
        "--windows-filenames",
        "--concurrent-fragments", "4",
    ]

    cookies_txt = os.path.join(SCRIPT_DIR, "tiktok_cookies.txt")
    if os.path.exists(cookies_txt):
        print("  [Cookie] Da nhan dien phien dang nhap TikTok (tiktok_cookies.txt)")
        cmd.extend(["--cookies", cookies_txt])

    # Neu la 1 link video don le thi moi them --no-playlist
    is_single_video = any(k in url_or_file for k in ["/video/", "/reel/", "watch?v=", "/shorts/"])
    if is_single_video:
        cmd.append("--no-playlist")

    if os.path.exists(url_or_file):
        cmd.extend(["-a", url_or_file])
    else:
        cmd.append(url_or_file)

    try:
        subprocess.run(cmd, check=True)
        print("\n==================================================")
        print("HOAN TAT! Video da duoc luu tai:")
        print(DOWNLOAD_DIR)
        print("==================================================")
    except subprocess.CalledProcessError:
        print("\n==================================================")
        print("[THONG BAO NGUYEN NHAN & HUONG DAN]")
        if "tiktok.com" in url_or_file:
            if "/@" in url_or_file and "/video/" not in url_or_file:
                print("1. Ban vua dan link trang chu cua KENH (@user).")
                print("   Neu kenh nay la kenh PHIM NGAN / SERIES (Short Drama) hoac tat tinh nang nhung,")
                print("   TikTok se khong tra ve video feed thong thuong.")
                print("   -> GIAI PHAP:")
                print("      - Dan link 1 TAP BAT KY cua phim vao 'tai_tiktok_series.bat' de tai tron bo.")
                print("      - Hoac dan truc tiep link tap video (co /video/...) vao day.")
            else:
                print("1. Neu kenh TikTok bat che do Private hoac yeu cau dang nhap:")
                print("   Ban hay chay file 'run_login_tiktok.bat' de dang nhap TikTok 1 lan duy nhat.")
            print("2. Voi cac video/kenh TikTok thong thuong khac, cong cu se tu dong tai ngay.")
        print("==================================================")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = input("Nhap link video hoac duong dan file links.txt: ").strip()

    if target:
        download(target)
    else:
        print("Chua nhap link!")
