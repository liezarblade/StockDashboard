import json
import os
import concurrent.futures
import threading
from indicators import fetch_and_calculate

CACHE_FILE = "data/cache.json"

DEFAULT_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", 
    "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "BAJFINANCE.NS", "KOTAKBANK.NS", 
    "LT.NS", "HINDUNILVR.NS", "AXISBANK.NS", "MARUTI.NS", "SUNPHARMA.NS", 
    "TITAN.NS", "ULTRACEMCO.NS", "ASIANPAINT.NS", "BAJAJFINSV.NS", "TATASTEEL.NS", 
    "HCLTECH.NS", "WIPRO.NS", "POWERGRID.NS", "NTPC.NS", "ONGC.NS", 
    "COALINDIA.NS", "INDUSINDBK.NS", "NESTLEIND.NS", "GRASIM.NS", "TECHM.NS", 
    "HINDALCO.NS", "JSWSTEEL.NS", "M&M.NS", "CIPLA.NS", "DRREDDY.NS", 
    "DIVISLAB.NS", "TATACONSUM.NS", "ADANIENT.NS", "ADANIPORTS.NS", "APOLLOHOSP.NS", 
    "BRITANNIA.NS", "EICHERMOT.NS", "HEROMOTOCO.NS", "BPCL.NS", "SHREECEM.NS", 
    "SBILIFE.NS", "HDFCLIFE.NS", "BAJAJ-AUTO.NS", "MARICO.NS", "UPL.NS",
    "PIDILITIND.NS", "GODREJCP.NS", "DABUR.NS", "SHRIRAMFIN.NS", "TVSMOTOR.NS",
    "CHOLAFIN.NS", "ICICIPRULI.NS", "TRENT.NS", "BANKBARODA.NS", "PNB.NS",
    "ZOMATO.NS", "JIOFIN.NS", "LICI.NS", "GAIL.NS", "DLF.NS",
    "VEDL.NS", "HAL.NS", "BEL.NS", "BHEL.NS", "INDIGO.NS",
    "SIEMENS.NS", "ABB.NS", "CUMMINSIND.NS", "BOSCHLTD.NS", "NAUKRI.NS",
    "MUTHOOTFIN.NS", "BAJAJHLDNG.NS", "HAVELLS.NS", "POLYCAB.NS", "CGPOWER.NS",
    "TATACHEM.NS", "TATAPOWER.NS", "JSWENERGY.NS", "LODHA.NS", "MAXHEALTH.NS",
    "TORNTPHARM.NS", "ZYDUSLIFE.NS", "ALKEM.NS", "LUPIN.NS", "AUROPHARMA.NS",
    "PIIND.NS", "COROMANDEL.NS", "PERSISTENT.NS", "COFORGE.NS", "MPHASIS.NS",
    "LTTS.NS", "OFSS.NS", "M&MFIN.NS", "PFC.NS", "RECLTD.NS"
]

on_stock_updated = None
cache_lock = threading.Lock()

def load_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            try:
                return json.load(f)
            except:
                pass
    return {}

MEMORY_CACHE = load_cache()

def get_all_stocks():
    with cache_lock:
        return list(MEMORY_CACHE.values())

def get_stock_data(ticker: str):
    with cache_lock:
        if ticker in MEMORY_CACHE:
            return MEMORY_CACHE[ticker]
            
    result = fetch_and_calculate(ticker)
    if result:
        update_cache(ticker, result)
        if on_stock_updated:
            on_stock_updated(result)
        return result
    return {"error": "Failed to fetch data"}

def update_cache(ticker: str, data: dict):
    with cache_lock:
        MEMORY_CACHE[ticker] = data
        os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
        with open(CACHE_FILE, "w") as f:
            json.dump(MEMORY_CACHE, f, indent=4)

def refresh_all_stocks():
    with cache_lock:
        tickers_to_refresh = list(MEMORY_CACHE.keys())
        
    if not tickers_to_refresh:
        tickers_to_refresh = DEFAULT_STOCKS
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_ticker = {executor.submit(fetch_and_calculate, t): t for t in tickers_to_refresh}
        for future in concurrent.futures.as_completed(future_to_ticker):
            t = future_to_ticker[future]
            try:
                data = future.result()
                if data:
                    update_cache(t, data)
                    if on_stock_updated:
                        on_stock_updated(data)
            except Exception as e:
                print(f"Error refreshing {t}: {e}")

def init_cache():
    if not MEMORY_CACHE:
        refresh_all_stocks()
