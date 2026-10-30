import asyncio
import json
import os
import re
import sys
import httpx
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True)

BASE_DIR = r"T:\tải video hàng loạt\Downloaded"
os.makedirs(BASE_DIR, exist_ok=True)

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
                    await asyncio.sleep(2)
                    continue
                with open(tmp_path, "wb") as f:
                    async for chunk in resp.aiter_bytes(chunk_size=131072):
                        f.write(chunk)
                os.replace(tmp_path, filepath)
                return True
        except Exception:
            if os.path.exists(tmp_path):
                try:
                    os.remove(tmp_path)
                except Exception:
                    pass
            await asyncio.sleep(2)
    return False

async def crawl_and_download(channel_url: str):
    print("==================================================")
    print("  TRINH TAI KENH DOUYIN TU CHON (1080P/4K KHONG LOGO)")
    print(f"  URL muc tieu: {channel_url}")
    print("==================================================")

    cookie_file = "cookies.json"
    cookies_payload = []
    if os.path.exists(cookie_file):
        with open(cookie_file, "r", encoding="utf-8") as f:
            cookie_dict = json.load(f)
        cookies_payload = [
            {"name": k, "value": v, "domain": ".douyin.com", "path": "/"}
            for k, v in cookie_dict.items() if k
        ]

    # Extract sec_uid if present in url
    m = re.search(r'user/([^/?]+)', channel_url)
    sec_uid = m.group(1) if m else None

    all_awemes = {}
    channel_info = {"nickname": "Douyin_Channel"}

    def extract_awemes_from_dict(d):
        aweme_list = d.get('aweme_list', [])
        for item in aweme_list:
            aid = str(item.get('aweme_id'))
            if aid and aid not in all_awemes:
                author = item.get('author', {})
                nick = author.get('nickname')
                item_sec_uid = author.get('sec_uid')

                if nick and channel_info["nickname"] == "Douyin_Channel":
                    channel_info["nickname"] = sanitize_filename(nick)

                if sec_uid and item_sec_uid and sec_uid not in item_sec_uid:
                    continue

                v = item.get('video', {})
                bitrates = v.get('bit_rate', [])
                selected = None
                for b in bitrates:
                    if '1080' in b.get('gear_name', ''):
                        selected = b
                        break
                if not selected and bitrates:
                    selected = max(bitrates, key=lambda b: b.get('bit_rate', 0))

                if selected:
                    urls = selected.get('play_addr', {}).get('url_list', [])
                    if urls:
                        all_awemes[aid] = {
                            'id': aid,
                            'title': item.get('desc', f'video_{aid}').strip(),
                            'nickname': nick or channel_info["nickname"],
                            'gear': selected.get('gear_name', 'default'),
                            'width': v.get('width', 0),
                            'height': v.get('height', 0),
                            'download_url': urls[0]
                        }

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            viewport={'width': 1600, 'height': 1000}
        )
        if cookies_payload:
            await context.add_cookies(cookies_payload)

        page = await context.new_page()

        mix_ids = set()

        async def on_resp(r):
            u = r.url
            if ('/aweme/v1/web/aweme/post' in u or '/aweme/v1/web/mix/aweme' in u) and r.status == 200:
                try:
                    body = await r.body()
                    data = json.loads(body.decode('utf-8'))
                    extract_awemes_from_dict(data)
                except Exception:
                    pass

        page.on('response', on_resp)

        print("[1/2] Dang mo trang kenh va lay danh sach video...")
        try:
            await page.goto(channel_url, wait_until='domcontentloaded', timeout=40000)
            await page.wait_for_timeout(4000)

            title = await page.title()
            page_nick = title.split(' - ')[0].replace('的主页', '').strip()
            if page_nick:
                channel_info["nickname"] = sanitize_filename(page_nick)

            # Check if there are mix collections on the channel
            mix_links = await page.evaluate('''() => {
                const links = Array.from(document.querySelectorAll('a[href*="/collection/"]'));
                return links.map(a => a.href);
            }''')
            for ml in mix_links:
                m_id = re.search(r'collection/(\d+)', ml)
                if m_id:
                    mix_ids.add(m_id.group(1))

            # Scroll channel page
            stagnant = 0
            last_count = 0
            for i in range(35):
                await page.mouse.wheel(0, 3500)
                await page.evaluate('''() => {
                    const c = document.querySelector('.route-scroll-container');
                    if (c) c.scrollTop = c.scrollHeight;
                }''')
                await page.wait_for_timeout(1500)
                curr = len(all_awemes)
                if curr > last_count:
                    print(f"  -> Da tim thay {curr} video...")
                    stagnant = 0
                else:
                    stagnant += 1
                    if stagnant >= 5:
                        break
                last_count = curr

        except Exception as e:
            print(f"Loi khi truy cap kenh: {e}")

        # Check mix collections if any
        if mix_ids:
            print(f"[2/2] Phat hien {len(mix_ids)} tuyen tap. Dang quet tuyen tap...")
            for mid in mix_ids:
                try:
                    await page.goto(f"https://www.douyin.com/collection/{mid}", wait_until='domcontentloaded', timeout=30000)
                    await page.wait_for_timeout(3000)
                    for _ in range(25):
                        await page.mouse.wheel(0, 3000)
                        await page.evaluate('''() => {
                            const c = document.querySelector('.route-scroll-container');
                            if (c) c.scrollTop = c.scrollHeight;
                        }''')
                        await page.wait_for_timeout(1500)
                except Exception:
                    pass

        await browser.close()

    channel_name = channel_info["nickname"]
    channel_dir = os.path.join(BASE_DIR, channel_name)
    os.makedirs(channel_dir, exist_ok=True)
    history_file = os.path.join(channel_dir, "download_history.json")

    history = set()
    if os.path.exists(history_file):
        try:
            with open(history_file, "r", encoding="utf-8") as f:
                history = set(json.load(f))
        except Exception:
            pass

    to_download = [v for v in all_awemes.values() if v["id"] not in history]
    print(f"\n==================================================")
    print(f"Kenh: {channel_name}")
    print(f"Tong so video tim thay: {len(all_awemes)}")
    print(f"Da tai truoc do: {len(history)}")
    print(f"So video can tai moi: {len(to_download)}")
    print(f"Thu muc luu: {channel_dir}")
    print(f"==================================================")

    if not to_download:
        print("Tat ca video da duoc tai ve truoc do!")
        return

    success = 0
    limits = httpx.Limits(max_keepalive_connections=5, max_connections=10)
    async with httpx.AsyncClient(timeout=180.0, follow_redirects=True, limits=limits) as http:
        for idx, item in enumerate(to_download, start=1):
            vid = item["id"]
            title = item.get("title", f"video_{vid}")
            url = item["download_url"]
            filename = f"{sanitize_filename(title)}_{vid}.mp4"
            filepath = os.path.join(channel_dir, filename)

            print(f"[{idx}/{len(to_download)}] Dang tai: {title[:50]}...")
            ok = await download_file(http, url, filepath)
            if ok:
                size_mb = os.path.getsize(filepath) / (1024 * 1024)
                print(f"  [OK] Luu thanh cong: {filename} ({size_mb:.2f} MB)")
                history.add(vid)
                with open(history_file, "w", encoding="utf-8") as f:
                    json.dump(list(history), f, ensure_ascii=False, indent=2)
                success += 1
            else:
                print(f"  [LOI] Khong tai duoc video {vid}")

    print(f"\nHOAN TAT! Da tai thanh cong {success} video vao:")
    print(channel_dir)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target = sys.argv[1]
    else:
        target = input("Nhap link kenh Douyin: ").strip()

    if target:
        asyncio.run(crawl_and_download(target))
    else:
        print("Chua nhap link!")

