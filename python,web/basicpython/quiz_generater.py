import streamlit as st
import bardapi
import os
import googletrans
import pandas as pd
from bs4 import BeautifulSoup
import requests
import re
import datetime
from tqdm import tqdm
import sys
import uuid

os.environ['_BARD_API_KEY'] = "YQj0rPNxh8-NdDhzf-NgXqC9y2o38ln0-1i0nirGh8IA6QbiX9ERnSYRX_yhh_bhVrlAMw."

def makePgNum(num):
     if num == 1:
          return num
     elif num == 0:
          return num + 1
     else:
          return num + 9 * (num - 1)


# 크롤링할 url 생성하는 함수 만들기(검색어, 크롤링 시작 페이지, 크롤링 종료 페이지)

def makeUrl(search, start_pg, end_pg):
     if start_pg == end_pg:
          start_page = makePgNum(start_pg)
          url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + search + "&start=" + str(
               start_page)
          print("생성url: ", url)
          return url
     else:
          urls = []
          for i in range(start_pg, end_pg + 1):
               page = makePgNum(i)
               url = "https://search.naver.com/search.naver?where=news&sm=tab_pge&query=" + search + "&start=" + str(
                    page)
               urls.append(url)
          print("생성url: ", urls)
          return urls

     # html에서 원하는 속성 추출하는 함수 만들기 (기사, 추출하려는 속성값)


def news_attrs_crawler(articles, attrs):
     attrs_content = []
     for i in articles:
          attrs_content.append(i.attrs[attrs])
     return attrs_content


# ConnectionError방지
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/98.0.4758.102"}


# html생성해서 기사크롤링하는 함수 만들기(url): 링크를 반환
def articles_crawler(url):
     # html 불러오기
     original_html = requests.get(i, headers=headers)
     html = BeautifulSoup(original_html.text, "html.parser")

     url_naver = html.select(
          "div.group_news > ul.list_news > li div.news_area > div.news_info > div.info_group > a.info")
     url = news_attrs_crawler(url_naver, 'href')
     return url


#####뉴스크롤링 시작#####

st.title('AI 영어 지문 및 문제 생성기 ')
# 검색어 입력
search = st.text_input("검색할 키워드를 입력해주세요")
# 검색 시작할 페이지 입력
page = 1  # ex)1 =1페이지,2=2페이지...
# 검색 종료할 페이지 입력
page2 = 2  # ex)1 =1페이지,2=2페이지...

# naver url 생성
url = makeUrl(search, page, page2)

# 뉴스 크롤러 실행
news_titles = []
news_url = []
news_contents = []
news_dates = []
for i in url:
     url = articles_crawler(url)
     news_url.append(url)


# 제목, 링크, 내용 1차원 리스트로 꺼내는 함수 생성
def makeList(newlist, content):
     for i in content:
          for j in i:
               newlist.append(j)
     return newlist


# 제목, 링크, 내용 담을 리스트 생성
news_url_1 = []

# 1차원 리스트로 만들기(내용 제외)
makeList(news_url_1, news_url)

# NAVER 뉴스만 남기기
final_urls = []
for i in tqdm(range(len(news_url_1))):
     if "news.naver.com" in news_url_1[i]:
          final_urls.append(news_url_1[i])
     else:
          pass

# 뉴스 내용 크롤링

for i in tqdm(final_urls):
     # 각 기사 html get하기
     news = requests.get(i, headers=headers)
     news_html = BeautifulSoup(news.text, "html.parser")

     # 뉴스 제목 가져오기
     title = news_html.select_one("#ct > div.media_end_head.go_trans > div.media_end_head_title > h2")
     if title == None:
          title = news_html.select_one("#content > div.end_ct > div > h2")

     # 뉴스 본문 가져오기
     content = news_html.select("div#dic_area")
     if content == []:
          content = news_html.select("#articeBody")

     # 기사 텍스트만 가져오기
     # list합치기
     content = ''.join(str(content))

     # html태그제거 및 텍스트 다듬기
     pattern1 = '<[^>]*>'
     title = re.sub(pattern=pattern1, repl='', string=str(title))
     content = re.sub(pattern=pattern1, repl='', string=content)
     pattern2 = """[\n\n\n\n\n// flash 오류를 우회하기 위한 함수 추가\nfunction _flash_removeCallback() {}"""
     content = content.replace(pattern2, '')

     news_titles.append(title)
     news_contents.append(content)

     try:
          html_date = news_html.select_one(
               "div#ct> div.media_end_head.go_trans > div.media_end_head_info.nv_notrans > div.media_end_head_info_datestamp > div > span")
          news_date = html_date.attrs['data-date-time']
     except AttributeError:
          news_date = news_html.select_one("#content > div.end_ct > div > div.article_info > span > em")
          news_date = re.sub(pattern=pattern1, repl='', string=str(news_date))
     # 날짜 가져오기
     news_dates.append(news_date)

