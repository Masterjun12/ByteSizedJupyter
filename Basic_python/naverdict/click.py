from playwright.sync_api import sync_playwright
import time

URL = "https://dic.daum.net/word/view.do?wordid=ekw000138780&q=relative"  # 원하는 URL로 변경

def check_and_click_button(page):
    """ 버튼이 존재하면 클릭하고, 없으면 기다린다. """
    button_selector = 'a[name="addToDefaultWordbook"]'

    try:
        button = page.locator(button_selector)
        if button.count() > 0:
            print("✅ 버튼 발견! 클릭합니다.")
            button.click()
            time.sleep(1)  # 클릭 후 잠시 대기
        else:
            print("❌ 버튼 없음. 기다리는 중...")
    except Exception as e:
        print(f"⚠️ 오류 발생: {e}")

def main():
    print("🚀 Playwright 실행 중...")
    p = sync_playwright().start()  # Playwright 수동 시작 (with 블록 X)
    browser = p.chromium.launch(headless=False)  # 브라우저 실행
    context = browser.new_context()
    page = context.new_page()
    
    print(f"🔗 {URL} 로 이동 중...")
    try:
        page.goto(URL, timeout=60000)  # 60초 동안 페이지 로딩 기다림
    except Exception as e:
        print(f"⚠️ 페이지 이동 중 오류 발생: {e}")

    while True:
        try:
            check_and_click_button(page)  # 버튼 확인 후 클릭

            # 새로 열린 페이지 감지 후 전환
            new_pages = context.pages
            if len(new_pages) > 1:
                print("🆕 새 페이지 감지! 전환 중...")
                page = new_pages[-1]  # 가장 최근 열린 페이지로 변경
            
            time.sleep(3)  # 3초마다 버튼 확인
            page.wait_for_load_state("domcontentloaded", timeout=60000)  # 로딩 완료까지 대기

        except Exception as e:
            print(f"⚠️ 메인 루프 오류 발생: {e}")

if __name__ == "__main__":
    main()
