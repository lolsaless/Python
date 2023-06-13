import requests
from bs4 import BeautifulSoup

# Naver 뉴스 검색 URL
url = "https://search.naver.com/search.naver?where=news&sm=tab_jum&query=chatGPT"

# HTTP GET 요청
response = requests.get(url)

# 응답 데이터의 HTML 파싱
soup = BeautifulSoup(response.text, 'html.parser')

# a.news_tit 요소 선택
news_tit_elements = soup.select('a.news_tit')

# 결과 출력
for news_tit_element in news_tit_elements:
    print(news_tit_element.text)
