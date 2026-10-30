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

        mix_items = []
        async def on_resp(r):
            if 'mix/aweme' in r.url:
                print('Intercepted mix/aweme API! Status:', r.status)
                try:
                    data = await r.json()
                    items = data.get('aweme_list', [])
                    print(f'Mix API returned {len(items)} items! cursor={data.get("cursor")}, has_more={data.get("has_more")}')
                    mix_items.extend(items)
                except Exception as e:
                    print('JSON err:', e)

        page.on('response', on_resp)
        await page.goto('https://www.douyin.com/video/7701656445934210319', wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(3000)

        mix_url = 'https://www.douyin.com/collection/7651813684464846886'
        print('Going to mix url:', mix_url)
        await page.goto(mix_url, wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(5000)

        print('Total mix items so far:', len(mix_items))
        title = await page.title()
        print('Title:', title.encode('ascii', errors='replace').decode())
        
        # Check if collection page loads all episodes or lists them in the playlist sidebar
        episodes = await page.evaluate('''() => {
            const list = [];
            const links = document.querySelectorAll('a[href*="/video/"]');
            for (const a of links) {
                const m = a.href.match(/\\/video\\/(\\d+)/);
                if (m) list.push({ id: m[1], text: (a.innerText || '').slice(0, 50) });
            }
            return list;
        }''')
        print(f'Episodes found on collection page DOM: {len(episodes)}')
        for ep in episodes[:5]:
            print('  ->', ep)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())

