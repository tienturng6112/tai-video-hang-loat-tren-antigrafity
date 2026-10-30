import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            viewport={'width': 1600, 'height': 1000}
        )
        page = await context.new_page()

        mix_videos = {}

        async def on_resp(r):
            if 'mix/aweme' in r.url:
                try:
                    data = await r.json()
                    items = data.get('aweme_list', [])
                    for item in items:
                        aid = item.get('aweme_id')
                        if aid:
                            mix_videos[str(aid)] = item
                    print(f'Mix API resp: current total = {len(mix_videos)}, cursor={data.get("cursor")}, has_more={data.get("has_more")}')
                except Exception as e:
                    pass

        page.on('response', on_resp)
        await page.goto('https://www.douyin.com/video/7701656445934210319', wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(3000)

        mix_url = 'https://www.douyin.com/collection/7651813684464846886'
        await page.goto(mix_url, wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(4000)

        # Find playlist scroll container
        container_selector = await page.evaluate('''() => {
            // Find container holding episode links
            const links = document.querySelectorAll('a[href*="/video/"]');
            if (links.length > 0) {
                let p = links[0].parentElement;
                while (p && p !== document.body) {
                    const s = window.getComputedStyle(p);
                    if (s.overflowY === 'auto' || s.overflowY === 'scroll') {
                        return p.className;
                    }
                    p = p.parentElement;
                }
            }
            return null;
        }''')
        print('Playlist scroll container class:', container_selector)

        # Scroll the playlist container
        for step in range(25):
            res = await page.evaluate('''() => {
                const links = document.querySelectorAll('a[href*="/video/"]');
                if (links.length > 0) {
                    let p = links[0].parentElement;
                    while (p && p !== document.body) {
                        const s = window.getComputedStyle(p);
                        if (s.overflowY === 'auto' || s.overflowY === 'scroll') {
                            p.scrollTop += 2000;
                            return { scrollTop: p.scrollTop, scrollHeight: p.scrollHeight, count: links.length };
                        }
                        p = p.parentElement;
                    }
                }
                return null;
            }''')
            print(f'Step {step+1}: {res}, captured API items: {len(mix_videos)}')
            await page.wait_for_timeout(1500)
            if len(mix_videos) >= 94:
                print('Captured all 94 mix videos!')
                break

        print('Final mix videos captured via API:', len(mix_videos))
        with open('mix_videos.json', 'w', encoding='utf-8') as f:
            json.dump(mix_videos, f, ensure_ascii=False, indent=2)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())

