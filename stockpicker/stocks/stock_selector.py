import twstock
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

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
    return one['volume'] > 500000

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
    with open('E:\程式教學\selectStock\stockpicker\stocks\stock.json', encoding='utf-8') as f:
        stock_collection = json.load(f)

    selected_stocks = [] 
    total_stocks = len(stock_collection)

    with ThreadPoolExecutor(max_workers=3) as executor:
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
    # selected_stocks = ['3466', '3623', '5206', '5324', '5529', '1110', '1453', '1805', '1806', '1903', '2303', '2362', '2501', '2504', '2505', '2506', '2515', '2514', '2527', '2528', '2534', '2530', '2538', '2537', '2540', '2548', '2547', '2597', '2915', '3056', '5515', '5525', '5533', '8374', '8462', '9917', '9940', '9946']
    return selected_stocks