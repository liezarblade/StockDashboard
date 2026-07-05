import yfinance as yf
import pandas as pd
import ta
import numpy as np
from datetime import datetime

def calculate_confidence(price, rsi, macd, macd_signal, psar, bollinger_l, bollinger_h):
    score = 50 # Start neutral
    
    # RSI (0-100)
    if not pd.isna(rsi):
        if rsi < 30:
            score += 20
        elif rsi > 70:
            score -= 20
        elif rsi > 50:
            score += 5
        else:
            score -= 5
        
    # MACD
    if not pd.isna(macd) and not pd.isna(macd_signal):
        if macd > macd_signal:
            score += 15 # Bullish crossover
        else:
            score -= 15 # Bearish crossover
        
    # PSAR
    if not pd.isna(psar):
        if price > psar:
            score += 15 # Bullish
        else:
            score -= 15 # Bearish
        
    # Bollinger
    if not pd.isna(bollinger_l) and not pd.isna(bollinger_h):
        if price < bollinger_l:
            score += 10 # Bounced off lower
        elif price > bollinger_h:
            score -= 10 # Rejected at upper
        
    score = max(0, min(100, score)) # Clamp 0-100
    
    if score >= 65:
        rec = "BUY"
    elif score <= 35:
        rec = "SELL"
    else:
        rec = "HOLD"
        
    return score, rec

def fetch_and_calculate(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        df = stock.history(period="6mo")
        
        if df.empty:
            return None
            
        info = stock.info
        company_name = info.get("shortName", ticker)
        
        # Calculate indicators
        df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
        
        macd = ta.trend.MACD(close=df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        
        psar = ta.trend.PSARIndicator(high=df['High'], low=df['Low'], close=df['Close'])
        df['PSAR'] = psar.psar()
        
        bb = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
        df['BB_High'] = bb.bollinger_hband()
        df['BB_Low'] = bb.bollinger_lband()
        
        latest = df.iloc[-1]
        prev = df.iloc[-2] if len(df) > 1 else latest
        
        current_price = latest['Close']
        prev_close = prev['Close']
        change_pct = ((current_price - prev_close) / prev_close) * 100
        
        volume = latest['Volume']
        
        high_52w = info.get("fiftyTwoWeekHigh", df['High'].max())
        low_52w = info.get("fiftyTwoWeekLow", df['Low'].min())
        
        recent_period = df.tail(20)
        support = recent_period['Low'].min()
        resistance = recent_period['High'].max()
        
        max_price = df['High'].max()
        min_price = df['Low'].min()
        diff = max_price - min_price
        
        fib_levels = {
            "0%": max_price,
            "23.6%": max_price - 0.236 * diff,
            "38.2%": max_price - 0.382 * diff,
            "50%": max_price - 0.5 * diff,
            "61.8%": max_price - 0.618 * diff,
            "100%": min_price
        }
        
        score, rec = calculate_confidence(
            current_price, latest['RSI'], latest['MACD'], latest['MACD_Signal'], 
            latest['PSAR'], latest['BB_Low'], latest['BB_High']
        )
        
        chart_data = []
        for index, row in df.tail(100).iterrows():
            chart_data.append({
                "time": index.strftime('%Y-%m-%d'),
                "value": row['Close']
            })
            
        return {
            "Ticker": ticker,
            "Company": company_name,
            "Price": round(current_price, 2),
            "ChangePct": round(change_pct, 2),
            "Volume": int(volume),
            "RSI": round(latest['RSI'], 2) if not pd.isna(latest['RSI']) else 50,
            "MACD": "Bullish" if latest['MACD'] > latest['MACD_Signal'] else "Bearish",
            "PSAR": round(latest['PSAR'], 2) if not pd.isna(latest['PSAR']) else 0,
            "Bollinger": "Upper" if current_price > latest['BB_High'] else ("Lower" if current_price < latest['BB_Low'] else "Inside"),
            "BB_High": round(latest['BB_High'], 2) if not pd.isna(latest['BB_High']) else 0,
            "BB_Low": round(latest['BB_Low'], 2) if not pd.isna(latest['BB_Low']) else 0,
            "52W_High": round(high_52w, 2),
            "52W_Low": round(low_52w, 2),
            "Support": round(support, 2),
            "Resistance": round(resistance, 2),
            "Recommendation": rec,
            "Confidence": score,
            "Fibonacci": {k: round(v, 2) for k, v in fib_levels.items()},
            "ChartData": chart_data,
            "LastUpdated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"Failed to fetch {ticker}: {e}")
        return None
