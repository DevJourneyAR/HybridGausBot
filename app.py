import streamlit as st
import pandas as pd
import numpy as np
import requests
import time

# --- Page Configuration ---
st.set_page_config(page_title="Hybrid Gaus Radar", layout="wide")
st.title("🛡️ Statistical Trading Radar (Real-Time)")
st.markdown("---")

# --- Real-Time Price Fetcher ---
def get_crypto_price(symbol):
    try:
        # Fetching price from Binance Public API
        url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol.upper()}USDT"
        response = requests.get(url, timeout=5)
        data = response.json()
        return float(data['price'])
    except Exception as e:
        return None

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Asset Selection
    coin = st.text_input("Coin Symbol (e.g., BTC, ETH, SOL)", value="BTC").upper()
    
    st.divider()
    
    # Telegram Security Credentials
    token = st.text_input("Telegram Bot Token", type="password")
    chat_id = st.text_input("Your Chat ID")
    
    st.divider()
    
    # Gaussian Sensitivity (Z-Score Threshold)
    threshold = st.slider("Sensitivity (Z-Score Threshold)", 1.5, 3.5, 2.0)
    st.write("Higher threshold means fewer but more accurate alerts.")

# --- Statistical Engine ---
def calculate_z_score(price_list):
    if len(price_list) < 20: 
        return 0
    df = pd.DataFrame(price_list, columns=['price'])
    mean = df['price'].mean()
    std = df['price'].std()
    # Z-Score formula: (Current Price - Mean) / Standard Deviation
    z_score = (df['price'].iloc[-1] - mean) / std if std != 0 else 0
    return z_score

# --- Main Dashboard Layout ---
col1, col2 = st.columns([3, 1])
chart_place = col1.empty()
metric_place = col2.empty()

# --- Execution Engine ---
if st.button(f"Start Monitoring {coin}/USDT"):
    if not token or not chat_id:
        st.error("⚠️ Error: Please provide Telegram credentials in the sidebar.")
    else:
        st.success(f"System is now monitoring {coin}/USDT in real-time.")
        
        # Initialization
        price_history = []
        
        # Send Start Notification to Telegram
        welcome_msg = f"🚀 *Hybrid Gaus Bot Started*\nAsset: {coin}/USDT\nThreshold: {threshold}"
        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                      json={"chat_id": chat_id, "text": welcome_msg, "parse_mode": "Markdown"})

        # Live Monitoring Loop
        while True:
            current_p = get_crypto_price(coin)
            
            if current_p:
                price_history.append(current_p)
                
                # Maintain buffer size (keep last 100 data points)
                if len(price_history) > 100:
                    price_history.pop(0)
                
                # Calculate statistical deviation
                z = calculate_z_score(price_history)
                
                # Update Chart
                with chart_place.container():
                    st.line_chart(price_history)
                
                # Update Metrics
                with metric_place.container():
                    st.metric("Current Price", f"${current_p:,.2f}")
                    st.metric("Z-Score (Deviation)", f"{z:.2f}")
                
                # Alert Logic
                if len(price_history) >= 20:
                    if z < -threshold:
                        alert_msg = f"🟢 **BUY SIGNAL**: {coin} is Oversold! (Z-Score: {z:.2f})"
                        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                                      json={"chat_id": chat_id, "text": alert_msg, "parse_mode": "Markdown"})
                        st.toast(alert_msg)
                        
                    elif z > threshold:
                        alert_msg = f"🔴 **SELL SIGNAL**: {coin} is Overbought! (Z-Score: {z:.2f})"
                        requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                                      json={"chat_id": chat_id, "text": alert_msg, "parse_mode": "Markdown"})
                        st.toast(alert_msg)
            
            else:
                st.warning("Connection lost. Retrying to fetch price...")
            
            time.sleep(5) # 5-second interval
