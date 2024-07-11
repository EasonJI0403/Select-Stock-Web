import twstock
import pandas as pd
from datetime import datetime, time as dt_time
import winsound
# import json

# tickersAll = twstock.codes  # 取得所有上櫃股票代碼
# stock_realtime = twstock.realtime.get('2330')
# tickersFour = [] # 過濾代碼 4 位數的股票
# for ticker in tickersAll:
#     if len(ticker) == 4 and ticker.isdigit():
#         tickersFour.append(ticker)

# with open('stock.json', 'w', encoding='utf-8') as f:
#     json.dump(tickersFour, f, ensure_ascii=False, indent=4)

# twstock.__update_codes()
def get_stock_data(ticker):
    try:
        stock = twstock.Stock(ticker)
        current_time = dt_time(9, 12)
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
winsound.Beep(800, 2000)
print(get_stock_data("2330"))