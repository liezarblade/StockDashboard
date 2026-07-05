import json
import os
import concurrent.futures
from indicators import fetch_and_calculate

CACHE_FILE = "data/cache.json"

DEFAULT_STOCKS = ["ITC.NS", "RELIANCE.NS", "BEL.NS", "HAL.NS", "INFY.NS"]

def get_all_stocks():
    if not os.path.exists(CACHE_FILE):
        return []
    with open(CACHE_FILE, "r") as f:
        try:
            data = json.load(f)
            return list(data.values())
        except json.JSONDecodeError:
            return []

def get_stock_data(ticker: str):
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            try:
                data = json.load(f)
                if ticker in data:
                    return data[ticker]
            except json.JSONDecodeError:
                pass
    
    result = fetch_and_calculate(ticker)
    if result:
        update_cache(ticker, result)
        return result
    return {"error": "Failed to fetch data"}

def update_cache(ticker: str, data: dict):
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            try:
                cache = json.load(f)
            except json.JSONDecodeError:
                pass
    cache[ticker] = data
    os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=4)

def refresh_all_stocks():
    cache = {}
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            try:
                cache = json.load(f)
            except json.JSONDecodeError:
                pass
    
    tickers_to_refresh = list(cache.keys())
    if not tickers_to_refresh:
        tickers_to_refresh = DEFAULT_STOCKS
    
    new_data = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ticker = {executor.submit(fetch_and_calculate, t): t for t in tickers_to_refresh}
        for future in concurrent.futures.as_completed(future_to_ticker):
            t = future_to_ticker[future]
            try:
                data = future.result()
                if data:
                    new_data[t] = data
            except Exception as e:
                print(f"Error refreshing {t}: {e}")
                
    if new_data:
        for t, d in new_data.items():
            cache[t] = d
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump(cache, f, indent=4)

def init_cache():
    if not os.path.exists(CACHE_FILE) or os.path.getsize(CACHE_FILE) == 0:
        refresh_all_stocks()
