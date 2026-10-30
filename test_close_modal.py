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

        # Scroll to trigger modal
        await page.evaluate('''() => {
            const c = document.querySelector('.route-scroll-container');
            if (c) c.scrollTop += 3000;
        }''')
        await page.wait_for_timeout(2000)

        # Check for close button on modal
        close_btn = await page.evaluate('''() => {
            const btns = Array.from(document.querySelectorAll('*'));
            const matches = [];
            for (const b of btns) {
                const cls = (b.className || '').toString();
                if (cls.toLowerCase().includes('close') || b.getAttribute('data-e2e') === 'close-icon' || b.getAttribute('aria-label') === '关闭') {
                    matches.push({ tag: b.tagName, class: cls, rect: b.getBoundingClientRect() });
                }
            }
            return matches;
        }''')
        print('Close button candidates:', close_btn)

        # Try clicking any visible close button
        if close_btn:
            print('Trying to click close button...')
            await page.evaluate('''() => {
                for (const b of document.querySelectorAll('*')) {
                    const cls = (b.className || '').toString();
                    if (cls.toLowerCase().includes('close') || b.getAttribute('data-e2e') === 'close-icon') {
                        b.click();
                        return;
                    }
                }
            }''')
            await page.wait_for_timeout(2000)

        # Or remove modal directly from DOM
        await page.evaluate('''() => {
            for (const el of document.querySelectorAll('div')) {
                if (el.innerText && el.innerText.includes('登录后免费畅享') && el.innerText.includes('扫码登录')) {
                    el.remove();
                }
            }
        }''')
        await page.wait_for_timeout(1000)

        # Now scroll again!
        for i in range(5):
            await page.evaluate('''() => {
                const c = document.querySelector('.route-scroll-container');
                if (c) c.scrollTop += 2000;
            }''')
            await page.wait_for_timeout(1500)

        # Check if more videos appeared in DOM
        count = await page.evaluate('''() => {
            return document.querySelectorAll('a[href*="/video/"]').length;
        }''')
        print('Video links count after dismissing modal and scrolling:', count)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())

