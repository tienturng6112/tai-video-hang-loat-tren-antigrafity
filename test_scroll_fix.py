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
        
        post_api_pages = []

        async def on_resp(r):
            u = r.url
            if '/aweme/v1/web/aweme/post' in u:
                print(f'POST API hit: {r.status}')
                try:
                    data = await r.json()
                    items = data.get('aweme_list', [])
                    has_more = data.get('has_more')
                    max_cursor = data.get('max_cursor')
                    print(f'Page received: items={len(items)}, has_more={has_more}, max_cursor={max_cursor}')
                    post_api_pages.append(items)
                except Exception as e:
                    print('Post JSON error:', e)

        page.on('response', on_resp)

        # Warm up
        print('Warming up...')
        await page.goto('https://www.douyin.com/video/7701656445934210319', wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(3000)

        user_url = 'https://www.douyin.com/user/MS4wLjABAAAAQsKgmnH7iih6NGtvCjC6eXjGLtsFMKeNLx1hqqDg1ZViKWUW4J8j8zi4eaMF0sci'
        print('Opening channel page...')
        await page.goto(user_url, wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(5000)

        # Move mouse to center
        await page.mouse.move(800, 500)

        for i in range(15):
            print(f'--- Scroll step {i+1} ---')
            # Try multiple scrolling methods
            await page.mouse.move(800, 600)
            await page.mouse.wheel(0, 3000)
            await page.evaluate('window.scrollBy(0, 3000);')
            # Find the last video card or footer and scroll it into view
            await page.evaluate('''() => {
                const cards = document.querySelectorAll('li, div[data-e2e="user-post-list"] > *');
                if (cards.length > 0) {
                    cards[cards.length - 1].scrollIntoView({ behavior: 'smooth', block: 'end' });
                }
            }''')
            await page.wait_for_timeout(2500)
            print(f'Total post API pages loaded so far: {len(post_api_pages)}')
            total_items = sum(len(p) for p in post_api_pages)
            print(f'Total video items captured: {total_items}')
            if total_items >= 100:
                print('All 100 videos captured!')
                break

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())

