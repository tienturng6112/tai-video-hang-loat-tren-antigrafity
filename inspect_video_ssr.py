import asyncio
import json
import re
from playwright.async_api import async_playwright

async def inspect():
    with open('cookies.json', 'r', encoding='utf-8') as f:
        cookie_dict = json.load(f)
    cookies = [{'name': k, 'value': v, 'domain': '.douyin.com', 'path': '/'} for k, v in cookie_dict.items()]

    vid = '7680133883844775168'
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        ctx = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800}
        )
        await ctx.add_cookies(cookies)
        page = await ctx.new_page()
        await page.goto(f'https://www.douyin.com/video/{vid}', wait_until='domcontentloaded')
        html = await page.content()
        print('HTML len:', len(html))

        scripts = re.findall(r'<script id="([^"]+)"[^>]*>(.*?)</script>', html, re.DOTALL)
        print('Found script IDs:', [s[0] for s in scripts])
        for sid, content in scripts:
            if any(k in sid.lower() for k in ['render', 'data', 'router', 'state']):
                print(f'Script {sid}: len={len(content)}, preview={content[:150]}')
                with open(f'script_{sid}.txt', 'w', encoding='utf-8') as sf:
                    sf.write(content)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(inspect())

