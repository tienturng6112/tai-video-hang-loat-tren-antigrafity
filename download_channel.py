import asyncio
import json
import os
import re
import sys
import httpx

sys.stdout.reconfigure(line_buffering=True)

DOWNLOAD_DIR = r"T:\tải video hàng loạt\Downloaded\捣蛋暮暮"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
HISTORY_FILE = os.path.join(DOWNLOAD_DIR, "download_history.json")
VIDEOS_DATA_FILE = "all_channel_videos.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(list(history), f, ensure_ascii=False, indent=2)

def sanitize_filename(name: str) -> str:
    cleaned = re.sub(r'[\\/*?:"<>|]', '_', name)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned[:85]

async def download_file(client: httpx.AsyncClient, url: str, filepath: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        'Referer': 'https://www.douyin.com/'
    }
    tmp_path = filepath + ".tmp"
    for attempt in range(3):
        try:
            async with client.stream('GET', url, headers=headers) as resp:
                if resp.status_code != 200:
                    print(f"  [LỖI] HTTP {resp.status_code} khi tải stream video (lần {attempt+1})")
                    await asyncio.sleep(2)
                    continue
                with open(tmp_path, "wb") as f:
                    async for chunk in resp.aiter_bytes(chunk_size=131072):
                        f.write(chunk)
                os.replace(tmp_path, filepath)
                return True
        except Exception as e:
            print(f"  [CẢNH BÁO] Lỗi khi tải lần {attempt+1}: {e}")
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            await asyncio.sleep(2)
    return False

async def main(max_downloads=None):
    history = load_history()
    print(f"==================================================")
    print(f"  TRÌNH TẢI VIDEO DOUYIN 1080P/4K KHÔNG LOGO")
    print(f"  Kênh: 捣蛋暮暮 (Đáo Đản Mộ Mộ)")
    print(f"  Thư mục lưu: {DOWNLOAD_DIR}")
    print(f"  Đã tải trước đó: {len(history)} video")
    print(f"==================================================")

    if not os.path.exists(VIDEOS_DATA_FILE):
        print(f"[THÔNG BÁO] Chưa có dữ liệu kênh {VIDEOS_DATA_FILE}, đang tự động quét kênh...")
        import export_all_clean_urls
        await export_all_clean_urls.main()

    if not os.path.exists(VIDEOS_DATA_FILE):
        print("[LỖI] Không tìm thấy dữ liệu video của kênh.")
        return

    with open(VIDEOS_DATA_FILE, "r", encoding="utf-8") as f:
        targets = json.load(f)

    print(f"Tổng số video của kênh: {len(targets)} video.")
    
    to_download = [t for t in targets if str(t["id"]) not in history]
    print(f"Số video cần tải mới: {len(to_download)} video.")
    
    if not to_download:
        print("[THÔNG BÁO] Bạn đã tải trọn bộ tất cả các video của kênh rồi!")
        return

    success_count = 0
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    async with httpx.AsyncClient(timeout=180.0, follow_redirects=True, limits=limits) as http_client:
        for idx, item in enumerate(to_download, start=1):
            vid = str(item["id"])
            title = item.get("title", f"video_{vid}").strip()
            gear = item.get("gear", "1080p")
            w = item.get("width", 0)
            h = item.get("height", 0)
            url = item.get("download_url")

            if max_downloads and success_count >= max_downloads:
                print(f"Đã đạt số lượng video yêu cầu ({max_downloads}).")
                break

            clean_title = sanitize_filename(title)
            filename = f"{clean_title}_{vid}.mp4"
            filepath = os.path.join(DOWNLOAD_DIR, filename)

            print(f"\n[{idx}/{len(to_download)}] [Tổng {len(history) + 1}/{len(targets)}] Đang tải video {vid}...")
            print(f"  Tiêu đề: {title[:70]}")
            print(f"  Chất lượng: {gear} ({w}x{h}) - SẠCH 100% KHÔNG LOGO")

            ok = await download_file(http_client, url, filepath)
            if ok:
                filesize = os.path.getsize(filepath) / (1024 * 1024)
                print(f"  [THÀNH CÔNG] Đã lưu: {filename} ({filesize:.2f} MB)")
                history.add(vid)
                save_history(history)
                success_count += 1
            else:
                print(f"  [THẤT BẠI] Không thể tải video {vid}")

    print(f"\n==================================================")
    print(f"HOÀN TẤT ĐỢT TẢI! Đã tải thành công thêm {success_count} video.")
    print(f"Tổng số video đã có trong máy: {len(history)}/{len(targets)} video.")
    print(f"Thư mục lưu trữ: {DOWNLOAD_DIR}")
    print(f"==================================================")

if __name__ == "__main__":
    count = int(sys.argv[1]) if len(sys.argv) > 1 else None
    asyncio.run(main(count))
