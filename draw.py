from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import time
import json
import math

# 讀取選擇的股票列表
with open('E:\\程式教學\\selectStock\\selected_stocks.json', encoding='utf-8') as f:
    select_stock = json.load(f)

# 設置Chrome WebDriver的路徑
webdriver_path = 'E:\\程式教學\\selectStock\\chromedriver-win64\\chromedriver.exe'

# 設置啟動選項
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')  # 啟動時最大化視窗

# 每個Chrome實例最多打開的分頁數量
max_tabs_per_browser = 10

# 計算需要的Chrome實例數量
num_browsers = math.ceil(len(select_stock) / max_tabs_per_browser)

# 打開多個Chrome瀏覽器並分配股票技術分析頁面
browsers = []
for i in range(num_browsers):
    service = Service(webdriver_path)
    driver = webdriver.Chrome(service=service, options=options)
    browsers.append(driver)

    # 為當前的Chrome實例分配分頁
    start_index = i * max_tabs_per_browser
    end_index = min(start_index + max_tabs_per_browser, len(select_stock))
    for stock in select_stock[start_index:end_index]:
        url = f'https://www.fugle.tw/tradingview/{stock}'
        driver.execute_script(f"window.open('{url}', '_blank');")  # 使用JavaScript在新分頁中打開URL

# 等待一段時間以觀察打開的分頁
time.sleep(100000000)  # 可以根據需要調整等待時間

# 關閉所有WebDriver
for driver in browsers:
    driver.quit()