# 데이터 프레임 만들기
news_df = pd.DataFrame({'date': news_dates, 'title': news_titles, 'link': final_urls, 'content': news_contents})

# 중복 행 지우기
news_df = news_df.drop_duplicates(keep='first', ignore_index=True)

def convert_to_int(text):
    # 공백과 점을 제거한 문자열을 생성
    cleaned_text = ''.join(filter(lambda char: char.isdigit(), text))
    
    # 정수로 변환하여 반환
    try:
        result = int(cleaned_text[0])
        return result
    except ValueError:
        return None
   
# st.set_page_config(layout="wide")




# if "button_clicked" not in st.session_state:
#      st.session_state.button_clicked = False
#
# def callback():
#      st.session_state.button_clicked = True

# if (st.button("open next part", on_click=callback) or st.session_state.button_clicked):
#     if st.button("open  part"):
#         if st.button("open"):
#             st.write("나이스")

# 문자열 다듬기 -------------------------------------------------------------
news = []

for i in news_contents:
    for char in ['[', ']', '\\', 'n', '\"', '\'', '\n']:
        i = i.replace(char, '')
    news.append(i)



# 영어로 번역 ---------------------------------------------------------------
import googletrans

english_news = []

translator = googletrans.Translator()

for i in news:
     try:
          english_news.append(translator.translate(i, dest = 'en', src = 'auto').text)
     except AttributeError:
          pass

# 바드 ---------------------------------------------------------------------
os.environ['_BARD_API_KEY'] = "YQj0rPNxh8-NdDhzf-NgXqC9y2o38ln0-1i0nirGh8IA6QbiX9ERnSYRX_yhh_bhVrlAMw."

# input_text = f"다음 주제에 관련된 문제를 영어로 생성해주세요: {english_news[0]}. 이 문제는 4개의 보기를 포함해야 하며, 그중 정답은 1개여야 합니다. 그리고 출력 형태는 Question:who are you? Answer Choices:1. a. 2. b. 3. c. 4. d. Correct Answer: 4. d. 이런식으로 출력해주세요."
#
# response = bardapi.core.Bard().get_answer(input_text)['content']

# 문제 출력 -----------------------------------------------------------------

