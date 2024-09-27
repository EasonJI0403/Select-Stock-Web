import pandas as pd
import json, requests
from concurrent.futures import ThreadPoolExecutor, as_completed

# 取得股價資訊
def get_stock_data(ticker):
    try:
        html = requests.get('https://ws.api.cnyes.com/ws/api/v1/charting/history?resolution=D&symbol=TWS:%s:STOCK&from=1727395200&to=1686787200' %(ticker))
        content = json.loads(html.text)
        open = content['data']['o']
        high = content['data']['h']
        low = content['data']['l']
        close = content['data']['c']
        volume = content['data']['v']
        data = {
            'open': open,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        }
        df = pd.DataFrame(data=data)
        df_reversed = df.iloc[::-1]
        return ticker, df_reversed
    except Exception as e:
        print(f"Error fetching data for {ticker}: {e}")
        return ticker, None

# 收下影線並收盤價與最低價的差大於最低價的 1%
def is_hammer(one):
    if (one['close'] < 100) and (one['close'] > one['low']) and (one['close'] - one['low'] >= one['low'] * 0.01):
        return True
    return False

# 當日最低價創五日新低
def lower(con_tinue):
    try:
        # 如果這五天最低價就是今天最低價的話
        return con_tinue['low'].iloc[-1] == con_tinue['low'].rolling(window=5).min().iloc[-1]
    except IndexError:
        return False

# 股價小於 20MA
def ma(con_tinue):
    con_tinue['MA_long'] = con_tinue['close'].rolling(window=20).mean()
    return con_tinue['close'].iloc[-1] < con_tinue['MA_long'].iloc[-1]

# # 紅K不超過 1%
# def red(one):
#     if one['open'] < one['close']:
#         return one['close'] - one['open'] < one['open'] * 0.01
#     return Trueand red(one)

# 量能大於 100 張
def volume(one):
    return one['volume'] > 500

# 執行選股
def process_stock(stockNum):
    ticker, con_tinue = get_stock_data(stockNum)
    if con_tinue is None or len(con_tinue) < 30:
        return None
    one = con_tinue.iloc[-1] 
    if lower(con_tinue) and is_hammer(one) and ma(con_tinue)  and volume(one):
        return ticker
    return None

import time
def select_stock():
    s = time.time()
    with open('E:\程式教學\selectStock\stockpicker\stocks\stock.json', encoding='utf-8') as f:
        stock_collection = json.load(f)
    selected_stocks = [] 
    total_stocks = len(stock_collection)
    # 60是最快的
    with ThreadPoolExecutor(max_workers=60) as executor:
        future_to_stock = {executor.submit(process_stock, stockNum): stockNum for stockNum in stock_collection}

        for i, future in enumerate(as_completed(future_to_stock), 1):
            stockNum = future_to_stock[future]
            try:
                result = future.result()
                progress = (i / total_stocks) * 100
                if result:
                    selected_stocks.append(result)
                    yield {
                        "status": "processing",
                        "progress": progress,
                    }
                else:
                    yield {
                        "status": "processing",
                        "progress": progress,
                    }
                # print(f"Processing {i}/{total_stocks}: {stockNum} completed")
            except Exception as e:
                yield {
                    "status": "error",
                    "message": f"Error processing {stockNum}: {str(e)}"
                }
                print(f"Error processing {stockNum}: {e}")
    # selected_stocks = ['3466', '3623', '5206', '5324']
    e = time.time()
    # 最後回傳完整選股結果
    yield {
        "status": "completed",
        "selected_stocks": selected_stocks
    }