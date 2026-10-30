import asyncio
import json
import re
from playwright.async_api import async_playwright

async def run():
    with open('fresh_cookies.json', 'r', encoding='utf-8') as f:
        cookie_dict = json.load(f)

    cookies_payload = [
        {'name': k, 'value': v, 'domain': '.douyin.com', 'path': '/'}
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

        print('Loading collection page...')
        await page.goto('https://www.douyin.com/collection/7651813684464846886', wait_until='domcontentloaded', timeout=40000)
        await page.wait_for_timeout(4000)

        episodes_map = {}

        async def collect_visible():
            data = await page.evaluate('''() => {
                const res = [];
                const links = document.querySelectorAll('a[href*="/video/"]');
                for (const a of links) {
                    const m = a.href.match(/\\/video\\/(\\d+)/);
                    if (m) {
                        res.push({
                            id: m[1],
                            url: a.href,
                            text: (a.innerText || '').replace(/\\s+/g, ' ').trim()
                        });
                    }
                }
                return res;
            }''')
            for item in data:
                if item['id'] not in episodes_map:
                    episodes_map[item['id']] = item

        await collect_visible()
        print(f'Initial visible: {len(episodes_map)}')

        # Gradual scroll down
        stagnant = 0
        last_len = len(episodes_map)
        for step in range(50):
            await page.evaluate('''() => {
                const c = document.querySelector('.route-scroll-container');
                if (c) c.scrollTop += 600;
            }''')
            await page.wait_for_timeout(800)
            await collect_visible()
            curr_len = len(episodes_map)
            print(f'Step {step+1}: total unique episodes so far = {curr_len}')
            if curr_len == last_len:
                stagnant += 1
                if stagnant >= 6:
                    print('Stagnant reached bottom!')
                    break
            else:
                stagnant = 0
            last_len = curr_len
            if curr_len >= 94:
                print('Reached 94 episodes!')
                break

        print(f'Final collection episodes captured: {len(episodes_map)}')
        with open('collection_episodes.json', 'w', encoding='utf-8') as f:
            json.dump(list(episodes_map.values()), f, ensure_ascii=False, indent=2)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())

