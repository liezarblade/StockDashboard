const API_BASE = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://127.0.0.1:8000' 
    : 'https://stockdashboard-ioba.onrender.com';

let chart = null;
let lineSeries = null;

document.addEventListener('DOMContentLoaded', () => {
    setupSearch();
    initChart();
});

function setupSearch() {
    const searchInput = document.getElementById('search-input');
    const dropdown = document.getElementById('search-dropdown');
    
    let debounceTimer;
    
    searchInput.addEventListener('input', (e) => {
        clearTimeout(debounceTimer);
        const query = e.target.value.trim();
        
        if (query.length < 2) {
            dropdown.style.display = 'none';
            return;
        }
        
        debounceTimer = setTimeout(() => {
            fetch(`${API_BASE}/search?query=${query}`)
                .then(res => res.json())
                .then(results => {
                    dropdown.innerHTML = '';
                    if (results.length > 0) {
                        dropdown.style.display = 'block';
                        results.forEach(item => {
                            const div = document.createElement('div');
                            div.className = 'dropdown-item';
                            div.textContent = `${item.shortname || item.symbol} (${item.symbol})`;
                            div.onclick = () => {
                                searchInput.value = item.symbol;
                                dropdown.style.display = 'none';
                                loadStockData(item.symbol);
                            };
                            dropdown.appendChild(div);
                        });
                    } else {
                        dropdown.style.display = 'none';
                    }
                });
        }, 500);
    });
    
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-container')) {
            dropdown.style.display = 'none';
        }
    });
}

function initChart() {
    const chartContainer = document.getElementById('chart-container');
    chart = LightweightCharts.createChart(chartContainer, {
        layout: {
            background: { type: 'solid', color: 'transparent' },
            textColor: '#d1d4dc',
        },
        grid: {
            vertLines: { color: 'rgba(42, 46, 57, 0.5)' },
            horzLines: { color: 'rgba(42, 46, 57, 0.5)' },
        },
        rightPriceScale: {
            borderVisible: false,
        },
        timeScale: {
            borderVisible: false,
        },
    });

    lineSeries = chart.addLineSeries({
        color: '#E50914', // Netflix Red
        lineWidth: 2,
    });
    
    window.addEventListener('resize', () => {
        chart.resize(chartContainer.clientWidth, 400);
    });
}

function loadStockData(ticker) {
    document.getElementById('welcome-message').style.display = 'none';
    document.getElementById('stock-details').style.display = 'block';
    
    // Show loading state
    document.getElementById('panel-ticker').textContent = 'Loading...';
    
    fetch(`${API_BASE}/stock/${ticker}`)
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                alert("Could not fetch data for this stock.");
                return;
            }
            
            document.getElementById('panel-ticker').textContent = data.Ticker;
            document.getElementById('panel-company').textContent = data.Company;
            document.getElementById('panel-price').textContent = `₹${data.Price.toFixed(2)}`;
            
            const changeEl = document.getElementById('panel-change');
            changeEl.textContent = `${data.ChangePct.toFixed(2)}%`;
            changeEl.className = data.ChangePct >= 0 ? 'change-pct color-green' : 'change-pct color-red';
            
            // Metrics
            const recEl = document.getElementById('panel-rec');
            recEl.textContent = data.Recommendation;
            recEl.className = `metric-value ${data.Recommendation === 'BUY' ? 'color-green' : (data.Recommendation === 'SELL' ? 'color-red' : 'color-yellow')}`;
            
            document.getElementById('panel-score').textContent = `${data.Confidence}%`;
            document.getElementById('panel-rsi').textContent = data.RSI;
            document.getElementById('panel-macd').textContent = data.MACD;
            document.getElementById('panel-ema').textContent = `₹${data.EMA_200}`;
            document.getElementById('panel-adx').textContent = data.ADX;
            document.getElementById('panel-bb').textContent = data.Bollinger;
            document.getElementById('panel-vol').textContent = data.Volume.toLocaleString();
            
            // Fib
            const fibs = data.Fibonacci;
            document.getElementById('fib-0').textContent = `₹${fibs["0%"]}`;
            document.getElementById('fib-23').textContent = `₹${fibs["23.6%"]}`;
            document.getElementById('fib-38').textContent = `₹${fibs["38.2%"]}`;
            document.getElementById('fib-50').textContent = `₹${fibs["50%"]}`;
            document.getElementById('fib-61').textContent = `₹${fibs["61.8%"]}`;
            document.getElementById('fib-100').textContent = `₹${fibs["100%"]}`;
            
            // Update Chart
            if (data.ChartData && data.ChartData.length > 0) {
                lineSeries.setData(data.ChartData);
                chart.timeScale().fitContent();
            }
        });
}
