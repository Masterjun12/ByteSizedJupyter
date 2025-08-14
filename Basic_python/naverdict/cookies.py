def load_cookies(page):
    try:
        with open("cookies.json", "r") as f:
            cookies = json.load(f)
        page.context.add_cookies(cookies)
        print("✅ 쿠키 로드 완료! 자동 로그인 유지됨.")
    except:
        print("❌ 쿠키 파일 없음! 수동 로그인 필요")
