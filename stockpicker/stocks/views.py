from django.shortcuts import render 
from django.http import JsonResponse
import twstock
import pandas as pd
from .stock_selector import select_stock
from fugle_marketdata import RestClient
import datetime as d

key = "Njg1M2VkY2ItZjQ2NC00M2VjLTk5NjMtODFlMjA3YzA2NzdlIDY3NGQ3ZTRmLWZkNDktNGVkNy1iMTkyLTUzZDk4ODY4YzkwMw=="
client = RestClient(api_key = key)  # 輸入您的 API key

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
    return {
        "code": stock_code,
        "name": s.get('name', 'N/A'), # 族群
        "current_price": s.get('closePrice', 'N/A'),  # 歷史價格，取最後一個
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
        # 將數據轉換為 JSON 格式並返回
        data_json = {
            'name': ticker,
            'data': df.to_dict(orient='records')
        }
        return JsonResponse(data_json, safe=False)
    
    except Exception as e:
        return JsonResponse({'error': f"Error fetching data for {ticker}: {str(e)}"}, status=400)
