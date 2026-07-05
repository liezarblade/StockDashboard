const isLocal = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' || window.location.protocol === 'file:';
const API_BASE = isLocal ? "http://127.0.0.1:8000" : "https://stockdashboard-ioba.onrender.com";

const gridOptions = {
    columnDefs: [
        { 
            field: "Recommendation", 
            headerName: "Rec",
            width: 150,
            cellRenderer: (params) => {
                if (!params.value) return '';
                const conf = params.data.Confidence || 0;
                let colorClass = '';
                let icon = '';
                if (params.value === 'BUY') { colorClass = 'color-green'; icon = '🟢'; }
                else if (params.value === 'SELL') { colorClass = 'color-red'; icon = '🔴'; }
                else { colorClass = 'color-yellow'; icon = '🟡'; }
                
                return `<span class="${colorClass}">${icon} ${params.value} <span style="opacity:0.7; font-size:0.8em; margin-left:5px">${conf}%</span></span>`;
            }
        },
        { field: "Ticker", hide: true },
        { field: "Company", width: 250, filter: true },
        { 
            field: "Confidence", 
            headerName: "Score %",
            width: 120,
            filter: 'agNumberColumnFilter',
            sort: 'desc'
        },
        { field: "Price", width: 120, filter: 'agNumberColumnFilter' },
        { 
            field: "ChangePct", 
            headerName: "Change %",
            width: 120,
            cellRenderer: (params) => {
                if (params.value === undefined) return '';
                const isPos = params.value > 0;
                const color = isPos ? 'var(--buy-color)' : 'var(--sell-color)';
                const sign = isPos ? '+' : '';
                return `<span style="color: ${color}">${sign}${params.value}%</span>`;
            }
        },
        { field: "Volume", width: 120, filter: 'agNumberColumnFilter' },
        { field: "RSI", width: 100, filter: 'agNumberColumnFilter' },
        { field: "MACD", width: 100 },
        { field: "PSAR", width: 100 },
        { field: "Bollinger", width: 120 },
        { field: "Support", width: 120 },
        { field: "Resistance", width: 120 }
    ],
    defaultColDef: {
        sortable: true,
        filter: true,
        resizable: true,
    },
    rowData: [],
    rowSelection: 'single',
    getRowId: (params) => params.data.Ticker,
    onRowClicked: (event) => {
        if (window.openPanel) {
            window.openPanel(event.data.Ticker);
        }
    },
    animateRows: true
};

document.addEventListener('DOMContentLoaded', () => {
    const gridDiv = document.querySelector('#myGrid');
    new agGrid.Grid(gridDiv, gridOptions);
});

window.updateGridData = function(data) {
    gridOptions.api.setRowData(data);
};

window.applyGridTransaction = function(items) {
    if (gridOptions.api) {
        // If row doesn't exist, it will be added, if it does, it will be updated
        gridOptions.api.applyTransaction({ update: items, add: items });
        // Optionally resort after update
        gridOptions.api.refreshClientSideRowModel('sort');
    }
};
