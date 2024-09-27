from django.shortcuts import render 
from django.http import JsonResponse
import twstock
import pandas as pd
from .stock_selector import select_stock
from fugle_marketdata import RestClient
import datetime as d
import json, requests

key = "Njg1M2VkY2ItZjQ2NC00M2VjLTk5NjMtODFlMjA3YzA2NzdlIDY3NGQ3ZTRmLWZkNDktNGVkNy1iMTkyLTUzZDk4ODY4YzkwMw=="
client = RestClient(api_key = key)  # 輸入您的 API key

def get_historical_data(stock_no):
    html = requests.get('https://ws.api.cnyes.com/ws/api/v1/charting/history?resolution=D&symbol=TWS:%s:STOCK&from=1727395200&to=1686787200' %(stock_no))
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
    d = df_reversed.tail(1)
    return d

# 返回主頁面
def index(request):
    return render(request, 'index.html')  # 渲染首頁模板

# 選股功能 API
def select_stock_view(request):
    stock_codes = select_stock()  # 調用選股程式
    selected_stocks = [get_stock_info(code) for code in stock_codes]
    return JsonResponse({'selected_stocks': selected_stocks})  # 返回選股結果

def get_stock_info(stock_code):
    # 一個月前的日期
    stock = client.stock
    s = stock.historical.stats(symbol = stock_code)
    c = get_historical_data(stock_code)
    close_price = c['close'].values[0]
    return {
        "code": stock_code,
        "name": s.get('name', 'N/A'), # 族群
        "current_price": close_price,  # 歷史價格，取最後一個
    }

# 獲取動態股票數據的 API
def get_data(request):

    # 從 URL 中取得股票代碼，默認為 '2330'
    ticker = request.GET.get('ticker', '2330')
    to_date = d.date.today().strftime('%Y-%m-%d')
    from_date = (d.date.today() - d.timedelta(days=365)).strftime('%Y-%m-%d')
    stock = client.stock
    try:
        s = stock.historical.candles(**{"symbol": ticker, "from": from_date, "to": to_date, "fields": "open,high,low,close,volume,change"})
        stock = s['data']
        
        df = pd.DataFrame(stock)
        
        # 保留需要的列並重命名以符合圖表格式
        df = df[['date', 'open', 'high', 'low', 'close', 'volume']]
        df.columns = ['Date', 'Open', 'High', 'Low', 'Close', 'Volume']
        df['Volume'] = df['Volume'] / 1000  # 將成交量除以1000
        # df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')  # 將日期轉換為字符串格式
        df['Date'] = pd.to_datetime(df['Date'], format="%Y-%m-%d").dt.date
        
        df = df.sort_values(by='Date', ascending=True)

        last_row_data = get_historical_data(ticker)
        today_date = d.date.today()

        if df.iloc[-1]['Date'] != today_date:
            last_row_data['Date'] = today_date
            last_row_df = pd.DataFrame({
                'Date': [today_date],
                'Open': last_row_data['open'].values,
                'High': last_row_data['high'].values,
                'Low': last_row_data['low'].values,
                'Close': last_row_data['close'].values,
                'Volume': last_row_data['volume'].values
            })

            # 如果日期不同則合併最後一行數據
            df = pd.concat([df, last_row_df], ignore_index=True)

        # 將數據轉換為 JSON 格式並返回
        data_json = {
            'name': ticker,
            'data': df.to_dict(orient='records')
        }
        # print(data_json)
        return JsonResponse(data_json, safe=False)
    
    except Exception as e:
        return JsonResponse({'error': f"Error fetching data for {ticker}: {str(e)}"}, status=400)
