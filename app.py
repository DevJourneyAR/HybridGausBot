import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from web3 import Web3

# --- Page Configuration ---
st.set_page_config(page_title="Hybrid Network Gaus Radar", layout="wide", page_icon="🛡️")

st.title("🛡️ Hybrid Network Statistical Radar")
st.caption("Monitoring Hybrid Network Blocks & Prices via RPC")
st.markdown("---")

# --- Hybrid Network Connection ---
# Use the official Hybrid RPC URL
HYBRID_RPC_URL = "https://rpc.hybrid.network"
w3 = Web3(Web3.HTTPProvider(HYBRID_RPC_URL))

def get_hybrid_data():
    try:
        if w3.is_connected():
            # In a real scenario, we fetch the latest block or a specific pair price
            # For now, we will monitor the Latest Block Number as a proxy for activity
            block = w3.eth.block_number
            return float(block)
        return None
    except:
        return None

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Hybrid Settings")
    st.info("Connected to: Hybrid Mainnet")
    
    st.divider()
    token = st.text_input("Telegram Bot Token", type="password")
    chat_id = st.text_input("Telegram Chat ID")
    
    st.divider()
    threshold = st.slider("Z-Score Sensitivity", 1.5, 4.0, 2.0)

# --- Statistical Engine ---
def calculate_z_score(data_list):
    if len(data_list) < 20: return 0
    series = pd.Series(data_list)
    z_score = (series.iloc[-1] - series.mean()) / series.std() if series.std() != 0 else 0
    return z_score

# --- Dashboard ---
col1, col2 = st.columns([3, 1])
chart_place = col1.empty()
metric_place = col2.empty()

if st.button("🚀 Start Hybrid Monitoring"):
    if not token or not chat_id:
        st.error("❌ Please enter Telegram credentials.")
    else:
        st.success("Connected to Hybrid Network. Analyzing Blocks...")
        data_history = []
        
        while True:
            current_val = get_hybrid_data()
            if current_val:
                data_history.append(current_val)
                if len(data_history) > 60: data_history.pop(0)
                
                z = calculate_z_score(data_history)
                
                chart_place.line_chart(data_history)
                with metric_place.container():
                    st.metric("Latest Hybrid Block", int(current_val))
                    st.metric("Z-Score Deviation", f"{z:.2f}")

                # Alerting Logic
                if len(data_history) >= 20 and abs(z) > threshold:
                    msg = f"⚠️ **Hybrid Network Alert**\nSignificant Statistical Deviation detected!\nZ-Score: {z:.2f}"
                    requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                                  json={"chat_id": chat_id, "text": msg})
            
            time.sleep(3) # Hybrid block time is fast
