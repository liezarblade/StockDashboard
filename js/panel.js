let chart = null;
let lineSeries = null;

document.addEventListener('DOMContentLoaded', () => {
    const sidePanel = document.getElementById('side-panel');
    const closeBtn = document.getElementById('close-panel');
    
    closeBtn.addEventListener('click', () => {
        sidePanel.classList.remove('open');
        document.querySelector('.grid-wrapper').style.marginRight = '0';
    });
});

window.openPanel = async function(ticker) {
    const sidePanel = document.getElementById('side-panel');
    const gridWrapper = document.querySelector('.grid-wrapper');
    
    // Slide out
    sidePanel.classList.add('open');
    gridWrapper.style.marginRight = '500px'; // Push grid left
    
    // Fetch data
    try {
        const response = await fetch(`${API_BASE}/stock/${ticker}`);
        const data = await response.json();
        populatePanel(data);
    } catch (e) {
        console.error("Error fetching stock details", e);
    }
};

function populatePanel(data) {
    document.getElementById('panel-company').textContent = data.Company;
    document.getElementById('panel-ticker').textContent = data.Ticker;
    document.getElementById('panel-price').textContent = `₹${data.Price}`;
    
    const changeEl = document.getElementById('panel-change');
    changeEl.textContent = `${data.ChangePct > 0 ? '+' : ''}${data.ChangePct}%`;
    changeEl.style.color = data.ChangePct > 0 ? 'var(--buy-color)' : 'var(--sell-color)';
    
    const recEl = document.getElementById('panel-rec');
    recEl.textContent = data.Recommendation;
    if (data.Recommendation === 'BUY') {
        recEl.style.backgroundColor = 'var(--buy-color)';
        recEl.style.color = '#fff';
    } else if (data.Recommendation === 'SELL') {
        recEl.style.backgroundColor = 'var(--sell-color)';
        recEl.style.color = '#fff';
    } else {
        recEl.style.backgroundColor = 'var(--hold-color)';
        recEl.style.color = '#fff';
    }
    
    document.getElementById('panel-conf').textContent = `${data.Confidence}%`;
    
    // Indicators
    document.getElementById('panel-rsi').textContent = data.RSI;
    document.getElementById('panel-macd').textContent = data.MACD;
    document.getElementById('panel-psar').textContent = data.PSAR;
    
    document.getElementById('panel-support').textContent = data.Support;
    document.getElementById('panel-resistance').textContent = data.Resistance;
    document.getElementById('panel-bollinger').textContent = data.Bollinger;
    
    // Fibonacci
    if (data.Fibonacci) {
        document.getElementById('panel-fib-0').textContent = data.Fibonacci["0%"];
        document.getElementById('panel-fib-23').textContent = data.Fibonacci["23.6%"];
        document.getElementById('panel-fib-38').textContent = data.Fibonacci["38.2%"];
        document.getElementById('panel-fib-50').textContent = data.Fibonacci["50%"];
        document.getElementById('panel-fib-61').textContent = data.Fibonacci["61.8%"];
        document.getElementById('panel-fib-100').textContent = data.Fibonacci["100%"];
    }
    
    // Render Chart
    renderChart(data.ChartData);
}

function renderChart(data) {
    const container = document.getElementById('chart-container');
    
    if (!chart) {
        const theme = document.documentElement.getAttribute('data-theme');
        const isDark = theme === 'dark';
        
        chart = LightweightCharts.createChart(container, {
            width: container.clientWidth,
            height: container.clientHeight,
            layout: {
                backgroundColor: isDark ? '#1A242F' : '#FFFFFF',
                textColor: isDark ? '#d1d4dc' : '#000000',
            },
            grid: {
                vertLines: { color: isDark ? '#2B3139' : '#e1e3ea' },
                horzLines: { color: isDark ? '#2B3139' : '#e1e3ea' },
            },
            rightPriceScale: {
                borderVisible: false,
            },
            timeScale: {
                borderVisible: false,
            },
        });
        lineSeries = chart.addLineSeries({
            color: '#00A8E1',
            lineWidth: 2,
        });
        
        // Resize observer
        new ResizeObserver(entries => {
            if (entries.length === 0 || entries[0].target !== container) { return; }
            const newRect = entries[0].contentRect;
            chart.applyOptions({ height: newRect.height, width: newRect.width });
        }).observe(container);
    }
    
    if (data && data.length > 0) {
        lineSeries.setData(data);
        chart.timeScale().fitContent();
    }
}
