from playwright.sync_api import sync_playwright
import json
import time

BASE_URL = "https://learn.dict.naver.com/wordbook/enkodict/#/my/cards"
WB_ID = "3a5921f2c3a1403494cba32ff181c18d"
PAGE_START = 6


def load_cookies(page):
    """저장된 쿠키를 불러와 로그인 유지"""
    try:
        with open("cookies.json", "r") as f:
            cookies = json.load(f)
        page.context.add_cookies(cookies)
        print("✅ 쿠키 로드 완료! 자동 로그인 유지됨.")
    except:
        print("❌ 쿠키 파일 없음! 수동 로그인 필요")


def get_words_from_page(page, page_num):
    url = f"{BASE_URL}?wbId={WB_ID}&qt=0&st=0&name=%EC%95%94%EA%B8%B0&tab=list&page={page_num}"
    print(f"[이동 중] 페이지 {page_num}: {url}")
    page.goto(url)
    time.sleep(2)  # 페이지 로딩 대기

    words = page.eval_on_selector_all(
        "#section_word_card a.title",
        "elements => elements.map(e => ({'text': e.innerText.trim(), 'link': e.href}))"
    )

    print(f"[페이지 {page_num}] 단어 개수: {len(words)}")
    for word in words:
        print(f"[링크 찾음] {word['text']} → {word['link']}")

    return words


def get_english_word(page, word_link):
    print(f"[이동 중] 단어 페이지: {word_link}")
    page.goto(word_link)
    time.sleep(2)

    try:
        english_word = page.eval_on_selector("span.u_word_dic[data-hook='tip']", "e => e.innerText.trim()")
        print(f"[단어 찾음] {english_word}")  # 찾은 단어 출력
        return english_word if english_word else "[단어 없음]"
    except:
        print("[오류 발생] 단어를 찾을 수 없음")
        return "[오류 발생]"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False로 변경 (화면 확인 가능)
        page = browser.new_page()

        load_cookies(page)  # 쿠키 로드

        words_data = []
        page_num = PAGE_START

        while True:
            words = get_words_from_page(page, page_num)
            if not words:
                print("더 이상 단어가 없습니다. 크롤링 종료.")
                break

            for word in words:
                # 한국어 단어 그대로 저장
                korean_word = word['text']
                
                # 영어 단어 가져오기
                english_word = get_english_word(page, word['link'])
                
                # 단어 저장 (영어 단어가 못 찾아도 원래 단어 저장)
                words_data.append({"korean": korean_word, "english": english_word})

                print(f"[완료] {korean_word} → {english_word}")

            page_num += 1

        # JSON 파일로 저장
        with open("words.json", "w", encoding="utf-8") as f:
            json.dump(words_data, f, ensure_ascii=False, indent=4)

        print("모든 단어 수집 완료, words.json 저장됨.")
        browser.close()


if __name__ == "__main__":
    main()
