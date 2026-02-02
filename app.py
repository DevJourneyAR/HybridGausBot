import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from web3 import Web3

# --- Page Configuration ---
st.set_page_config(page_title="Hybrid Network Gaus Radar", layout="wide", page_icon="🛡️")

st.title("🛡️ Hybrid Network Statistical Radar")
st.caption("Monitoring Real-Time Blockchain Data via Hybrid RPC")
st.markdown("---")

# --- Hybrid Network Connection ---
# Official Hybrid Testnet RPC URL
HYBRID_RPC_URL = "https://rpc.testnet.hybrid.network" 
w3 = Web3(Web3.HTTPProvider(HYBRID_RPC_URL))

def get_hybrid_data():
    try:
        if w3.is_connected():
            # Monitoring the latest block number as a proxy for network pulse
            block = w3.eth.block_number
            return float(block)
        return None
    except Exception as e:
        return None

# --- Sidebar Configuration ---
with st.sidebar:
    st.header("⚙️ Hybrid Settings")
    if w3.is_connected():
        st.success("Connected to Hybrid Network")
    else:
        st.error("Not Connected to Hybrid")
    
    st.divider()
    token = st.text_input("Telegram Bot Token", type="password")
    chat_id = st.text_input("Telegram Chat ID")
    
    st.divider()
    threshold = st.slider("Z-Score Sensitivity", 1.5, 4.0, 2.0)

# --- Statistical Engine ---
def calculate_z_score(data_list):
    if len(data_list) < 10: return 0
    series = pd.Series(data_list)
    z_score = (series.iloc[-1] - series.mean()) / series.std() if series.std() != 0 else 0
    return z_score

# --- Dashboard Layout ---
col1, col2 = st.columns([3, 1])
chart_place = col1.empty()
metric_place = col2.empty()

# --- Execution Engine ---
if st.button("🚀 Start Hybrid Monitoring"):
    if not token or not chat_id:
        st.error("❌ Please enter Telegram credentials.")
    else:
        st.success("Hybrid Radar Online. Analyzing Blocks...")
        data_history = []
        
        while True:
            current_val = get_hybrid_data()
            if current_val:
                data_history.append(current_val)
                if len(data_history) > 50: data_history.pop(0)
                
                z = calculate_z_score(data_history)
                
                # Update Visuals
                chart_place.line_chart(data_history)
                with metric_place.container():
                    st.metric("Latest Hybrid Block", int(current_val))
                    st.metric("Z-Score Deviation", f"{z:.2f}")

                # Alerting Logic
                if len(data_history) >= 10 and abs(z) > threshold:
                    msg = f"⚠️ **Hybrid Network Alert**\nStatistical Deviation detected!\nZ-Score: {z:.2f}\nBlock: {int(current_val)}"
                    requests.post(f"https://api.telegram.org/bot{token}/sendMessage", 
                                  json={"chat_id": chat_id, "text": msg})
            
            time.sleep(2) # Refresh every 2 seconds for Hybrid blocks
