from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import pandas as pd
from datetime import datetime

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)

def fetch_articles(url, article_class_name, date_class_name):
    driver.get(url)
    time.sleep(5)
    articles = driver.find_elements(By.CLASS_NAME, article_class_name)
    results = []
    for article in articles:
        title = article.find_element(By.TAG_NAME, "h1 class").text  # 根據實際HTML結構修改
        link = article.find_element(By.TAG_NAME, "a").get_attribute("href")
        date_str = article.find_element(By.CLASS_NAME, date_class_name).text  # 根據實際HTML結構修改
        date = datetime.strptime(date_str, "%Y-%m-%d")  # 根據實際日期格式修改
        if date >= datetime(2024, 4, 1) and date <= datetime(2024, 6, 30):
            results.append({"title": title, "link": link, "date": date})
    return results
# print(fetch_articles)
# # line_today_url = "https://today.line.me/tw/v3/tab/finance"
# # line_articles = fetch_articles(line_today_url, "headline", "datePublished")  # 修改為實際的類名

finet_dog_url = "https://statementdog.com/news"
finet_articles = fetch_articles(finet_dog_url, "main-news-title", "main-news-time")  # 修改為實際的類名

components = ["台積電", "鴻海", "聯發科","台達電","廣達","中信金","富邦金","聯電","日月光投控","國泰金" ,"兆豐金" ,"中華電","玉山金","統一","元大金","聯詠","華碩","永豐金","第一金","緯創", "智邦","大立光","國巨","合庫金","中鋼","華南金","瑞昱","南亞","開發金","緯穎","台泥","台新金","欣興","光寶科","奇鋐","台塑","和碩","和泰車","世芯-KY","長榮","研華","台灣大","上海商銀","台化","遠傳","統一超","亞德客-KY","中租-KY","台塑化","南亞科"]  # 根據實際成分股修改

related_articles = []
for article in finet_articles:
# for article in line_articles + finet_articles:
    for component in components:
        if component in article["title"]:
            related_articles.append(article)

for article in related_articles:
    print(f"Title: {article['title']}, Link: {article['link']}, Date: {article['date']}")

df = pd.DataFrame(related_articles)
df.to_csv("related_articles.csv", index=False)
print(related_articles)

