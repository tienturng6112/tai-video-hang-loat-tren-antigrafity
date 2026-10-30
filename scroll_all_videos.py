import asyncio
import json
import re
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
        
        post_api_items = {}
        all_requests = []

        async def on_resp(r):
            u = r.url
            if '/aweme/v1/web/aweme/post' in u:
                print(f'POST API hit: {r.status} {u[:80]}')
                try:
                    data = await r.json()
                    for item in data.get('aweme_list', []):
                        aid = item.get('aweme_id')
                        if aid:
                            post_api_items[str(aid)] = item
                    print(f'Total post_api_items so far: {len(post_api_items)}, has_more: {data.get("has_more")}, max_cursor: {data.get("max_cursor")}')
                except Exception as e:
                    print('Post JSON error:', e)
            elif '/aweme/v1/web/user/profile' in u:
                try:
                    data = await r.json()
                    user = data.get('user', {})
                    print(f'Profile loaded: {user.get("nickname")}, aweme_count={user.get("aweme_count")}')
                except Exception as e:
                    pass

        page.on('response', on_resp)

        # Warm up
        print('Warming up on video page...')
        await page.goto('https://www.douyin.com/video/7701656445934210319', wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(3000)

        user_url = 'https://www.douyin.com/user/MS4wLjABAAAAQsKgmnH7iih6NGtvCjC6eXjGLtsFMKeNLx1hqqDg1ZViKWUW4J8j8zi4eaMF0sci'
        print('Opening channel page...')
        await page.goto(user_url, wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(5000)

        # Collect DOM video links & keep scrolling
        dom_ids = set()
        
        async def collect_dom_ids():
            data = await page.evaluate('''() => {
                const links = Array.from(document.querySelectorAll('a[href]'));
                const ids = [];
                for (const a of links) {
                    const m = a.href.match(/\\/video\\/(\\d+)/);
                    if (m) ids.push(m[1]);
                }
                // also check text in page
                const html = document.body ? document.body.innerHTML : '';
                const re = /"aweme_id":"(\\d{15,20})"/g;
                let match;
                while ((match = re.exec(html)) !== null) {
                    ids.push(match[1]);
                }
                return ids;
            }''')
            for i in data:
                dom_ids.add(str(i))

        await collect_dom_ids()
        print(f'Initial DOM ids: {len(dom_ids)}')

        # Scroll loop
        stagnant_count = 0
        last_count = len(dom_ids)
        for i in range(40):
            await page.mouse.wheel(0, 4000)
            await page.wait_for_timeout(2000)
            await collect_dom_ids()
            curr_count = len(dom_ids)
            print(f'Scroll {i+1}: DOM IDs={curr_count}, API items={len(post_api_items)}')
            if curr_count == last_count and len(post_api_items) == 0:
                stagnant_count += 1
                if stagnant_count >= 5:
                    print('Stagnant for 5 rounds, trying page down key...')
                    await page.keyboard.press('PageDown')
                    await page.wait_for_timeout(2000)
            else:
                stagnant_count = 0
            last_count = curr_count
            if curr_count >= 100:
                print('Reached 100 videos!')
                break

        print(f'Final captured DOM IDs count: {len(dom_ids)}')
        with open('captured_video_ids.json', 'w', encoding='utf-8') as f:
            json.dump(list(dom_ids), f, indent=2)

        if post_api_items:
            with open('captured_post_items.json', 'w', encoding='utf-8') as f:
                json.dump(post_api_items, f, ensure_ascii=False, indent=2)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())

