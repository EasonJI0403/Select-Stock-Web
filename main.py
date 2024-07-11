import twstock
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
import math
import winsound
from datetime import datetime, time as dt_time

# 取得股價資訊
def get_stock_data(ticker):
    try:
        stock = twstock.Stock(ticker)
        current_time = datetime.now().time()
        start_time = dt_time(9, 0)  # 上午9點
        end_time = dt_time(13, 30)  # 下午1點30分
        if start_time <= current_time <= end_time:
            stock_realtime = twstock.realtime.get(ticker)
            s = stock_realtime["realtime"]
            data_realtime = {
                'date': [stock_realtime['info']['time']],
                'open': [float(s['open'])],
                'high': [float(s['high'])],
                'low': [float(s['low'])],
                'close': [float(s['latest_trade_price'])],
                'volume': [int(s['accumulate_trade_volume'])*1000]
            }
            data = {
                'date': stock.date,
                'open': stock.open,
                'high': stock.high,
                'low': stock.low,
                'close': stock.close,
                'volume': stock.capacity
            }
            df = pd.DataFrame(data)
            df_realtime = pd.DataFrame(data_realtime)
            df = pd.concat([df, df_realtime], ignore_index=True)
            return ticker, df
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
    return one['close'] - one['low'] >= one['low'] * 0.01

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
            # if i % 200 == 0:
            #     time.sleep(60)
            try:
                result = future.result()
                if result:
                    selected_stocks.append(result)
                print(f"Processing {i}/{total_stocks}: {stockNum} completed")
            except Exception as e:
                print(f"Error processing {stockNum}: {e}")
    winsound.Beep(800, 2000)
    return selected_stocks

def main():
    selected_stocks = select_stock()
    # selected_stocks = select_stock()
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
        for stock in selected_stocks[start_index:end_index]:
            url = f'https://www.fugle.tw/tradingview/{stock}'
            driver.execute_script(f"window.open('{url}', '_blank');")

    time.sleep(1000000)
    for driver in browsers:
        driver.quit()

if __name__ == "__main__":
    main()
