import asyncio
import json
import os
import re
import httpx
from playwright.async_api import async_playwright

DOWNLOAD_DIR = r"T:\tải video hàng loạt\Downloaded\捣蛋暮暮"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

with open('fresh_cookies.json', 'r', encoding='utf-8') as f:
    cookie_dict = json.load(f)

cookies_payload = [
    {'name': k, 'value': v, 'domain': '.douyin.com', 'path': '/'}
    for k, v in cookie_dict.items() if k
]

def sanitize_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', '_', name).strip()

async def download_video(client: httpx.AsyncClient, video_url: str, filepath: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
        'Referer': 'https://www.douyin.com/'
    }
    async with client.stream('GET', video_url, headers=headers) as resp:
        if resp.status_code == 200:
            with open(filepath, 'wb') as f:
                async for chunk in resp.aiter_bytes(chunk_size=65536):
                    f.write(chunk)
            return True
        else:
            print(f'Download failed HTTP {resp.status_code} for {video_url[:60]}')
            return False

async def run():
    with open('target_videos.json', 'r', encoding='utf-8') as f:
        target_videos = json.load(f)

    # Test with first 3 videos
    test_targets = target_videos[:3]

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox']
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800}
        )
        await context.add_cookies(cookies_payload)
        page = await context.new_page()

        async with httpx.AsyncClient(timeout=120.0, follow_redirects=True) as http_client:
            for item in test_targets:
                vid = item['id']
                print(f'\n--- Processing video {vid} ---')
                captured_detail = {}

                async def on_resp(r):
                    if 'aweme/v1/web/aweme/detail' in r.url and r.status == 200:
                        try:
                            data = await r.json()
                            if 'aweme_detail' in data:
                                captured_detail['data'] = data['aweme_detail']
                        except Exception:
                            pass

                page.on('response', on_resp)

                video_page_url = f'https://www.douyin.com/video/{vid}'
                try:
                    await page.goto(video_page_url, wait_until='domcontentloaded', timeout=30000)
                    # wait up to 4s for detail response
                    for _ in range(8):
                        if 'data' in captured_detail:
                            break
                        await page.wait_for_timeout(500)
                except Exception as e:
                    print(f'Nav error for {vid}: {e}')

                detail = captured_detail.get('data')
                if not detail:
                    print(f'Could not capture detail for {vid}')
                    continue

                author = detail.get('author', {}).get('nickname', 'unknown')
                author_sec_uid = detail.get('author', {}).get('sec_uid', '')
                title = detail.get('desc', 'video').strip()
                print(f'Author: {author} ({author_sec_uid[:20]}...)')
                print(f'Title: {title[:60]}')

                if 'MS4wLjABAAAAQsKgmnH7iih6NGtvCjC6eXjGLtsFMKeNLx1hqqDg1ZViKWUW4J8j8zi4eaMF0sci' not in author_sec_uid:
                    print('Not this author! Skipping.')
                    continue

                # Find 1080p or highest bitrate
                video_obj = detail.get('video', {})
                bitrates = video_obj.get('bit_rate', [])
                selected_br = None
                for br in bitrates:
                    gear = br.get('gear_name', '')
                    if '1080' in gear:
                        selected_br = br
                        break
                if not selected_br and bitrates:
                    selected_br = bitrates[0]

                if not selected_br:
                    print('No bitrates found!')
                    continue

                play_urls = selected_br.get('play_addr', {}).get('url_list', [])
                if not play_urls:
                    print('No play URLs found!')
                    continue

                chosen_url = play_urls[0]
                gear_name = selected_br.get('gear_name', 'default')
                print(f'Quality chosen: {gear_name}, URL: {chosen_url[:60]}...')

                # Filename
                clean_title = sanitize_filename(title[:80])
                filename = f"{clean_title}_{vid}.mp4"
                filepath = os.path.join(DOWNLOAD_DIR, filename)

                print(f'Downloading to: {filename} ...')
                success = await download_video(http_client, chosen_url, filepath)
                if success:
                    size = os.path.getsize(filepath)
                    print(f'Successfully downloaded: {filename} ({size / 1024 / 1024:.2f} MB)')
                else:
                    print('Download failed!')

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())

