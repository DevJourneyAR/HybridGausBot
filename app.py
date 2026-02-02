import streamlit as st
import pandas as pd
import numpy as np
import requests
import time
from web3 import Web3

# --- Page Config ---
st.set_page_config(page_title="Hybrid Network Radar", layout="wide", page_icon="🛡️")

# Styling
st.markdown("""<style> .main { background-color: #0e1117; } </style>""", unsafe_allow_html=True)
st.title("🛡️ Hybrid Network Statistical Radar")
st.caption("Monitoring Real-Time Blockchain Data via Official Hybrid RPC")
st.markdown("---")

# --- Hybrid Network Connection Logic ---
# Official Mainnet and Testnet fallbacks
RPC_NODES = [
    "https://rpc.hybrid.network",
    "https://rpc.testnet.hybrid.network",
    "https://rpc-testnet.hybrid.network"
]

def connect_to_hybrid():
    for node in RPC_NODES:
        try:
            w3 = Web3(Web3.HTTPProvider(node))
            if w3.is_connected():
                return w3, node
        except:
            continue
    return None, None

w3, active_node = connect_to_hybrid()

# --- Sidebar ---
with st.sidebar:
    st.header("⚙️ System Configuration")
    if w3:
        st.success(f"Connected to Hybrid\nNode: {active_node}")
    else:
        st.error("❌ Link Broken: Not Connected to Hybrid")
        if st.button("Retry Connection"):
            st.rerun()
    
    st.divider()
    tg_token = st.text_input("Telegram Bot Token", type="password")
    tg_chat_id = st.text_input("Your Chat ID", value="70697336")
    
    st.divider()
    sensitivity = st.slider("Z-Score Sensitivity", 1.5, 4.0, 2.0)
    st.info("High sensitivity (low number) triggers more alerts.")

# --- Analytics Engine ---
def get_live_data():
    if w3:
        try:
            # Monitoring block height as the primary live metric
            return float(w3.eth.block_number)
        except:
            return None
    return None

def compute_z_score(data_list):
    if len(data_list) < 15: return 0
    series = pd.Series(data_list)
    std = series.std()
    return (series.iloc[-1] - series.mean()) / std if std != 0 else 0

# --- Dashboard Layout ---
col_main, col_stats = st.columns([3, 1])
chart_area = col_main.empty()
stats_area = col_stats.empty()

# --- Main Logic ---
if st.button("🚀 Start Hybrid Monitoring"):
    if not tg_token or not tg_chat_id:
        st.error("Please enter Telegram Token first.")
    elif not w3:
        st.error("Cannot start: No connection to Hybrid Network.")
    else:
        st.success("Radar Active. Tracking Hybrid Blocks...")
        history = []
        
        # Send Start Message
        try:
            requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", 
                          json={"chat_id": tg_chat_id, "text": "🛡️ *Hybrid Radar Online*\nSystem connected to RPC."})
        except:
            pass

        while True:
            val = get_live_data()
            if val:
                history.append(val)
                if len(history) > 50: history.pop(0)
                
                z = compute_z_score(history)
                
                # Update Visuals
                chart_area.line_chart(history)
                with stats_area.container():
                    st.metric("Latest Block", int(val))
                    st.metric("Z-Score", f"{z:.2f}")
                
                # Alert Logic
                if len(history) >= 15 and abs(z) > sensitivity:
                    alert_msg = f"⚠️ *Hybrid Deviation Alert*\nZ-Score: {z:.2f}\nBlock: {int(val)}"
                    requests.post(f"https://api.telegram.org/bot{tg_token}/sendMessage", 
                                  json={"chat_id": tg_chat_id, "text": alert_msg})
            
            time.sleep(3)
