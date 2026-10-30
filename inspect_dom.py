import asyncio
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
        await page.goto('https://www.douyin.com/video/7701656445934210319', wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(3000)

        user_url = 'https://www.douyin.com/user/MS4wLjABAAAAQsKgmnH7iih6NGtvCjC6eXjGLtsFMKeNLx1hqqDg1ZViKWUW4J8j8zi4eaMF0sci'
        await page.goto(user_url, wait_until='domcontentloaded', timeout=20000)
        await page.wait_for_timeout(4000)

        data = await page.evaluate('''() => {
            const list = document.querySelectorAll('[data-e2e="user-post-list"] li');
            const elements = [];
            for (const el of document.querySelectorAll('*')) {
                const text = (el.innerText || '').trim();
                if (text.includes('暂无更多') || text.includes('加载中') || text.includes('到底了') || text.includes('作品') && text.length < 30) {
                    elements.push({ tag: el.tagName, class: el.className, text: text });
                }
            }
            return {
                postCount: list.length,
                elements: elements.slice(0, 10)
            };
        }''')
        print('Post list data:', data)
        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())

