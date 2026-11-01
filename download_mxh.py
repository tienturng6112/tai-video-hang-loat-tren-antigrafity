import os
import sys
import subprocess

sys.stdout.reconfigure(line_buffering=True)

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

