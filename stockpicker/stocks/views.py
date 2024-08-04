from django.shortcuts import render
from django.http import JsonResponse
import twstock
import pandas as pd
from datetime import datetime

def index(request):
    return render(request, 'index.html')

def get_data(request):
    ticker = '6125'  
    stock = twstock.Stock(ticker)

    # 获取最近一个月的交易数据
    df = pd.DataFrame(stock.fetch_from(2023 , 1))

    # 保留需要的列並重命名以符合 Lightweight Charts 的格式
    df = df[['date', 'open', 'high', 'low', 'close', 'capacity']]
    df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
    df['Volume'] = df['Volume'] / 1000
    df['Date'] = df['Date'].astype(str)

    data_json = {
        'name': ticker,
        'data': df.to_dict(orient='records')
    }
    return JsonResponse(data_json, safe=False)
