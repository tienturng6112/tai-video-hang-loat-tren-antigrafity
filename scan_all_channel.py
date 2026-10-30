import asyncio
import json
import os
from playwright.async_api import async_playwright

async def scan():
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

    print(f"Loaded {len(cookies_payload)} cookies. sessionid present: {'sessionid' in cookie_dict}")

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

        found_videos = {}

        async def on_resp(r):
            u = r.url
            if '/aweme/v1/web/aweme/post' in u or '/aweme/v1/web/mix/aweme' in u:
                try:
                    res = await r.json()
                    awemes = res.get('aweme_list', [])
                    print(f"API {u.split('?')[0].split('/')[-1]}: {len(awemes)} awemes (has_more={res.get('has_more')})")
                    for a in awemes:
                        aid = str(a.get('aweme_id'))
                        desc = a.get('desc', '')
                        if aid:
                            found_videos[aid] = {
                                "id": aid,
                                "url": f"https://www.douyin.com/video/{aid}",
                                "text": desc
                            }
                except Exception as e:
                    pass

        page.on('response', on_resp)

        # 1. First visit mix collection URL
        mix_url = 'https://www.douyin.com/collection/7651813684464846886'
        print(f"Opening mix collection: {mix_url}")
        try:
            await page.goto(mix_url, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(4000)
            
            # Scroll inside collection
            for s in range(25):
                await page.mouse.wheel(0, 3000)
                await page.evaluate('''() => {
                    const c = document.querySelector('.route-scroll-container');
                    if (c) c.scrollTop = c.scrollHeight;
                }''')
                await page.wait_for_timeout(1500)
                # also extract DOM links
                links = await page.evaluate('''() => {
                    const res = [];
                    for (const a of document.querySelectorAll('a[href*="/video/"]')) {
                        const m = a.href.match(/\\/video\\/(\\d+)/);
                        if (m) res.push({ id: m[1], text: (a.innerText || '').replace(/\\s+/g, ' ').trim() });
                    }
                    return res;
                }''')
                for l in links:
                    if l['id'] not in found_videos:
                        found_videos[l['id']] = {
                            "id": l['id'],
                            "url": f"https://www.douyin.com/video/{l['id']}",
                            "text": l['text']
                        }
                print(f"Mix scroll {s+1}: total collected = {len(found_videos)}")
                if len(found_videos) >= 94:
                    print("Reached collection full size!")
                    break
        except Exception as e:
            print("Error visiting mix:", e)

        # 2. Visit user channel page
        user_url = 'https://www.douyin.com/user/MS4wLjABAAAAQsKgmnH7iih6NGtvCjC6eXjGLtsFMKeNLx1hqqDg1ZViKWUW4J8j8zi4eaMF0sci'
        print(f"Opening user channel: {user_url}")
        try:
            await page.goto(user_url, wait_until='domcontentloaded', timeout=30000)
            await page.wait_for_timeout(4000)
            for s in range(30):
                await page.mouse.wheel(0, 3000)
                await page.evaluate('''() => {
                    const c = document.querySelector('.route-scroll-container');
                    if (c) c.scrollTop = c.scrollHeight;
                }''')
                await page.wait_for_timeout(1500)
                links = await page.evaluate('''() => {
                    const res = [];
                    for (const a of document.querySelectorAll('a[href*="/video/"]')) {
                        const m = a.href.match(/\\/video\\/(\\d+)/);
                        if (m) res.push({ id: m[1], text: (a.innerText || '').replace(/\\s+/g, ' ').trim() });
                    }
                    return res;
                }''')
                for l in links:
                    if l['id'] not in found_videos:
                        found_videos[l['id']] = {
                            "id": l['id'],
                            "url": f"https://www.douyin.com/video/{l['id']}",
                            "text": l['text']
                        }
                print(f"Channel scroll {s+1}: total collected = {len(found_videos)}")
                if len(found_videos) >= 100:
                    break
        except Exception as e:
            print("Error visiting channel:", e)

        print(f"\n==========================================")
        print(f"TOTAL VIDEOS COLLECTED: {len(found_videos)}")
        print(f"==========================================")

        with open("target_videos.json", "w", encoding="utf-8") as f:
            json.dump(list(found_videos.values()), f, ensure_ascii=False, indent=2)
        print("Updated target_videos.json successfully!")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(scan())

