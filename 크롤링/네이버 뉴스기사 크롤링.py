import time
import pandas as pd
from selenium.common.exceptions import NoSuchElementException
from selenium import webdriver
from selenium.webdriver.common.by import By

def safe_find_element(driver, by, value):
    try:
        return driver.find_element(by, value)
    except NoSuchElementException:
        return None

def news_scraping(news_url, driver):
    press_element = safe_find_element(driver, By.XPATH, '//*[@id="ct"]/div[1]/div[1]/a/img[2]')
    press = press_element.get_attribute('title') if press_element else ""

    title_element = safe_find_element(driver, By.ID, 'title_area')
    title = title_element.text if title_element else ""

    date_time_element = safe_find_element(driver, By.XPATH, '//*[@id="ct"]/div[1]/div[3]/div[1]/div[2]/span')
    date_time = date_time_element.text if date_time_element else ""

    repoter_element = safe_find_element(driver, By.XPATH, '//*[@id="JOURNALIST_CARD_LIST"]/div[1]/div/div[1]/div/div/div[1]/a[2]/span/span/em')
    repoter = repoter_element.text if repoter_element else ""

    article_element = safe_find_element(driver, By.ID, 'dic_area')
    article = article_element.text.replace("\n", "").replace("\t", "") if article_element else ""

    useful_element = safe_find_element(driver, By.XPATH, '//*[@id="likeItCountViewDiv"]/ul/li[1]/a/span[2]')
    useful = useful_element.text if useful_element else ""

    wow_element = safe_find_element(driver, By.XPATH, '//*[@id="likeItCountViewDiv"]/ul/li[2]/a/span[2]')
    wow = wow_element.text if wow_element else ""

    touched_element = safe_find_element(driver, By.XPATH, '//*[@id="likeItCountViewDiv"]/ul/li[3]/a/span[2]')
    touched = touched_element.text if touched_element else ""

    analytical_element = safe_find_element(driver, By.XPATH, '//*[@id="likeItCountViewDiv"]/ul/li[4]/a/span[2]')
    analytical = analytical_element.text if analytical_element else ""

    recommend_element = safe_find_element(driver, By.XPATH, '//*[@id="likeItCountViewDiv"]/ul/li[5]/a/span[2]')
    recommend = recommend_element.text if recommend_element else ""

    print("뉴스:", [title, press, date_time, repoter, article, useful, wow, touched, analytical, recommend, news_url])

    return [title, press, date_time, repoter, article, useful, wow, touched, analytical, recommend, news_url]

def scraping(urls):
    driver.implicitly_wait(3)

    news_idx = 0
    news_df = pd.DataFrame(columns=("Title", "Press", "DateTime", "Repoter", "Article", "Useful", "Wow", "Touched", "Analytical", "Recommend", "URL"))

    for url in urls:
        driver.get(url)
        news_df.loc[news_idx] = news_scraping(url, driver)
        news_idx += 1

    driver.close()

    return news_df

def make_pg_num(num):
    """Calculate the page number in the format required by the website."""
    return num if num == 1 else num+9*(num-1)

def create_url(search, page_num):
    """Create a URL with the search term and page number."""
    return f"https://search.naver.com/search.naver?where=news&sm=tab_pge&query={search}&sort=0&photo=0&field=0&pd=0&ds=&de=&cluster_rank=17&mynews=0&office_type=0&office_section_code=0&news_office_checked=&nso=so:r,p:all,a:all&start={page_num}"

def make_urls(search, start_pg, end_pg):
    """Generate the URLs for the range of pages."""
    return [create_url(search, make_pg_num(i)) for i in range(start_pg, end_pg+1)]

def input_with_validation(prompt):
    """Ask for input with the given prompt, repeating until a valid integer is provided."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Invalid input, please enter an integer.")

def main():
    search = input("검색할 키워드를 입력해주세요: ")

    start_pg = input_with_validation("\n크롤링할 시작 페이지를 입력해주세요. ex)1(숫자만입력): ")
    print(f"\n크롤링할 시작 페이지: {start_pg}페이지")

    end_pg = input_with_validation("\n크롤링할 종료 페이지를 입력해주세요. ex)1(숫자만입력): ")
    print(f"\n크롤링할 종료 페이지: {end_pg}페이지")

    return make_urls(search, start_pg, end_pg)

if __name__ == "__main__":
    search_urls = main()
    print("생성된 URL들: ", search_urls)


#Chrome drive option 설정
chrome_options = webdriver.ChromeOptions()

chrome_options.add_argument('--verbose')
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--windows-size=1920, 1200')
chrome_options.add_argument('--disable-dev-shm-usage')

driver = webdriver.Chrome(options = chrome_options)

import requests
from bs4 import BeautifulSoup
import time

# Initialize the list to store the links
list_url = []

# Iterate over the URLs
for url in search_urls:
    # Send GET request to the web page
    response = requests.get(url)

    # If the request is successful, extract the HTML content and create a BeautifulSoup object
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        links = soup.select("a.info")

        # Filter and save the links with "naver.com" in their address
        for link in links:
            href = link.get("href")
            if "naver.com" in href:
                list_url.append(href)
    else:
        print("The request failed.")

    # Sleep for 1 second
    time.sleep(2)

    scraping(list_url)