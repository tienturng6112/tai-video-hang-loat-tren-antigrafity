import json
import httpx
from urllib.parse import urlencode, parse_qs, urlparse
import sys
sys.path.append('douyin_tool')

from utils.abogus import ABogus

with open('fresh_cookies.json', 'r', encoding='utf-8') as f:
    cookie_dict = json.load(f)

cookie_str = '; '.join(f'{k}={v}' for k, v in cookie_dict.items() if k)

with open('captured_post_req.json', 'r', encoding='utf-8') as f:
    req = json.load(f)

orig_url = req['url']
parsed = urlparse(orig_url)
qs = {k: v[0] for k, v in parse_qs(parsed.query).items()}

qs.pop('a_bogus', None)

base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
user_agent = req['headers'].get('user-agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36')

query_str = urlencode(qs)
signer = ABogus(user_agent=user_agent)
params_with_ab, abogus, ua, _ = signer.generate_abogus(query_str, '')

target_url = f"{base_url}?{params_with_ab}"
print('Signed target URL (prefix):', target_url[:120])

headers = dict(req['headers'])
headers['cookie'] = cookie_str
headers['user-agent'] = ua

with httpx.Client(headers=headers, timeout=20.0, follow_redirects=True) as client:
    r = client.get(target_url)
    print('Status code:', r.status_code)
    print('Content-Type:', r.headers.get('content-type'))
    print('Body length:', len(r.text))
    try:
        data = r.json()
        items = data.get('aweme_list', [])
        print(f'SUCCESS! Got {len(items)} items! has_more={data.get("has_more")}, cursor={data.get("max_cursor")}')
    except Exception as e:
        print('Not JSON. First 200 chars:', r.text[:200])
