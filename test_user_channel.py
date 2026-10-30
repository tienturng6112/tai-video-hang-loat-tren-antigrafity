import asyncio
import json
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
            viewport={'width': 1600, 'height': 900}
        )
        page = await context.new_page()
        
        post_items = []
        video_ids = set()

        async def on_resp(r):
            u = r.url
            if '/aweme/v1/web/aweme/post' in u:
                print(f'Intercepted POST API! Status: {r.status}')
                try:
                    data = await r.json()
                    aweme_list = data.get('aweme_list', [])
                    print(f'Received {len(aweme_list)} videos in aweme_list!')
                    post_items.extend(aweme_list)
                    for item in aweme_list:
                        video_ids.add(item.get('aweme_id'))
                except Exception as e:
                    print('Error parsing post JSON:', e)
            elif '/aweme/v1/web/user/profile' in u:
                print(f'Intercepted USER PROFILE API! Status: {r.status}')
                try:
                    data = await r.json()
                    user = data.get('user', {})
                    print('User nickname:', user.get('nickname'), 'aweme_count:', user.get('aweme_count'))
                except Exception as e:
                    print('Error parsing user profile JSON:', e)

        page.on('response', on_resp)

        # First visit video page or main page to warm up cookies
        print('Warming up cookies on video page...')
        await page.goto('https://www.douyin.com/video/7701656445934210319', wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(3000)
        
        user_url = 'https://www.douyin.com/user/MS4wLjABAAAAQsKgmnH7iih6NGtvCjC6eXjGLtsFMKeNLx1hqqDg1ZViKWUW4J8j8zi4eaMF0sci'
        print('Navigating to user channel:', user_url)
        await page.goto(user_url, wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(4000)
        
        title = await page.title()
        print('User page title:', title.encode('ascii', errors='replace').decode())
        
        # Check links on page
        hrefs = await page.evaluate('''() => {
            return Array.from(document.querySelectorAll('a[href]')).map(a => a.href);
        }''')
        for h in hrefs:
            m = re.search(r'/video/(\d+)', h)
            if m:
                video_ids.add(m.group(1))
                
        print(f'Currently captured unique video IDs: {len(video_ids)}')
        
        # Scroll a few times to see if pagination works
        for scroll_i in range(5):
            await page.mouse.wheel(0, 3000)
            await page.wait_for_timeout(1500)
            # check hrefs again
            more_hrefs = await page.evaluate('''() => {
                return Array.from(document.querySelectorAll('a[href]')).map(a => a.href);
            }''')
            for h in more_hrefs:
                m = re.search(r'/video/(\d+)', h)
                if m:
                    video_ids.add(m.group(1))
            print(f'After scroll {scroll_i+1}: captured {len(video_ids)} video IDs, total post_items: {len(post_items)}')

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())

