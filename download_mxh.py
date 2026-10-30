import os
import sys
import subprocess

sys.stdout.reconfigure(line_buffering=True)

DOWNLOAD_DIR = r"T:\tải video hàng loạt\Downloaded\TikTok_Facebook"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

YTDLP_EXE = r"T:\tải video hàng loạt\.venv\Scripts\yt-dlp.exe"

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
        "--no-playlist",
        "--windows-filenames",
        "--concurrent-fragments", "4",
    ]

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
    except Exception as e:
        print(f"Loi trong qua trinh tai: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = input("Nhap link video hoac duong dan file links.txt: ").strip()

    if target:
        download(target)
    else:
        print("Chua nhap link!")