for idx, (date, title, new) in enumerate(zip(news_df["date"], news_df["title"], english_news)):
     if "button_clicked" not in st.session_state:
          st.session_state.button_clicked = False
     def callback(title=title, new=new):
          st.session_state.button_clicked = title, new
     


     if (st.button(title, on_click=callback) or st.session_state.button_clicked == (title, new)):
          if 'count' not in st.session_state:
               st.session_state.count = 1
          if st.session_state.count==1:

               input_text = f"Create a 4-point multiple-choice question based on the content of the {new}. This question must contain 4 options, and the correct answer must be 1. Each option should be a minimum of 20 characters and a maximum of 30 characters. The output format should be as follows: 'Question: Who are you? Choices: 1. a 2. b 3. c 4. d Answer: 4. d'. Please generate only one quiz concern. and don't show the correct answer in Choices"
               st.session_state.response = bardapi.core.Bard().get_answer(input_text)['content']
               st.session_state.count-=1
               st.write(st.session_state.response)
          
          st.write(date)
          st.write(new)
          
          # Question
          ques = st.session_state.response[st.session_state.response.find("Question:"):st.session_state.response.find("Choices:")].replace("\n\n",
                                                                                                      "").replace("**",
                                                                                                                  "")[
                st.session_state.response[st.session_state.response.find("Question:"):st.session_state.response.find("Choices:")].replace("\n\n",
                                                                                                      "").replace("**",
                                                                                                                  "").find(
                     ":") + 1:]
          
          st.write("Q.", ques)

          # Correct Answer -------------------------------------------------------------------------------------
          ans = st.session_state.response[
               st.session_state.response.find("Answer:") + len("Answer:"):st.session_state.response.find("\n", st.session_state.response.find("Answer:"))
               ].strip().replace("**", "")


          # Answer Choices -------------------------------------------------------------------------------
          afaf = st.session_state.response[
                 st.session_state.response.find("Choices:"):st.session_state.response.find(
                      "Answer:")].replace("**",
                                                      "").replace(
               "\n\n", "")[
                 st.session_state.response[
                 st.session_state.response.find("Choices:"):st.session_state.response.find(
                      "Answer:")].replace("**",
                                                      "").replace(
                      "\n\n", "").find(":") + 1:].replace("\n", "")

          one = afaf[:afaf.find("2.")]
          two = afaf[afaf.find("2."):afaf.find("3.")]
          three = afaf[afaf.find("3."):afaf.find("4.")]
          four = afaf[afaf.find("4."):]

          boxlist = [one, two, three, four]
          answer = [ans]
          myclick = []

          for idx, item in enumerate(boxlist):
               checked = st.checkbox(item, key=f"checkbox_{idx}_{item}")
               if checked:
                    myclick.append(item)

          st.write("ans", ans)
          st.write("myclick", myclick[0])

          # 정답 확인 및 결과 출력-----------------------------------------------------------------------
          if len(myclick) > 0:
               selected_item = myclick[0]
               st.write("선택한 항목:", selected_item)
               
               # selected_item과 answer[0]를 숫자로 변환하여 비교
               selected_number = convert_to_int(selected_item)
               st.write("선택한 변환:", selected_number)
               answer_number = convert_to_int(answer[0])
               st.write("답 변환:", answer_number)
               st.write(answer_number)
               if selected_number is not None and answer_number is not None:
                    if selected_number == answer_number:
                         st.balloons()
                         st.write("Correct ✅!")
                         st.session_state.count = 1
                    else:
                         st.write("Incorrect ❌")
                         st.write("Correct Answer:", answer_number)
                         st.session_state.count = 1
               else:
                    st.write("Not valid input")
                    st.session_state.count = 1
# 문제 출력 -----------------------------------------------------------------
# for idx, (date, title, new) in enumerate(zip(news_df["date"], news_df["title"], english_news)):
#
#      if "button_clicked" not in st.session_state:
#           st.session_state.button_clicked = False
#
#
#      def callback(title=title, new=new):
#           st.session_state.button_clicked = title, new
#
#
#      boxlist = ["A", "B", "C", "D"]
#      answer = ["B"]
#      myclick = []
#
#      if (st.button(title, on_click=callback) or st.session_state.button_clicked == (title, new)):
#           if 'count' not in st.session_state:
#                st.session_state.count = 1
#           if st.session_state.count==1:
#                # st.balloons()
#                st.session_state.count -= 1
#                # input_text = f"다음 주제에 관련된 문제를 영어로 생성해주세요: {new}. 이 문제는 4개의 보기를 포함해야 하며, 그중 정답은 1개여야 합니다. 그리고 출력 형태는 Question:who are you? Answer Choices:1. a. 2. b. 3. c. 4. d. Correct Answer: 4. d. 이런식으로 출력해주세요."
#                # response = bardapi.core.Bard().get_answer(input_text)['content']
#           st.write(date)
#           st.write(new)
#
#           for item in boxlist:
#                checked = st.checkbox(item, key=f"checkbox_{i}_{item}")
#                if checked:
#                     myclick.append(item)
#
#           # 정답 확인 및 결과 출력
#           if len(myclick) > 0:
#                selected_item = myclick[0]
#                st.write("선택한 항목:", selected_item)
#
#                if selected_item in answer:
#                     st.write("정답입니다!")
#                else:
#                     st.write("오답입니다!")
#                     st.write("정답:", answer[0])