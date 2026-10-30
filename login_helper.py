import asyncio
import json
import os
from playwright.async_api import async_playwright

async def login():
    print("==================================================")
    print("  HƯỚNG DẪN ĐĂNG NHẬP DOUYIN ĐỂ QUÉT TOÀN BỘ KÊNH")
    print("  Trình duyệt Chrome sẽ mở ra.")
    print("  Bạn chỉ cần mở app Douyin trên điện thoại, quét mã QR (扫码登录)")
    print("  để đăng nhập. Hệ thống sẽ tự động bắt cookies và lưu lại.")
    print("==================================================")

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled']
        )
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36',
            viewport={'width': 1280, 'height': 800}
        )
        page = await context.new_page()
        await page.goto("https://www.douyin.com/", wait_until="domcontentloaded")

        print("Đang chờ bạn quét mã QR trên màn hình trình duyệt...")
        logged_in = False
        for _ in range(180): # wait up to 3 minutes
            cookies = await context.cookies()
            cookie_dict = {c['name']: c['value'] for c in cookies}
            if 'sessionid' in cookie_dict or 'sid_guard' in cookie_dict or 'sessionid_ss' in cookie_dict:
                print("\n[THÀNH CÔNG] Đã phát hiện đăng nhập thành công!")
                with open("cookies.json", "w", encoding="utf-8") as f:
                    json.dump(cookie_dict, f, ensure_ascii=False, indent=2)
                print("Đã lưu cookies vào cookies.json.")
                logged_in = True
                break
            await asyncio.sleep(1)

        if not logged_in:
            print("[CẢNH BÁO] Hết thời gian chờ đăng nhập (3 phút).")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(login())

