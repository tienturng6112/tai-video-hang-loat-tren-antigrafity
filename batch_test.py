import json
import httpx
from playwright.sync_api import sync_playwright

with open('target_videos.json', 'r', encoding='utf-8') as f:
    items = json.load(f)

print(f'Total candidates in target_videos.json: {len(items)}')

# Filter author videos
# We can check detail for the first few
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
    'Referer': 'https://www.douyin.com/'
}

with open('fresh_cookies.json', 'r', encoding='utf-8') as f:
    cookie_dict = json.load(f)

print('Testing detail fetching...')

