import asyncio
import json
import os
import sys
from playwright.async_api import async_playwright

sys.stdout.reconfigure(line_buffering=True)

async def main():
    cookie_file = "cookies.json"
    if not os.path.exists(cookie_file):
        print("[LỖI] Không tìm thấy cookies.json!")
        return

    with open(cookie_file, "r", encoding="utf-8") as f:
        cookie_dict = json.load(f)

    cookies_payload = [
        {"name": k, "value": v, "domain": ".douyin.com", "path": "/"}
        for k, v in cookie_dict.items() if k
    ]

    all_awemes = {}

    def extract_awemes_from_dict(d):
        aweme_list = d.get('aweme_list', [])
        for item in aweme_list:
            aid = str(item.get('aweme_id'))
            if aid and aid not in all_awemes:
                # check author
                author = item.get('author', {})
                sec_uid = author.get('sec_uid', '')
                nickname = author.get('nickname', '')
                
                # Filter for this channel: MS4wLjABAAAAQsKgmnH7iih6NGtvCjC6eXjGLtsFMKeNLx1hqqDg1ZViKWUW4J8j8zi4eaMF0sci or 捣蛋暮暮
                if 'MS4wLjABAAAAQsKgmnH7iih6NGtvCjC6eXjGLtsFMKeNLx1hqqDg1ZViKWUW4J8j8zi4eaMF0sci' in sec_uid or '捣蛋暮暮' in nickname:
                    # pick best bitrate (1080p first)
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
                                'nickname': nickname,
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
        await context.add_cookies(cookies_payload)
        page = await context.new_page()

        async def on_resp(r):
            u = r.url
            if ('/aweme/v1/web/aweme/post' in u or '/aweme/v1/web/mix/aweme' in u) and r.status == 200:
                try:
                    body = await r.body()
                    data = json.loads(body.decode('utf-8'))
                    before = len(all_awemes)
                    extract_awemes_from_dict(data)
                    after = len(all_awemes)
                    print(f"API {u.split('?')[0].split('/')[-1]}: +{after - before} videos mới (Tổng kênh: {after})")
                except Exception as e:
                    print(f"Lỗi parse response: {e}")

        page.on('response', on_resp)

        # 1. Quét Mix Collection (Tuyển tập 瓦瓦特工日记)
        print("--- [1/2] Đang quét Tuyển tập 瓦瓦特工日记 ---")
        try:
            await page.goto('https://www.douyin.com/collection/7651813684464846886', wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(3000)
            for i in range(25):
                await page.mouse.wheel(0, 3000)
                await page.evaluate('''() => {
                    const c = document.querySelector('.route-scroll-container');
                    if (c) c.scrollTop = c.scrollHeight;
                }''')
                await page.wait_for_timeout(1500)
                if len(all_awemes) >= 94:
                    print(f"Đã lấy đủ {len(all_awemes)} video từ tuyển tập!")
                    break
        except Exception as e:
            print(f"Lỗi khi quét tuyển tập: {e}")

        # 2. Quét Trang cá nhân chính
        print(f"\n--- [2/2] Đang quét Trang cá nhân kênh ---")
        try:
            user_url = 'https://www.douyin.com/user/MS4wLjABAAAAQsKgmnH7iih6NGtvCjC6eXjGLtsFMKeNLx1hqqDg1ZViKWUW4J8j8zi4eaMF0sci'
            await page.goto(user_url, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(3000)
            for i in range(25):
                await page.mouse.wheel(0, 3000)
                await page.evaluate('''() => {
                    const c = document.querySelector('.route-scroll-container');
                    if (c) c.scrollTop = c.scrollHeight;
                }''')
                await page.wait_for_timeout(1500)
                if len(all_awemes) >= 100:
                    print(f"Đã đạt mốc {len(all_awemes)} video!")
                    break
        except Exception as e:
            print(f"Lỗi khi quét trang cá nhân: {e}")

        await browser.close()

    print(f"\n==================================================")
    print(f"TỔNG SỐ VIDEO KÊNH THU THẬP ĐƯỢC: {len(all_awemes)}")
    print(f"==================================================")

    output_file = "all_channel_videos.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(list(all_awemes.values()), f, ensure_ascii=False, indent=2)

    print(f"Đã lưu danh sách video vào: {output_file}")

if __name__ == "__main__":
    asyncio.run(main())

