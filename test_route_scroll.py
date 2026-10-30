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
        
        all_videos = {}

        async def on_resp(r):
            u = r.url
            if '/aweme/v1/web/aweme/post' in u:
                try:
                    data = await r.json()
                    items = data.get('aweme_list', [])
                    for item in items:
                        aid = item.get('aweme_id')
                        if aid:
                            all_videos[str(aid)] = item
                    print(f'API resp: total videos now = {len(all_videos)}, has_more={data.get("has_more")}, cursor={data.get("max_cursor")}')
                except Exception as e:
                    pass

        page.on('response', on_resp)
        await page.goto('https://www.douyin.com/video/7701656445934210319', wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(3000)

        user_url = 'https://www.douyin.com/user/MS4wLjABAAAAQsKgmnH7iih6NGtvCjC6eXjGLtsFMKeNLx1hqqDg1ZViKWUW4J8j8zi4eaMF0sci'
        await page.goto(user_url, wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(4000)

        for step in range(20):
            res = await page.evaluate('''() => {
                const c = document.querySelector('.route-scroll-container');
                if (c) {
                    c.scrollTop += 2500;
                    return { scrollTop: c.scrollTop, scrollHeight: c.scrollHeight, clientHeight: c.clientHeight };
                }
                return null;
            }''')
            print(f'Step {step+1}: container state: {res}, unique videos: {len(all_videos)}')
            await page.wait_for_timeout(2000)
            if len(all_videos) >= 100:
                print('Captured all 100 videos!')
                break

        print('Final unique videos count:', len(all_videos))
        with open('all_channel_videos.json', 'w', encoding='utf-8') as f:
            json.dump(all_videos, f, ensure_ascii=False, indent=2)
        print('Saved all_channel_videos.json!')

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())

