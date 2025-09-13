from playwright.sync_api import sync_playwright
import json

def save_cookies():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False → 브라우저 창 띄움
        page = browser.new_page()
        
        page.goto("https://nid.naver.com/nidlogin.login")  # 네이버 로그인 페이지로 이동
        input("로그인 후 엔터를 눌러주세요...")  # 수동으로 로그인 후 진행
        
        cookies = page.context.cookies()  # 로그인 후 쿠키 저장
        with open("cookies.json", "w") as f:
            json.dump(cookies, f)
        
        print("✅ 쿠키 저장 완료!")
        browser.close()

save_cookies()
