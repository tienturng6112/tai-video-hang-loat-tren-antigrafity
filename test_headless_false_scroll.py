import asyncio
import json
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            viewport={'width': 1600, 'height': 1000}
        )
        page = await context.new_page()

        post_api_pages = []

        async def on_resp(r):
            u = r.url
            if '/aweme/v1/web/aweme/post' in u:
                print('POST API hit!')
                try:
                    data = await r.json()
                    items = data.get('aweme_list', [])
                    print(f'Received {len(items)} items! cursor={data.get("max_cursor")}, has_more={data.get("has_more")}')
                    post_api_pages.append(items)
                except Exception as e:
                    print('Post json err:', e)

        page.on('response', on_resp)

        url = 'https://www.douyin.com/user/MS4wLjABAAAAQsKgmnH7iih6NGtvCjC6eXjGLtsFMKeNLx1hqqDg1ZViKWUW4J8j8zi4eaMF0sci'
        await page.goto(url, wait_until='domcontentloaded', timeout=40000)
        await page.wait_for_timeout(5000)

        # Move mouse to center of page
        await page.mouse.move(800, 600)

        for i in range(25):
            await page.mouse.wheel(0, 3000)
            await page.wait_for_timeout(1500)
            total = sum(len(p) for p in post_api_pages)
            print(f'Scroll {i+1}: total items = {total}')
            if total >= 100:
                print('All 100 loaded!')
                break

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())

