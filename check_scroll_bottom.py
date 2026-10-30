import asyncio
import json
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

        url = 'https://www.douyin.com/user/MS4wLjABAAAAQsKgmnH7iih6NGtvCjC6eXjGLtsFMKeNLx1hqqDg1ZViKWUW4J8j8zi4eaMF0sci'
        await page.goto(url, wait_until='domcontentloaded', timeout=40000)
        await page.wait_for_timeout(4000)

        # Scroll to bottom of route-scroll-container
        await page.evaluate('''() => {
            const c = document.querySelector('.route-scroll-container');
            if (c) c.scrollTop = c.scrollHeight;
        }''')
        await page.wait_for_timeout(3000)

        await page.screenshot(path='user_scroll_bottom.png', full_page=False)
        print('Saved user_scroll_bottom.png')

        # Check all visible texts at bottom
        texts = await page.evaluate('''() => {
            const res = [];
            for (const el of document.querySelectorAll('button, div, p, span')) {
                const t = (el.innerText || '').trim();
                if (t.includes('登录') || t.includes('更多') || t.includes('没有更多') || t.includes('查看')) {
                    if (t.length < 50) res.push(t);
                }
            }
            return Array.from(new Set(res));
        }''')
        print('Bottom texts found:', texts)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())

