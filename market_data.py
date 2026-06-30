import yfinance as yf
import pandas as pd
import streamlit as st

TICKER_MAP = {
    "IHSG": "^JKSE",
    "BBRI": "BBRI.JK",
    "TLKM": "TLKM.JK",
    "GOTO": "GOTO.JK",
    "BMRI": "BMRI.JK",
    "BBNI": "BBNI.JK",
    "ASII": "ASII.JK",
    "UNVR": "UNVR.JK"
}

@st.cache_data(ttl=60)  # Cache real-time prices for 60 seconds
def fetch_realtime_price(query):
    """
    Fetch real-time stock price metrics and 5-day historical trend.
    """
    q_upper = query.strip().upper()
    ticker_symbol = TICKER_MAP.get(q_upper, None)
    
    # If not a mapped ticker, try standard query search
    if not ticker_symbol:
        ticker_symbol = f"{q_upper}.JK"
        
    try:
        ticker = yf.Ticker(ticker_symbol)
        
        # Get historical data for the last 5 days (15-min interval for near real-time trend)
        hist = ticker.history(period="5d", interval="15m")
        if hist.empty:
            hist = ticker.history(period="1mo", interval="1d")
            
        # Get basic info / current price
        fast_info = ticker.fast_info
        current_price = fast_info.get("last_price", None)
        prev_close = fast_info.get("previous_close", None)
        
        # Fallback if fast_info last_price is missing
        if current_price is None and not hist.empty:
            current_price = hist['Close'].iloc[-1]
            if len(hist) > 1:
                prev_close = hist['Close'].iloc[-2]
                
        if current_price is None:
            return None
            
        change_val = 0.0
        change_pct = 0.0
        if prev_close:
            change_val = current_price - prev_close
            change_pct = (change_val / prev_close) * 100
            
        return {
            "symbol": ticker_symbol,
            "price": current_price,
            "change_val": change_val,
            "change_pct": change_pct,
            "high": fast_info.get("day_high", current_price),
            "low": fast_info.get("day_low", current_price),
            "volume": fast_info.get("last_volume", 0),
            "history": hist
        }
    except Exception as e:
        print(f"Error fetching yfinance data for {ticker_symbol}: {e}")
        return None
