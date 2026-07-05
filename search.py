import requests

def search_ticker(query: str):
    """Search Yahoo Finance for a ticker."""
    url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=5&newsCount=0"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            quotes = data.get("quotes", [])
            results = []
            for q in quotes:
                if 'quoteType' in q and q['quoteType'] in ['EQUITY', 'ETF']:
                    results.append({
                        "symbol": q.get("symbol"),
                        "shortname": q.get("shortname", q.get("longname", "")),
                        "exchange": q.get("exchDisp", "")
                    })
            return results
    except Exception as e:
        print("Search error:", e)
    return []
