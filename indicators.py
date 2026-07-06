import yfinance as yf
import pandas as pd
import ta
import numpy as np
from datetime import datetime

def calculate_confidence(price, rsi, macd, macd_signal, psar, ema200, bollinger_l, bollinger_h, adx, current_close, prev_close, volume_ratio):
    score = 0
    breakdown = {}
    
    # RSI (10%)
    if not pd.isna(rsi):
        if rsi < 30: pts = 10
        elif rsi > 70: pts = 0
        else: pts = 5
        score += pts
        breakdown['RSI'] = pts
        
    # MACD (25%)
    pts = 0
    if not pd.isna(macd) and not pd.isna(macd_signal):
        if macd > macd_signal: pts = 25
    score += pts
    breakdown['MACD'] = pts
        
    # PSAR (5%)
    pts = 0
    if not pd.isna(psar):
        if price > psar: pts = 5
    score += pts
    breakdown['PSAR'] = pts
        
    # EMA 200 (20%)
    pts = 0
    if not pd.isna(ema200):
        if price > ema200: pts = 20
    score += pts
    breakdown['EMA'] = pts
        
    # ADX (10%)
    pts = 0
    if not pd.isna(adx):
        if adx > 25 and (not pd.isna(ema200) and price > ema200):
            pts = 10
        elif adx < 25:
            pts = 5
    score += pts
    breakdown['ADX'] = pts
        
    # Bollinger (15%)
    pts = 0
    if not pd.isna(bollinger_l) and not pd.isna(bollinger_h):
        if price < bollinger_l: pts = 15
        elif price > bollinger_h: pts = 0
        else: pts = 7
    score += pts
    breakdown['Bollinger'] = pts
        
    # Volume (15%) - User Logic
    pts = 0
    if not pd.isna(volume_ratio):
        if current_close > prev_close and volume_ratio > 1.5:
            pts = 15
        elif current_close < prev_close and volume_ratio > 1.5:
            pts = -15
        elif volume_ratio < 0.8:
            pts = -5
    score += pts
    breakdown['Volume'] = pts
            
    score = max(0, min(100, score)) # Clamp 0-100
    
    if score >= 65: rec = "BUY"
    elif score <= 35: rec = "SELL"
    else: rec = "HOLD"
        
    return score, rec, breakdown

def fetch_and_calculate(ticker: str):
    try:
        stock = yf.Ticker(ticker)
        # Fetch 1y to have enough data for EMA 200
        df = stock.history(period="1y")
        
        if df.empty or len(df) < 20:
            return None
            
        df = df.dropna(subset=['Close'])
            
        info = stock.info if hasattr(stock, 'info') else {}
        company_name = info.get("shortName", ticker)
        
        # Calculate indicators
        df['RSI'] = ta.momentum.RSIIndicator(close=df['Close'], window=14).rsi()
        
        macd = ta.trend.MACD(close=df['Close'])
        df['MACD'] = macd.macd()
        df['MACD_Signal'] = macd.macd_signal()
        
        psar = ta.trend.PSARIndicator(high=df['High'], low=df['Low'], close=df['Close'])
        df['PSAR'] = psar.psar()
        
        df['EMA_200'] = ta.trend.EMAIndicator(close=df['Close'], window=200).ema_indicator()
        
        adx_ind = ta.trend.ADXIndicator(high=df['High'], low=df['Low'], close=df['Close'], window=14)
        df['ADX'] = adx_ind.adx()
        
        bb = ta.volatility.BollingerBands(close=df['Close'], window=20, window_dev=2)
        df['BB_High'] = bb.bollinger_hband()
        df['BB_Low'] = bb.bollinger_lband()
        
        df = df.ffill()
        
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        current_price = latest['Close']
        prev_close = prev['Close']
        change_pct = ((current_price - prev_close) / prev_close) * 100
        
        volume = latest['Volume']
        
        avg_volume = df["Volume"].rolling(20).mean().iloc[-1]
        today_volume = volume
        volume_ratio = today_volume / avg_volume if avg_volume else 1
        
        high_52w = info.get("fiftyTwoWeekHigh", df['High'].max())
        low_52w = info.get("fiftyTwoWeekLow", df['Low'].min())
        
        recent_period = df.tail(20)
        support = recent_period['Low'].min()
        resistance = recent_period['High'].max()
        
        max_price = df['High'].tail(130).max()
        min_price = df['Low'].tail(130).min()
        diff = max_price - min_price
        
        fib_levels = {
            "0%": max_price,
            "23.6%": max_price - 0.236 * diff,
            "38.2%": max_price - 0.382 * diff,
            "50%": max_price - 0.5 * diff,
            "61.8%": max_price - 0.618 * diff,
            "100%": min_price
        }
        
        score, rec, breakdown = calculate_confidence(
            current_price, latest['RSI'], latest['MACD'], latest['MACD_Signal'], 
            latest['PSAR'], latest['EMA_200'], latest['BB_Low'], latest['BB_High'], 
            latest['ADX'], current_price, prev_close, volume_ratio
        )
        
        return {
            "Ticker": ticker,
            "Company": company_name,
            "Price": round(current_price, 2),
            "ChangePct": round(change_pct, 2),
            "Volume": int(volume),
            "VolumeRatio": round(volume_ratio, 2),
            "RSI": round(latest['RSI'], 2) if not pd.isna(latest['RSI']) else 50,
            "MACD": "Bullish" if latest['MACD'] > latest['MACD_Signal'] else "Bearish",
            "MACD_Val": round(latest['MACD'], 2) if not pd.isna(latest['MACD']) else 0,
            "MACD_Sig": round(latest['MACD_Signal'], 2) if not pd.isna(latest['MACD_Signal']) else 0,
            "PSAR": round(latest['PSAR'], 2) if not pd.isna(latest['PSAR']) else 0,
            "EMA_200": round(latest['EMA_200'], 2) if not pd.isna(latest['EMA_200']) else 0,
            "ADX": round(latest['ADX'], 2) if not pd.isna(latest['ADX']) else 0,
            "Bollinger": "Upper" if current_price > latest['BB_High'] else ("Lower" if current_price < latest['BB_Low'] else "Inside"),
            "BB_High": round(latest['BB_High'], 2) if not pd.isna(latest['BB_High']) else 0,
            "BB_Low": round(latest['BB_Low'], 2) if not pd.isna(latest['BB_Low']) else 0,
            "52W_High": round(high_52w, 2),
            "52W_Low": round(low_52w, 2),
            "Recommendation": rec,
            "Confidence": score,
            "Breakdown": breakdown,
            "Fibonacci": {k: round(v, 2) for k, v in fib_levels.items()},
        }
    except Exception as e:
        print(f"Failed to fetch {ticker}: {e}")
        return None
