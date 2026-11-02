import os
import sys
import json
import shutil
import asyncio
import subprocess
from playwright.async_api import async_playwright

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
    sys.stderr.reconfigure(encoding='utf-8', errors='replace', line_buffering=True)
except Exception:
    pass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DOWNLOAD_DIR = os.path.join(SCRIPT_DIR, "Downloaded", "TikTok_Dramas")
os.makedirs(BASE_DOWNLOAD_DIR, exist_ok=True)

venv_ytdlp = os.path.join(SCRIPT_DIR, ".venv", "Scripts", "yt-dlp.exe")
if os.path.exists(venv_ytdlp):
    YTDLP_EXE = venv_ytdlp
elif shutil.which("yt-dlp"):
    YTDLP_EXE = shutil.which("yt-dlp")
else:
    YTDLP_EXE = "yt-dlp"

COOKIES_TXT = os.path.join(SCRIPT_DIR, "tiktok_cookies.txt")

async def extract_drama_info(initial_video_url):
    print("\n[1/3] Dang khoi chay trinh duyet ngam de quet danh sach tap phim...")
    drama_info = {
        "drama_title": "TikTok_Drama",
        "total_episodes": 0,
        "episodes": []
    }
    api_req_url = None

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page(viewport={"width": 1280, "height": 800})

        async def on_req(req):
            nonlocal api_req_url
            if "/api/drama/episode/item_list/" in req.url:
                api_req_url = req.url

        async def on_resp(resp):
            if "/api/drama/episode/item_list/" in resp.url:
                try:
                    data = await resp.json()
                    for item in data.get("itemList", []):
                        ep_data = item.get("dramaInfo", {}).get("DramaVideoData", {})
                        drama_name = item.get("dramaInfo", {}).get("dramaName")
                        if drama_name and drama_info["drama_title"] == "TikTok_Drama":
                            drama_info["drama_title"] = drama_name
                        
                        ep_num = ep_data.get("EpisodeNumber") or 0
                        drama_info["episodes"].append({
                            "id": item.get("id"),
                            "ep": ep_num,
                            "desc": item.get("desc", ""),
                            "url": f"https://www.tiktok.com/@user/video/{item.get('id')}"
                        })
                except Exception:
                    pass

        page.on("request", on_req)
        page.on("response", on_resp)

        print(f"      Dang truy cap: {initial_video_url}")
        try:
            await page.goto(initial_video_url, wait_until="commit", timeout=30000)
            await page.wait_for_timeout(4000)
        except Exception as e:
            print(f"      Loi truy cap: {e}")

        # Check rehydration data if API URL not captured yet
        if not drama_info["episodes"]:
            data_str = await page.evaluate('''() => {
                const el = document.getElementById("__UNIVERSAL_DATA_FOR_REHYDRATION__");
                return el ? el.textContent : null;
            }''')
            if data_str:
                try:
                    rehyd = json.loads(data_str)
                    video_detail = rehyd.get("__DEFAULT_SCOPE__", {}).get("webapp.video-detail", {})
                    item = video_detail.get("itemInfo", {}).get("itemStruct", {})
                    d_info = item.get("dramaInfo")
                    if d_info:
                        drama_info["drama_title"] = d_info.get("dramaName", "TikTok_Drama")
                except Exception:
                    pass

        # Paginate remaining episodes if api_req_url was found
        if api_req_url:
            cursor = 24
            while True:
                next_url = api_req_url.replace("cursor=0", f"cursor={cursor}")
                res = await page.evaluate('''async (url) => {
                    try {
                        const r = await fetch(url);
                        return await r.json();
                    } catch(e) {
                        return null;
                    }
                }''', next_url)
                if not res or not res.get("itemList"):
                    break
                items = res.get("itemList", [])
                for item in items:
                    ep_data = item.get("dramaInfo", {}).get("DramaVideoData", {})
                    ep_num = ep_data.get("EpisodeNumber") or 0
                    drama_info["episodes"].append({
                        "id": item.get("id"),
                        "ep": ep_num,
                        "desc": item.get("desc", ""),
                        "url": f"https://www.tiktok.com/@user/video/{item.get('id')}"
                    })
                if not res.get("hasMore") or len(items) == 0:
                    break
                cursor += len(items)

        await browser.close()

    # Deduplicate episodes by id
    seen = set()
    unique_eps = []
    for ep in drama_info["episodes"]:
        if ep["id"] not in seen:
            seen.add(ep["id"])
            unique_eps.append(ep)

    unique_eps.sort(key=lambda x: x["ep"])
    drama_info["episodes"] = unique_eps
    drama_info["total_episodes"] = len(unique_eps)
    return drama_info

def download_all_episodes(drama_info):
    title = "".join(c for c in drama_info["drama_title"] if c.isalnum() or c in " _-").strip()
    if not title:
        title = "TikTok_Drama_Series"

    save_dir = os.path.join(BASE_DOWNLOAD_DIR, title)
    os.makedirs(save_dir, exist_ok=True)

    episodes = drama_info["episodes"]
    total = len(episodes)
    print(f"\n[2/3] Da tim thay: {total} tap phim trong series '{title}'")
    print(f"      Thu muc luu: {save_dir}")

    temp_list_file = os.path.join(save_dir, "episode_links.txt")
    with open(temp_list_file, "w", encoding="utf-8") as f:
        for ep in episodes:
            f.write(ep["url"] + "\n")

    print(f"\n[3/3] Dang tien hanh tai tron bo {total} tap...")

    cmd = [
        YTDLP_EXE,
        "-P", save_dir,
        "-o", "Tap_%(autonumber)02d_%(id)s.%(ext)s",
        "--autonumber-start", "1",
        "--impersonate", "chrome",
        "--windows-filenames",
        "--concurrent-fragments", "4",
        "-a", temp_list_file
    ]

    if os.path.exists(COOKIES_TXT):
        cmd.extend(["--cookies", COOKIES_TXT])

    try:
        subprocess.run(cmd, check=True)
        print("\n" + "="*60)
        print("HOAN TAT! DA TAI XONG TOAN BO TAP PHIM!")
        print(f"Thu muc luu: {save_dir}")
        print("="*60)
    except subprocess.CalledProcessError as e:
        print(f"\n[!] Qua trinh tai gap loi: {e}")

def main():
    print("="*60)
    print("   CONG CU TAI TRON BO PHIM NGAN / SERIES TIKTOK")
    print("   (Tu dong quet toan bo tap tu 1 link bat ky)")
    print("="*60)

    if len(sys.argv) > 1:
        target_url = sys.argv[1].strip()
    else:
        target_url = input("\nNhap link 1 tap bat ky cua phim (VD: .../video/...): ").strip()

    if not target_url:
        print("Chua nhap link!")
        return

    drama_info = asyncio.run(extract_drama_info(target_url))
    if not drama_info["episodes"]:
        print("\n[!] Khong tim thay danh sach tap phim tu link nay.")
        print("    Hay chac chan ban dan link 1 tap phim cu the (co chua '/video/').")
        return

    download_all_episodes(drama_info)

if __name__ == "__main__":
    main()

