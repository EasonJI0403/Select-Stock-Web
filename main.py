import twstock
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import math
from datetime import datetime, time as dt_time

# 取得股價資訊
def get_stock_data(ticker):
    try:
        stock = twstock.Stock(ticker)
        data = {
            'date': stock.date,
            'open': stock.open,
            'high': stock.high,
            'low': stock.low,
            'close': stock.close,
            'volume': stock.capacity
        }
        df = pd.DataFrame(data)
        return ticker, df
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return ticker, None

# 收下影線並收盤價與最低價的差大於最低價的 1%
def is_hammer(one):
    if (one['close'] < 150) and (one['close'] > one['low']) and (one['close'] - one['low'] >= one['low'] * 0.01):
        return True
    return False

# 當日最低價創五日新低
def lower(con_tinue):
    try:
        return con_tinue['low'].iloc[-1] == con_tinue['low'].rolling(window=5).min().iloc[-1]
    except IndexError:
        return False

# 股價小於 20MA
def ma(con_tinue):
    con_tinue['MA_long'] = con_tinue['close'].rolling(window=20).mean()
    return con_tinue['close'].iloc[-1] < con_tinue['MA_long'].iloc[-1]

# 紅K不超過 1%
def red(one):
    if one['open'] < one['close']:
        return one['close'] - one['open'] < one['open'] * 0.01
    return True

# 量能大於 100 張
def volume(one):
    return one['volume'] > 100000

# 執行選股
def process_stock(stockNum):
    ticker, con_tinue = get_stock_data(stockNum)
    if con_tinue is None or len(con_tinue) < 30:
        return None
    one = con_tinue.iloc[-1]
    if lower(con_tinue) and is_hammer(one) and ma(con_tinue) and red(one) and volume(one):
        return ticker
    return None

def select_stock():
    with open('stock.json', encoding='utf-8') as f:
        stock_collection = json.load(f)

    selected_stocks = []
    total_stocks = len(stock_collection)

    with ThreadPoolExecutor(max_workers=10) as executor:
        future_to_stock = {executor.submit(process_stock, stockNum): stockNum for stockNum in stock_collection}

        for i, future in enumerate(as_completed(future_to_stock), 1):
            stockNum = future_to_stock[future]
            try:
                result = future.result()
                if result:
                    selected_stocks.append(result)
                print(f"Processing {i}/{total_stocks}: {stockNum} completed")
            except Exception as e:
                print(f"Error processing {stockNum}: {e}")
    return selected_stocks

def main():
    selected_stocks = select_stock()
    print("選股結果：")
    print(selected_stocks)
    input("確認後按 Enter 繼續...")
    
    webdriver_path = 'E:\\程式教學\\selectStock\\chromedriver-win64\\chromedriver.exe'
    options = webdriver.ChromeOptions()
    options.add_argument('--start-maximized')

    max_tabs_per_browser = 10
    num_browsers = math.ceil(len(selected_stocks) / max_tabs_per_browser)
    browsers = []

    for i in range(num_browsers):
        service = Service(webdriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        browsers.append(driver)
        start_index = i * max_tabs_per_browser
        end_index = min(start_index + max_tabs_per_browser, len(selected_stocks))
        for j, stock in enumerate(selected_stocks[start_index:end_index]):
            url = f'https://histock.tw/stock/tchart.aspx?no={stock}'
            if j == 0:
                driver.get(url)  # 第一次呼叫 driver.get() 以顯示第一頁內容
            else:
                driver.execute_script(f"window.open('{url}', '_blank');")

    try:
        while any(driver.window_handles for driver in browsers):
            time.sleep(1)
    except Exception as e:
        print(f"Error while monitoring browser windows: {e}")
    finally:
        for driver in browsers:
            try:
                driver.quit()
            except Exception as e:
                print(f"Error while closing browser: {e}")

if __name__ == "__main__":
    main()
