import os
import sys
import re
import shutil
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

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

COOKIES_TXT = os.path.join(SCRIPT_DIR, "tiktok_cookies.txt")


def download_single_worker(url, index=None, total=None):
    prefix = f"[{index}/{total}] " if index and total else ""
    print(f"{prefix}⏳ Đang tải: {url}")

    cmd = [
        YTDLP_EXE,
        "-P", DOWNLOAD_DIR,
        "-o", "%(uploader,creator,title)s_%(id)s.%(ext)s",
        "--impersonate", "chrome",
        "--windows-filenames",
        "--no-playlist",
        url
    ]

    if os.path.exists(COOKIES_TXT):
        cmd.extend(["--cookies", COOKIES_TXT])

    try:
        proc = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )

        if proc.returncode == 0:
            saved_name = ""
            for line in proc.stdout.splitlines():
                if "Merging formats into" in line:
                    match = re.search(r'Merging formats into "(.*?)"', line)
                    if match:
                        saved_name = os.path.basename(match.group(1))
                elif "Destination:" in line and not saved_name:
                    match = re.search(r'Destination: (.*)', line)
                    if match:
                        saved_name = os.path.basename(match.group(1).strip())
                elif "has already been downloaded" in line:
                    match = re.search(r'\[download\] (.*?) has already been downloaded', line)
                    if match:
                        saved_name = os.path.basename(match.group(1).strip()) + " (Đã có sẵn)"

            detail = f" -> {saved_name}" if saved_name else ""
            print(f"{prefix}✅ Hoàn tất!{detail}")
            return True, url, saved_name
        else:
            err = "Lỗi không xác định"
            for line in reversed(proc.stdout.splitlines()):
                if "ERROR" in line:
                    err = line.strip()
                    break
            if err == "Lỗi không xác định" and proc.stdout.strip():
                err = proc.stdout.strip().splitlines()[-1]
            print(f"{prefix}❌ Thất bại: {err}")
            return False, url, err
    except Exception as e:
        print(f"{prefix}❌ Lỗi ngoại lệ: {e}")
        return False, url, str(e)


def download_parallel(url_list, max_workers=3):
    total = len(url_list)
    active_workers = min(max_workers, total)
    print("==================================================")
    print(f"  BẮT ĐẦU TẢI SONG SONG {total} VIDEO CÙNG LÚC")
    print(f"  Số video tải đồng thời: {active_workers} luồng")
    print(f"  Thư mục lưu: {DOWNLOAD_DIR}")
    print("==================================================")

    success_count = 0
    fail_count = 0

    with ThreadPoolExecutor(max_workers=active_workers) as executor:
        future_to_url = {
            executor.submit(download_single_worker, url, i + 1, total): url
            for i, url in enumerate(url_list)
        }
        for future in as_completed(future_to_url):
            try:
                ok, _, _ = future.result()
                if ok:
                    success_count += 1
                else:
                    fail_count += 1
            except Exception:
                fail_count += 1

    print("\n==================================================")
    print("  TỔNG KẾT TẢI HÀNG LOẠT:")
    print(f"  - Tổng số link: {total}")
    print(f"  - Thành công: {success_count} video")
    if fail_count > 0:
        print(f"  - Thất bại: {fail_count} video")
    print(f"  - Thư mục lưu: {DOWNLOAD_DIR}")
    print("==================================================")


def download_interactive(url):
    print("==================================================")
    print("  TRÌNH TẢI VIDEO TIKTOK / FACEBOOK / YOUTUBE")
    print("  (Chất lượng cao nhất - Không logo)")
    print(f"  Thư mục lưu: {DOWNLOAD_DIR}")
    print("==================================================")

    cmd = [
        YTDLP_EXE,
        "-P", DOWNLOAD_DIR,
        "-o", "%(uploader,creator,title)s_%(id)s.%(ext)s",
        "--impersonate", "chrome",
        "--windows-filenames",
        "--concurrent-fragments", "4",
    ]

    if os.path.exists(COOKIES_TXT):
        print("  [Cookie] Nhận diện tiktok_cookies.txt")
        cmd.extend(["--cookies", COOKIES_TXT])

    is_single_video = any(k in url for k in ["/video/", "/reel/", "watch?v=", "/shorts/"])
    if is_single_video:
        cmd.append("--no-playlist")

    cmd.append(url)

    try:
        subprocess.run(cmd, check=True)
        print("\n==================================================")
        print("HOÀN TẤT! Video đã được lưu tại:")
        print(DOWNLOAD_DIR)
        print("==================================================")
    except subprocess.CalledProcessError:
        print("\n==================================================")
        print("[THÔNG BÁO NGUYÊN NHÂN & HƯỚNG DẪN]")
        if "tiktok.com" in url:
            if "/@" in url and "/video/" not in url:
                print("1. Bạn vừa dán link trang chủ KÊNH (@user).")
                print("   Nếu kênh này là phim ngắn / series hoặc tắt nhúng:")
                print("   -> Dán link 1 tập vào 'tai_tiktok_series.bat' để tải trọn bộ.")
            else:
                print("1. Nếu video yêu cầu đăng nhập:")
                print("   Chạy 'run_login_tiktok.bat' để đăng nhập 1 lần duy nhất.")
        print("==================================================")


def process_target(target):
    target = target.strip().strip('"').strip("'")
    if not target:
        target = "links.txt"

    # Check if target is a file
    if os.path.isfile(target):
        with open(target, "r", encoding="utf-8", errors="ignore") as f:
            lines = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]

        if not lines:
            print("==================================================")
            print(f"[CẢNH BÁO] File '{target}' hiện tại đang TRỐNG!")
            print(f"Vui lòng dán các link video vào file '{target}' rồi chạy lại.")
            print("==================================================")
            return

        if len(lines) == 1:
            download_interactive(lines[0])
        else:
            download_parallel(lines, max_workers=3)
        return

    # Check if target contains multiple URLs (separated by whitespace or comma)
    found_urls = re.findall(r'https?://[^\s,]+', target)
    if len(found_urls) > 1:
        download_parallel(found_urls, max_workers=3)
    elif len(found_urls) == 1:
        download_interactive(found_urls[0])
    else:
        # Maybe target was entered as filename but not found
        if target.endswith(".txt"):
            print(f"[LỖI] Không tìm thấy file: {target}")
            print(f"Vui lòng kiểm tra lại đường dẫn file.")
        else:
            download_interactive(target)


if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Check if multiple URLs were passed as arguments
        raw_args = sys.argv[1:]
        if len(raw_args) == 1:
            process_target(raw_args[0])
        else:
            process_target(" ".join(raw_args))
    else:
        print("==================================================")
        print("Ban co the:")
        print(" 1. Nhan ENTER ngay: Tu dong tai cac link trong 'links.txt'")
        print(" 2. Dan truc tiep link video / link kenh")
        print(" 3. Hoac dan nhieu link cach nhau boi dau cach")
        print(" 4. Hoac nhap ten file danh sach (vi du: links_maki.txt)")
        print("==================================================")
        target = input("Nhap link hoac file [Mac dinh: links.txt]: ").strip()
        process_target(target if target else "links.txt")
