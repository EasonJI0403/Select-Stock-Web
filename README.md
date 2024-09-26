這是一個選股程式網頁，Demo：https://drive.google.com/file/d/1l-sg29qMCFLdvihf1JTbXuuVsw4Q7RRJ/view?usp=sharing (此Demo省略選股過程，著重在前端畫面)

選股條件為破底翻


使用技術如下
網頁：Python-Django、HTML、JavaScript、CSS

選股數據套件：TwStock，不使用yfinance是因為它的開高低收有很多小數點；不使用富果API是因為我是搜尋全市場的標的，這樣用太多API要錢。

前端報價及圖表：圖表是使用 Tradingview 的 Lightweight，圖表數據以及報價數據是串富果API，不繼續使用TwStock是因為速度太慢，使用API串接跑比較快(使用少量API不用錢)。
