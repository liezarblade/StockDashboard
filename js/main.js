document.addEventListener('DOMContentLoaded', () => {
    loadStocks();
    
    document.getElementById('refresh-btn').addEventListener('click', () => {
        fetch(`${API_BASE}/refresh`, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                console.log("Refresh triggered", data);
            });
    });
    
    setupSearch();
    setupWebSocket();
});

function loadStocks() {
    fetch(`${API_BASE}/stocks`)
        .then(res => res.json())
        .then(data => {
            if (window.updateGridData && data.length > 0) {
                data.sort((a, b) => b.Confidence - a.Confidence);
                window.updateGridData(data);
            }
        });
}

function setupWebSocket() {
    let wsUrl = '';
    if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
        wsUrl = 'ws://127.0.0.1:8000/ws';
    } else {
        wsUrl = 'wss://stockdashboard-ioba.onrender.com/ws';
    }
    
    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
        console.log("WebSocket connected. Listening for live updates.");
    };
    
    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (window.applyGridTransaction) {
            window.applyGridTransaction([data]);
        }
    };
    
    ws.onclose = () => {
        console.log("WebSocket disconnected. Reconnecting in 5s...");
        setTimeout(setupWebSocket, 5000);
    };
}

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
                                searchInput.value = '';
                                dropdown.style.display = 'none';
                                if (window.openPanel) {
                                    window.openPanel(item.symbol);
                                }
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
