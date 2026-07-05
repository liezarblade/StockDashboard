document.addEventListener('DOMContentLoaded', () => {
    loadStocks();
    
    document.getElementById('refresh-btn').addEventListener('click', () => {
        fetch(`${API_BASE}/refresh`, { method: 'POST' })
            .then(res => res.json())
            .then(data => {
                console.log(data);
                // Optionally show a toast that refresh started
                setTimeout(loadStocks, 5000); // Check again after 5s
            });
    });
    
    setupSearch();
    
    // Auto-refresh every 15 seconds to load data as background thread finishes
    setInterval(loadStocks, 15000);
});

function loadStocks() {
    fetch(`${API_BASE}/stocks`)
        .then(res => res.json())
        .then(data => {
            if (window.updateGridData && data.length > 0) {
                window.updateGridData(data);
            }
        });
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
    
    // Close dropdown on click outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-container')) {
            dropdown.style.display = 'none';
        }
    });
}
