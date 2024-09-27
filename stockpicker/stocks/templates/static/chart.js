
const chart = LightweightCharts.createChart(document.getElementById('chart'), {
    width: document.getElementById('chart').offsetWidth,
    height: 600,
    layout: {
        backgroundColor: '#FFFFFF',
        textColor: '#000',
    },
    grid: {
        vertLines: {
            color: '#e1e1e1',
        },
        horzLines: {
            color: '#e1e1e1',
        },
    },
});

window.addEventListener('resize', () => {
    chart.applyOptions({ width: document.getElementById('chart').offsetWidth });
});

const candlestickSeries = chart.addCandlestickSeries();

// 從後端獲取股價數據並更新圖表
function loadChart(ticker, name) {
    fetch(`/data/?ticker=${ticker}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(data.error);
                return;
            }
            document.querySelector('h1').textContent = `${ticker} ${name}`;  // 顯示股票代碼與名稱
            const chartData = data.data.map(item => ({
                time: new Date(item.Date).getTime() / 1000,  // 將日期轉換為 UNIX 時間戳
                open: item.Open,
                high: item.High,
                low: item.Low,
                close: item.Close,
            }));

            candlestickSeries.setData(chartData);
        })
        .catch(error => console.error('Error fetching data:', error));
}

// 從後端選股並顯示結果
function getSelectedStocks() {
    const selectButton = document.getElementById('select-button');
    const progressBar = document.getElementById('progress-bar');
    const tableBody = document.querySelector('#stock-results tbody');
    
    selectButton.disabled = true;  // 禁用按鈕
    selectButton.textContent = '選股中...';  // 修改按鈕文本
    progressBar.value = 0;  // 重置進度條
    tableBody.innerHTML = '';  // 清空之前的選股結果

    const eventSource = new EventSource('/select-stock/');

    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);

        if (data.status === 'processing') {
            progressBar.value = data.progress;

        } else if (data.status === 'completed') {
            // 顯示最終選股結果
            const selectedStocks = data.selected_stocks;
            selectedStocks.forEach(stock => {
                const row = document.createElement('tr');
                row.onclick = function() {
                    loadChart(stock.code, stock.name);  // 點擊時加載該股票的圖表
                };
                row.innerHTML = `
                    <td>${stock.code || 'N/A'}</td>
                    <td>${stock.name || 'N/A'}</td>
                    <td>${stock.current_price || 'N/A'}</td>
                `;
                tableBody.appendChild(row);
        });

        selectButton.disabled = false;
        selectButton.textContent = '開始選股';
        eventSource.close();
        }
    };

    eventSource.onerror = function(error) {
        console.error('Error in EventSource:', error);
        eventSource.close();
        selectButton.disabled = false;
        selectButton.textContent = '開始選股';
    };
}