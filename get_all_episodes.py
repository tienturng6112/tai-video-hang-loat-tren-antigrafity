import asyncio
import json
import re
from playwright.async_api import async_playwright

async def run():
    with open('fresh_cookies.json', 'r', encoding='utf-8') as f:
        cookie_dict = json.load(f)

    cookies_payload = [
        {"name": k, "value": v, "domain": ".douyin.com", "path": "/"}
        for k, v in cookie_dict.items() if k
    ]

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

        mix_url = 'https://www.douyin.com/collection/7651813684464846886'
        print('Opening collection URL directly with cookies...')
        try:
            await page.goto(mix_url, wait_until='domcontentloaded', timeout=40000)
        except Exception as e:
            print('Goto warning (proceeding anyway):', e)
        await page.wait_for_timeout(5000)

        # Scroll collection container
        for step in range(8):
            await page.evaluate('''() => {
                const c = document.querySelector('.route-scroll-container');
                if (c) c.scrollTop = c.scrollHeight;
            }''')
            await page.wait_for_timeout(1500)

        episodes = await page.evaluate('''() => {
            const res = [];
            const seen = new Set();
            const links = document.querySelectorAll('a[href*="/video/"]');
            for (const a of links) {
                const m = a.href.match(/\\/video\\/(\\d+)/);
                if (m) {
                    const id = m[1];
                    if (!seen.has(id)) {
                        seen.add(id);
                        const text = (a.innerText || '').replace(/\\s+/g, ' ').trim();
                        res.push({ id: id, url: a.href, text: text });
                    }
                }
            }
            return res;
        }''')
        print(f'Total episodes found in collection: {len(episodes)}')

        # Now also visit author profile to grab standalone videos
        user_url = 'https://www.douyin.com/user/MS4wLjABAAAAQsKgmnH7iih6NGtvCjC6eXjGLtsFMKeNLx1hqqDg1ZViKWUW4J8j8zi4eaMF0sci'
        print('Opening user profile...')
        try:
            await page.goto(user_url, wait_until='domcontentloaded', timeout=40000)
        except Exception as e:
            print('Profile goto warning:', e)
        await page.wait_for_timeout(5000)

        for step in range(5):
            await page.evaluate('''() => {
                const c = document.querySelector('.route-scroll-container');
                if (c) c.scrollTop = c.scrollHeight;
            }''')
            await page.wait_for_timeout(1500)

        user_vids = await page.evaluate('''() => {
            const res = [];
            const seen = new Set();
            const links = document.querySelectorAll('a[href*="/video/"]');
            for (const a of links) {
                const m = a.href.match(/\\/video\\/(\\d+)/);
                if (m && !seen.has(m[1])) {
                    seen.add(m[1]);
                    res.push({ id: m[1], url: a.href, text: (a.innerText || '').replace(/\\s+/g, ' ').trim() });
                }
            }
            return res;
        }''')
        print(f'Videos found on author profile: {len(user_vids)}')

        all_dict = {}
        for ep in episodes:
            all_dict[ep['id']] = ep
        for v in user_vids:
            if v['id'] not in all_dict:
                print(f'Added standalone video from profile: [{v["id"]}] {v["text"][:50]}')
                all_dict[v['id']] = v

        print(f'=================================================')
        print(f'GRAND TOTAL UNIQUE CHANNEL VIDEOS: {len(all_dict)}')
        print(f'=================================================')
        with open('target_videos.json', 'w', encoding='utf-8') as f:
            json.dump(list(all_dict.values()), f, ensure_ascii=False, indent=2)
        print('Saved target_videos.json!')

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())
