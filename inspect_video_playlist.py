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

        await page.goto('https://www.douyin.com/video/7701656445934210319', wait_until='domcontentloaded', timeout=40000)
        await page.wait_for_timeout(4000)

        info = await page.evaluate('''() => {
            const lis = document.querySelectorAll('li a[href*="/video/"]');
            let scrollParent = null;
            if (lis.length > 0) {
                let p = lis[0].parentElement;
                while (p && p !== document.body) {
                    const s = window.getComputedStyle(p);
                    if (s.overflowY === 'auto' || s.overflowY === 'scroll') {
                        scrollParent = {
                            class: p.className,
                            scrollHeight: p.scrollHeight,
                            clientHeight: p.clientHeight,
                            scrollTop: p.scrollTop
                        };
                        break;
                    }
                    p = p.parentElement;
                }
            }
            return {
                liCount: lis.length,
                scrollParent: scrollParent
            };
        }''')
        print('Playlist info on video page:', info)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())

