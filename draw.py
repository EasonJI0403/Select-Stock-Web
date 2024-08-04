import twstock
from datetime import datetime, time as dt_time
import pandas as pd

ticker = "6125"

current_time = dt_time(12, 0)
start_time = dt_time(9, 0)  # 上午9點
end_time = dt_time(13, 30)  # 下午1點30分
stock = twstock.Stock(ticker)
if start_time <= current_time <= end_time:
    stock_realtime = twstock.realtime.get(ticker)
    s = stock_realtime["realtime"]
    print(s)
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
    df = df.drop(df.index[-1])
    df = pd.concat([df, df_realtime], ignore_index=True)
    print(df)