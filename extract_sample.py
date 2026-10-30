import asyncio
import json
import urllib.parse
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
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        url = 'https://www.douyin.com/video/7701656445934210319'
        await page.goto(url, wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(3000)
        content = await page.content()
        with open('page.html', 'w', encoding='utf-8') as f:
            f.write(content)
        print('Saved page.html, size:', len(content))
        await browser.close()
        
        m = re.search(r'id=["\']RENDER_DATA["\'][^>]*>(.*?)</script>', content, re.DOTALL)
        if m:
            raw = m.group(1).strip()
            decoded = urllib.parse.unquote(raw)
            data = json.loads(decoded)
            print('RENDER_DATA keys:', list(data.keys()))
            with open('render_data.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print('Saved render_data.json!')
        else:
            print('RENDER_DATA tag not matched by regex!')
            scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
            for s in scripts:
                if '7701656445934210319' in s and len(s) > 100:
                    print('Found script with video ID, len:', len(s))
                    with open('script_sample.txt', 'w', encoding='utf-8') as f:
                        f.write(s)
                    break

if __name__ == '__main__':
    asyncio.run(run())
