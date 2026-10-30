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

        # Open one video page first so browser loads all player and API scripts
        await page.goto('https://www.douyin.com/video/7701656445934210319', wait_until='domcontentloaded', timeout=40000)
        await page.wait_for_timeout(4000)

        # Test fetching details for another video ID directly in page context
        test_id = '7667534847249747263' # 置顶 我的宠物石头
        res = await page.evaluate(f'''async () => {{
            try {{
                // Find how xgplayer or page calls detail API
                const url = '/aweme/v1/web/aweme/detail/?device_platform=webapp&aid=6383&channel=channel_pc_web&aweme_id={test_id}&update_version_code=170400&pc_client_type=1&version_code=190500&version_name=19.5.0&cookie_enabled=true&screen_width=1600&screen_height=1000&browser_language=zh-CN&browser_platform=Win32&browser_name=Chrome&browser_version=133.0.0.0&browser_online=true&engine_name=Blink&engine_version=133.0.0.0&os_name=Windows&os_version=10&cpu_core_num=8&device_memory=8&platform=PC&downlink=10&effective_type=4g&round_trip_time=0';
                const r = await fetch(url);
                const data = await r.json();
                return {{
                    status: r.status,
                    desc: data.aweme_detail ? data.aweme_detail.desc : null,
                    video: !!(data.aweme_detail && data.aweme_detail.video)
                }};
            }} catch (e) {{
                return {{ error: e.toString() }};
            }}
        }}''')
        print('In-page fetch detail for another video:', res)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())

