import asyncio
import json
from urllib.parse import parse_qs, urlparse
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

        captured_request = {}

        def on_req(r):
            if '/aweme/v1/web/aweme/post' in r.url:
                captured_request['url'] = r.url
                captured_request['headers'] = r.headers
                captured_request['method'] = r.method
                print('Captured POST request!')
                print('URL:', r.url)

        page.on('request', on_req)

        await page.goto('https://www.douyin.com/video/7701656445934210319', wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(3000)

        user_url = 'https://www.douyin.com/user/MS4wLjABAAAAQsKgmnH7iih6NGtvCjC6eXjGLtsFMKeNLx1hqqDg1ZViKWUW4J8j8zi4eaMF0sci'
        await page.goto(user_url, wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(6000)

        with open('captured_post_req.json', 'w', encoding='utf-8') as f:
            json.dump(captured_request, f, ensure_ascii=False, indent=2)

        # Now test: Can page.evaluate fetch with the same URL but different max_cursor?
        url = captured_request.get('url', '')
        if url:
            print('Testing in-browser fetch for next cursor...')
            # replace max_cursor=0 with max_cursor=1790416834000
            import re
            next_url = re.sub(r'max_cursor=\d+', 'max_cursor=1790416834000', url)
            fetch_res = await page.evaluate(f'''async () => {{
                try {{
                    const resp = await fetch("{next_url}", {{
                        headers: {{
                            "accept": "application/json, text/plain, */*"
                        }}
                    }});
                    const data = await resp.json();
                    return {{
                        status: resp.status,
                        itemCount: (data.aweme_list || []).length,
                        has_more: data.has_more,
                        next_cursor: data.max_cursor
                    }};
                }} catch (e) {{
                    return {{ error: e.toString() }};
                }}
            }}''')
            print('In-browser fetch result for page 2:', fetch_res)

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())

